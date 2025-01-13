from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Sebet, Kateqoriya, Brend, Marka, Sifaris, SifarisMehsul, OEMKod, SebetItem
from django.db.models import F, Sum, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import re
from django.contrib.auth.models import User
from django.core.cache import cache
from urllib.request import urlopen
from urllib.error import URLError
from decimal import Decimal
from datetime import datetime

@login_required
def about(request):
    return render(request, 'about.html')



@login_required
def sebet_ekle(request, mehsul_id):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    sebet, created = Sebet.objects.get_or_create(user=request.user, mehsul=mehsul)
    if not created:
        sebet.miqdar += 1
        sebet.save()

    # Yalnız uğurlu əlavə üçün cavab
    return HttpResponse(status=204)
@login_required
def view_cart(request):
    sebet = Sebet.objects.filter(user=request.user)
    current_rate, previous_rate = get_eur_rate()
    rate_change = current_rate - previous_rate

    for item in sebet:
        item.stok_status = get_stock_status(item.mehsul.stok)
        item.stok_class = get_stock_class(item.mehsul.stok)
        item.cemi_eur = item.mehsul.qiymet_eur * item.miqdar
        item.cemi_azn = item.mehsul.qiymet_azn * item.miqdar
        item.previous_price_azn = round(item.mehsul.qiymet_eur * previous_rate, 2)
        item.price_change = round(item.mehsul.qiymet_azn - item.previous_price_azn, 2)
        # Mütləq qiyməti burada hesablayırıq
        item.price_change_percent = abs(round((item.price_change / item.previous_price_azn) * 100, 1))

    context = {
        'sebet': sebet,
        'cemi_mebleg_eur': sum(item.cemi_eur for item in sebet),
        'cemi_mebleg_azn': sum(item.cemi_azn for item in sebet),
        'eur_rate': current_rate,
        'rate_change': rate_change,
        'rate_change_percent': abs(round((rate_change / previous_rate) * 100, 1)),
        'update_time': cache.get('eur_update_time', 'Məlumat yoxdur')
    }
    return render(request, 'cart.html', context)

def get_stock_status(stok):
    if stok == 0:
        return "Yoxdur"
    elif stok <= 20:
        return "Az var"
    else:
        return "Var"

def get_stock_class(stok):
    if stok == 0:
        return "out-of-stock"
    elif stok <= 20:
        return "low-stock"
    else:
        return "in-stock"

def get_eur_rate():
    try:
        # Əvvəlki məzənnəni saxla
        previous_rate = cache.get('previous_eur_mezenne')
        current_rate = cache.get('eur_mezenne')
        
        if current_rate:
            if not previous_rate:
                cache.set('previous_eur_mezenne', current_rate, 43200)
            return current_rate, previous_rate or current_rate

        url = "https://open.er-api.com/v6/latest/EUR"
        with urlopen(url) as response:
            data = json.loads(response.read())
            rate = Decimal(str(data['rates']['AZN']))
            
            if current_rate:
                cache.set('previous_eur_mezenne', current_rate,  43200)
            cache.set('eur_mezenne', rate,  43200)
            cache.set('eur_update_time', datetime.now().strftime('%H:%M'),  43200)
            
            return rate, current_rate or rate

    except Exception as e:
        print(f"Məzənnə yeniləmə xətası: {e}")
        return Decimal('1.746752'), Decimal('1.746752')  # Default məzənnəni yenilədik

@login_required
def products_list(request):
    mehsullar = Mehsul.objects.all()
    current_rate, previous_rate = get_eur_rate()
    rate_change = current_rate - previous_rate
    
    for mehsul in mehsullar:
        mehsul.previous_price_azn = round(mehsul.qiymet_eur * previous_rate, 2)
        mehsul.price_change = round(mehsul.qiymet_azn - mehsul.previous_price_azn, 2)
        # Mütləq qiyməti burada hesablayırıq
        mehsul.price_change_percent = abs(round((mehsul.price_change / mehsul.previous_price_azn) * 100, 1))

    context = {
        'mehsullar': mehsullar,
        'eur_rate': current_rate,
        'previous_rate': previous_rate,
        'rate_change': rate_change,
        'rate_change_percent': abs(round((rate_change / previous_rate) * 100, 1)),
        'update_time': cache.get('eur_update_time', 'Məlumat yoxdur')
    }
    return render(request, 'products_list.html', context)


