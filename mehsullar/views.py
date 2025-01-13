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
    
    # Cari məzənnəni al
    eur_rate = get_eur_rate()
    update_time = cache.get('eur_update_time', 'Məlumat yoxdur')

    # Hər məhsul üçün stok məlumatını və cəmi məbləği əlavə et
    total_eur = 0
    total_azn = 0
    
    for item in sebet:
        item.stok_status = get_stock_status(item.mehsul.stok)
        item.stok_class = get_stock_class(item.mehsul.stok)
        item.cemi_eur = item.mehsul.qiymet_eur * item.miqdar  # EUR cəmi
        item.cemi_azn = item.mehsul.qiymet_azn * item.miqdar  # AZN cəmi
        
        total_eur += item.cemi_eur
        total_azn += item.cemi_azn

    return render(request, 'cart.html', {
        'sebet': sebet,
        'cemi_mebleg_eur': total_eur,
        'cemi_mebleg_azn': total_azn,
        'eur_rate': eur_rate,
        'update_time': update_time
    })

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
        cached_rate = cache.get('eur_mezenne')
        if cached_rate:
            return cached_rate

        url = "https://open.er-api.com/v6/latest/EUR"
        with urlopen(url) as response:
            data = json.loads(response.read())
            rate = Decimal(str(data['rates']['AZN']))
            
            # Əvvəlki məzənnəni saxla
            old_rate = cache.get('evvelki_mezenne')
            if old_rate != rate:
                cache.set('evvelki_mezenne', old_rate)
            
            cache.set('eur_mezenne', rate, 600)
            cache.set('eur_update_time', datetime.now().strftime('%H:%M'), 600)
            return rate

    except Exception as e:
        print(f"Məzənnə yeniləmə xətası: {e}")
        return Decimal('2.00')

@login_required
def products_list(request):
    # Mövcud kodu saxlayırıq
    mehsullar = Mehsul.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    brendlər = Brend.objects.all()
    markalar = Marka.objects.all()
    
    # Məzənnəni yeniləyirik
    eur_rate = get_eur_rate()
    update_time = cache.get('eur_update_time', 'Məlumat yoxdur')
    
    # Axtarış parametrlərini alırıq
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    search_text = request.GET.get('search_text')

    # Brend, kateqoriya və marka üçün dəqiq filtrasiya
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)

    # Brend kodu və OEM kodu üçün hissəvi axtarış
    if search_text:
        # Xüsusi simvolları təmizləyirik
        search_text = re.sub(r'[^a-zA-Z0-9]', '', search_text)
        # Brend kodu və ya OEM koduna görə hissəvi axtarış
        mehsullar = mehsullar.filter(
            Q(brend_kod__icontains=search_text) |  # Hissəvi uyğunluq
            Q(oem__icontains=search_text) |        # Hissəvi uyğunluq
            Q(oem_kodlar__kod__icontains=search_text)  # Əlavə OEM kodlarında hissəvi uyğunluq
        ).distinct()

    return render(request, 'products_list.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendlər': brendlər,
        'markalar': markalar,
        'eur_rate': eur_rate,
        'update_time': update_time
    })


