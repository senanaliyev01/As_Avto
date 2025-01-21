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
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
from django.utils import timezone
import io

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
    cemi_mebleg = sebet.aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0

    # Hər məhsul üçün stok məlumatını və cəmi məbləği əlavə et
    for item in sebet:
        item.stok_status = get_stock_status(item.mehsul.stok)
        item.stok_class = get_stock_class(item.mehsul.stok)
        item.cemi = item.mehsul.qiymet * item.miqdar  # Hər məhsul üçün cəmi məbləğ

    return render(request, 'cart.html', {
        'sebet': sebet,
        'cemi_mebleg': cemi_mebleg
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

@login_required
def products_list(request):
    # Başlanğıc olaraq bütün məhsulları götürürük
    mehsullar = Mehsul.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()

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
        'brendler': brendler,
        'markalar': markalar
    })


@login_required
def sebetden_sil(request, sebet_id):
    try:
        sebet_item = Sebet.objects.get(id=sebet_id, user=request.user)
        sebet_item.delete()
        
        # Yeni cəmi məbləği hesabla
        sebet = Sebet.objects.filter(user=request.user)
        cemi_mebleg = sebet.aggregate(
            total=Sum(F('miqdar') * F('mehsul__qiymet'))
        )['total'] or 0
        
        # Float-a çevir və yuvarlaqlaşdır
        cemi_mebleg = round(float(cemi_mebleg), 2)
        
        return JsonResponse({
            'success': True,
            'cemi_mebleg': cemi_mebleg
        })
    except Sebet.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Məhsul tapılmadı'
        }, status=404)

@login_required
def sifarisi_gonder(request):
    if request.method == "POST":
        try:
            # Səbətdəki məhsulları yoxla
            sebet = Sebet.objects.filter(user=request.user)
            if not sebet.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Səbətiniz boşdur'
                }, status=400)

            # Yeni sifarişi yarat
            sifaris = Sifaris.objects.create(
                user=request.user,
                cemi_mebleg=0
            )

            total_amount = 0
            # Məhsulları sifarişə əlavə et
            for item in sebet:
                item_total = item.mehsul.qiymet * item.miqdar
                total_amount += item_total
                
                SifarisMehsul.objects.create(
                    sifaris=sifaris,
                    mehsul=item.mehsul,
                    miqdar=item.miqdar,
                    qiymet=item.mehsul.qiymet
                )

            # Ümumi məbləği yenilə və sifarişi tamamla
            sifaris.cemi_mebleg = total_amount
            sifaris.status = 'gozleyir'
            sifaris.save()

            # Səbəti təmizlə
            sebet.delete()

            return JsonResponse({
                'success': True,
                'message': 'Sifarişiniz uğurla qeydə alındı'
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Xəta baş verdi: ' + str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu'
    }, status=400)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sifaris

@login_required
def sifaris_izle(request):
    sifarisler = Sifaris.objects.filter(user=request.user)

    toplam_mebleg = sum(sifaris.cemi_mebleg for sifaris in sifarisler)
    odenilen_mebleg = sum(sifaris.odenilen_mebleg for sifaris in sifarisler)
    qaliq_borc = toplam_mebleg - odenilen_mebleg

    status_text = {
        'gozleyir': 'Gözləyir',
        'hazirlanir': 'Hazırlanır',
        'yoldadir': 'Yoldadır',
        'catdirildi': 'Çatdırıldı'
    }

    # Hər sifarişə status əlavə edirik
    for sifaris in sifarisler:
        sifaris.display_status = status_text.get(sifaris.status, 'Gözləyir')

    return render(request, 'sifaris_izleme.html', {
        'sifarisler': sifarisler,
        'toplam_mebleg': toplam_mebleg,
        'odenilen_mebleg': odenilen_mebleg,
        'qaliq_borc': qaliq_borc,
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

        # Yeni məbləğləri hesabla
        item_total = round(float(cart_item.mehsul.qiymet * new_quantity), 2)
        
        # Ümumi səbət məbləğini hesabla
        cart_total = round(float(Sebet.objects.filter(user=request.user).aggregate(
            total=Sum(F('miqdar') * F('mehsul__qiymet'))
        )['total'] or 0), 2)

        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total': item_total,
            'total_amount': cart_total
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
    
    # Hər məhsul üçün cəmi məbləği hesablayaq
    for mehsul in sifaris_mehsullari:
        mehsul.cemi = mehsul.qiymet * mehsul.miqdar
    
    # Qalıq borcu hesablayaq
    sifaris.qaliq_borc = sifaris.cemi_mebleg - sifaris.odenilen_mebleg
    
    # Status mətnini əlavə edək
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
    if request.GET.get('pdf'):
        return generate_pdf(sifaris, sifaris_mehsullari)
    
    return render(request, 'sifaris_detallari.html', context)

def generate_pdf(sifaris, sifaris_mehsullari):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sifaris_{sifaris.id}.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.drawString(100, height - 50, "Sifariş Detalları")
    p.drawString(100, height - 70, f"Sifariş ID: {sifaris.id}")
    p.drawString(100, height - 90, f"Tarix: {sifaris.tarix.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, height - 110, f"Ümumi Məbləğ: {sifaris.cemi_mebleg} AZN")
    p.drawString(100, height - 130, f"Ödənilən Məbləğ: {sifaris.odenilen_mebleg} AZN")
    p.drawString(100, height - 150, f"Qalıq Borc: {sifaris.qaliq_borc} AZN")

    # Sifariş məhsulları
    p.drawString(100, height - 180, "Məhsul Adı | Miqdar | Qiymət | Cəmi")
    y = height - 200
    for mehsul in sifaris_mehsullari:
        p.drawString(100, y, f"{mehsul.mehsul.adi} | {mehsul.miqdar} | {mehsul.qiymet} AZN | {mehsul.cemi} AZN")
        y -= 20

    # İmza üçün xətt
    p.line(100, y, 300, y)
    p.drawString(100, y - 10, "İmza")

    p.showPage()
    p.save()
    buffer.seek(0)
    response.write(buffer.read())
    return response


def mehsul_haqqinda(request, mehsul_id):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    return render(request, 'mehsul_haqqinda.html', {
        'mehsul': mehsul
    })