@login_required
def sebetden_sil(request, sebet_id):
    if request.method == 'POST':
        try:
            sebet_item = get_object_or_404(Sebet, id=sebet_id, user=request.user)
            sebet_item.delete()
            
            # Cari məzənnəni al
            current_rate, _ = get_eur_rate()
            
            # Yeni ümumi məbləği hesabla
            sebet_items = Sebet.objects.filter(user=request.user)
            total_eur = sum(item.mehsul.qiymet_eur * item.miqdar for item in sebet_items)
            total_azn = total_eur * current_rate
        
            return JsonResponse({
                'success': True,
                'total_amount_eur': str(round(total_eur, 2)),
                'total_amount_azn': str(round(total_azn, 2))
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu'
    }, status=400)

@login_required
def sifarisi_gonder(request):
    if request.method == 'POST':
        try:
            sebet_items = Sebet.objects.filter(user=request.user)
            if not sebet_items:
                return JsonResponse({'status': 'error', 'message': 'Səbətiniz boşdur'})

            # Cari məzənnəni al
            current_rate, _ = get_eur_rate()
            
            # Ümumi məbləği EUR-da hesabla
            total_eur = sum(item.mehsul.qiymet_eur * item.miqdar for item in sebet_items)

            # Yeni sifarişi yarat və cari məzənnəni dəqiq olaraq saxla
            sifaris = Sifaris.objects.create(
                user=request.user,
                cemi_mebleg_eur=total_eur,
                odenilen_mebleg_eur=0,
                sifaris_mezennesi=float(current_rate),  # Cari məzənnəni float olaraq saxla
                status='gozleyir'
            )

            # Sifariş məhsullarını əlavə et
            for item in sebet_items:
                SifarisMehsul.objects.create(
                    sifaris=sifaris,
                    mehsul=item.mehsul,
                    miqdar=item.miqdar,
                    qiymet=float(item.mehsul.qiymet_eur)  # Qiyməti float olaraq saxla
                )

                # Stoku yenilə
                mehsul = item.mehsul
                mehsul.stok = F('stok') - item.miqdar
                mehsul.save()

            # Səbəti təmizlə
            sebet_items.delete()

            return JsonResponse({
                'status': 'success',
                'message': 'Sifariş uğurla yaradıldı',
                'sifaris_id': sifaris.id
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })

    return JsonResponse({'status': 'error', 'message': 'Yanlış sorğu metodu'})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sifaris

@login_required
def sifaris_izle(request):
    sifarisler = Sifaris.objects.filter(user=request.user).order_by('-tarix')
    
    # Ümumi statistika hesablamaları
    toplam_mebleg_eur = round(sum(sifaris.cemi_mebleg_eur for sifaris in sifarisler), 2)
    toplam_mebleg_azn = round(sum(sifaris.cemi_mebleg_azn for sifaris in sifarisler), 2)
    toplam_odenilen_eur = round(sum(sifaris.odenilen_mebleg_eur for sifaris in sifarisler), 2)
    toplam_odenilen_azn = round(sum(sifaris.odenilen_mebleg_azn for sifaris in sifarisler), 2)
    toplam_qaliq_eur = round(toplam_mebleg_eur - toplam_odenilen_eur, 2)
    toplam_qaliq_azn = round(toplam_mebleg_azn - toplam_odenilen_azn, 2)

    # Status mətnlərini əlavə et
    status_text = {
        'gozleyir': 'Gözləyir',
        'hazirlanir': 'Hazırlanır',
        'yoldadir': 'Yoldadır',
        'catdirildi': 'Çatdırıldı'
    }

    for sifaris in sifarisler:
        sifaris.display_status = status_text.get(sifaris.status, 'Gözləyir')

    context = {
        'sifarisler': sifarisler,
        'toplam_mebleg_eur': toplam_mebleg_eur,
        'toplam_mebleg_azn': toplam_mebleg_azn,
        'toplam_odenilen_eur': toplam_odenilen_eur,
        'toplam_odenilen_azn': toplam_odenilen_azn,
        'toplam_qaliq_eur': toplam_qaliq_eur,
        'toplam_qaliq_azn': toplam_qaliq_azn,
    }
    return render(request, 'sifaris_izleme.html', context)