@login_required
def sebetden_sil(request, sebet_id):
    if request.method == 'POST':
        try:
            sebet_item = get_object_or_404(Sebet, id=sebet_id, user=request.user)
            sebet_item.delete()
            
            # Cari məzənnəni al
            eur_rate = get_eur_rate()  # Bu Decimal qaytarır
            
            # Yeni ümumi məbləği hesabla
            cart_total_eur = Sebet.objects.filter(user=request.user).aggregate(
                total_eur=Sum(F('miqdar') * F('mehsul__qiymet_eur'))
            )['total_eur'] or Decimal('0')
            
            cart_total_azn = cart_total_eur * eur_rate
            
            return JsonResponse({
                'success': True,
                'total_amount_eur': str(round(cart_total_eur, 2)),
                'total_amount_azn': str(round(cart_total_azn, 2))
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

            # Cari məzənnəni al və saxla
            current_rate = get_eur_rate()

            # Ümumi məbləği EUR-da hesabla
            total_eur = sum(item.mehsul.qiymet_eur * item.miqdar for item in sebet_items)

            # Yeni sifarişi yarat
            sifaris = Sifaris.objects.create(
                user=request.user,
                cemi_mebleg_eur=total_eur,
                odenilen_mebleg_eur=0,
                sifaris_mezennesi=current_rate,  # Məzənnəni saxla
                status='gozleyir'
            )

            # Sifariş məhsullarını əlavə et
            for item in sebet_items:
                SifarisMehsul.objects.create(
                    sifaris=sifaris,
                    mehsul=item.mehsul,
                    miqdar=item.miqdar,
                    qiymet=item.mehsul.qiymet_eur  # EUR qiyməti
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
    sifarisler = Sifaris.objects.filter(user=request.user)

    # Cari məzənnəni al
    eur_rate = get_eur_rate()
    update_time = cache.get('eur_update_time', 'Məlumat yoxdur')

    # Ümumi məbləğləri hesabla
    toplam_mebleg_eur = sum(sifaris.cemi_mebleg_eur for sifaris in sifarisler)
    odenilen_mebleg_eur = sum(sifaris.odenilen_mebleg_eur for sifaris in sifarisler)
    
    # AZN məbləğləri
    toplam_mebleg_azn = toplam_mebleg_eur * eur_rate
    odenilen_mebleg_azn = odenilen_mebleg_eur * eur_rate

    # Qalıq borcları hesabla
    qaliq_borc_eur = toplam_mebleg_eur - odenilen_mebleg_eur
    qaliq_borc_azn = qaliq_borc_eur * eur_rate

    status_text = {
        'gozleyir': 'Gözləyir',
        'hazirlanir': 'Hazırlanır',
        'yoldadir': 'Yoldadır',
        'catdirildi': 'Çatdırıldı'
    }

    for sifaris in sifarisler:
        sifaris.display_status = status_text.get(sifaris.status, 'Gözləyir')

    return render(request, 'sifaris_izleme.html', {
        'sifarisler': sifarisler,
        'toplam_mebleg_eur': round(toplam_mebleg_eur, 2),
        'toplam_mebleg_azn': round(toplam_mebleg_azn, 2),
        'odenilen_mebleg_eur': round(odenilen_mebleg_eur, 2),
        'odenilen_mebleg_azn': round(odenilen_mebleg_azn, 2),
        'qaliq_borc_eur': round(qaliq_borc_eur, 2),
        'qaliq_borc_azn': round(qaliq_borc_azn, 2),
        'eur_rate': eur_rate,
        'update_time': update_time
    })


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
        eur_rate = get_eur_rate()  # Bu Decimal qaytarır

        # Yeni məbləğləri hesabla - hər şeyi Decimal-a çeviririk
        item_total_eur = Decimal(str(cart_item.mehsul.qiymet_eur)) * Decimal(str(new_quantity))
        item_total_azn = item_total_eur * eur_rate
        
        # Ümumi səbət məbləğini hesabla
        cart_total_eur = Sebet.objects.filter(user=request.user).aggregate(
            total_eur=Sum(F('miqdar') * F('mehsul__qiymet_eur'))
        )['total_eur'] or Decimal('0')
        
        cart_total_azn = cart_total_eur * eur_rate

        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total_eur': str(round(item_total_eur, 2)),
            'item_total_azn': str(round(item_total_azn, 2)),
            'total_amount_eur': str(round(cart_total_eur, 2)),
            'total_amount_azn': str(round(cart_total_azn, 2))
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
    
    # Cari məzənnəni al
    eur_rate = get_eur_rate()
    update_time = cache.get('eur_update_time', 'Məlumat yoxdur')
    
    # Hər məhsul üçün EUR və AZN qiymətlərini hesabla
    for mehsul in sifaris_mehsullari:
        mehsul.qiymet_eur = mehsul.qiymet
        mehsul.qiymet_azn = mehsul.qiymet * eur_rate
        mehsul.cemi_eur = mehsul.qiymet * mehsul.miqdar
        mehsul.cemi_azn = mehsul.cemi_eur * eur_rate
    
    # Artıq bu hesablamalara ehtiyac yoxdur, çünki model-də property kimi təyin olunub
    # sifaris.cemi_mebleg_eur və digər sahələr birbaşa modeldən gəlir
    
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
        'eur_rate': eur_rate,
        'update_time': update_time
    }
    return render(request, 'sifaris_detallari.html', context)