@login_required
def get_cart_count(request):
    try:
        count = Sebet.objects.filter(user=request.user).aggregate(
            total_items=Sum('miqdar')
        )['total_items'] or 0
        return JsonResponse({'count': count})
    except:
        return JsonResponse({'count': 0})



@login_required
def update_quantity(request, item_id, new_quantity):
    try:
        cart_item = get_object_or_404(Sebet, id=item_id, user=request.user)
        
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 1:
                new_quantity = 1
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Düzgün miqdar daxil edin.'
            }, status=400)

        cart_item.miqdar = new_quantity
        cart_item.save()

        # Cari məzənnəni al
        current_rate, _ = get_eur_rate()

        # Yeni məbləğləri hesabla
        item_total_eur = float(cart_item.mehsul.qiymet_eur) * new_quantity
        item_total_azn = item_total_eur * float(current_rate)
        
        # Ümumi səbət məbləğini hesabla
        sebet_items = Sebet.objects.filter(user=request.user)
        cart_total_eur = sum(float(item.mehsul.qiymet_eur) * item.miqdar for item in sebet_items)
        cart_total_azn = cart_total_eur * float(current_rate)

        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total_eur': f"{item_total_eur:.2f}",
            'item_total_azn': f"{item_total_azn:.2f}",
            'total_amount_eur': f"{cart_total_eur:.2f}",
            'total_amount_azn': f"{cart_total_azn:.2f}"
        })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def mehsul_axtaris(request):
    query = request.GET.get('q')
    if query:
        # Həm əsas OEM kodunda, həm də əlavə OEM kodlarında axtarış et
        mehsullar = Mehsul.objects.filter(
            Q(oem__icontains=query) |  # əsas OEM kodunda axtar
            Q(oem_kodlar__kod__icontains=query)  # əlavə OEM kodlarında axtar
        ).distinct()
        # qalan kod...


@login_required
def sifaris_detallari(request, sifaris_id):
    sifaris = get_object_or_404(Sifaris, id=sifaris_id, user=request.user)
    sifaris_mehsullari = SifarisMehsul.objects.filter(sifaris=sifaris)
    
    # Hər məhsul üçün EUR və AZN qiymətlərini hesabla
    for mehsul in sifaris_mehsullari:
        mehsul.qiymet_eur = mehsul.qiymet  # Saxlanmış EUR qiyməti
        mehsul.qiymet_azn = mehsul.qiymet * sifaris.sifaris_mezennesi  # Sifariş məzənnəsi ilə hesabla
        mehsul.cemi_eur = mehsul.qiymet * mehsul.miqdar
        mehsul.cemi_azn = mehsul.cemi_eur * sifaris.sifaris_mezennesi  # Sifariş məzənnəsi ilə hesabla
    
    status_text = {
        'gozleyir': 'Gözləyir',
        'hazirlanir': 'Hazırlanır',
        'yoldadir': 'Yoldadır',
        'catdirildi': 'Çatdırıldı'
    }
    sifaris.display_status = status_text.get(sifaris.status, 'Gözləyir')
    
    context = {
        'sifaris': sifaris,
        'sifaris_mehsullari': sifaris_mehsullari,
    }
    return render(request, 'sifaris_detallari.html', context)
