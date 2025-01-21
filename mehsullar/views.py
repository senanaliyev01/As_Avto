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
import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from django.utils import timezone
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image


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
        # Tarixi Bakı saatına uyğunlaşdırırıq
        sifaris.tarix = sifaris.tarix.astimezone(timezone.get_current_timezone())
        # Tarixi formatlayırıq
        sifaris.formatted_tarix = sifaris.tarix.strftime('%Y-%m-%d %H:%M:%S')

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
    
    # Tarixi formatlayırıq
    sifaris.formatted_tarix = sifaris.tarix.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
    
    context = {
        'sifaris': sifaris,
        'sifaris_mehsullari': sifaris_mehsullari,
    }
    
    if request.GET.get('pdf'):
        return generate_pdf(sifaris, sifaris_mehsullari)

    return render(request, 'sifaris_detallari.html', context)

@login_required
def generate_pdf(sifaris, sifaris_mehsullari):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sifaris_{sifaris.id}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Fontu qeyd edirik
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'mehsullar/DejaVuSans.ttf'))  # Düzgün yolu göstərin
    styles = getSampleStyleSheet()
    
    # Normal stilini DejaVuSans fontu ilə dəyişdirin
    styles['Normal'].fontName = 'DejaVuSans'
    styles['Title'].fontName = 'DejaVuSans'  # Başlıq üçün fontu dəyişdirin
    
    # Şirkət loqosunu əlavə edin
    logo_path = 'static/img/Header_Logo.png'  # Loqonun yolu
    logo = Image(logo_path, width=150, height=150)  # Loqonun ölçülərini tənzimləyin
    elements.append(logo)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et




    # Header
    header = Paragraph("Sifariş Detalları", styles['Title'])
    elements.append(header)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et

    # Sifariş məlumatları
    elements.append(Paragraph(f"İstifadəçi: {sifaris.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Sifariş ID: {sifaris.id}", styles['Normal']))
    elements.append(Paragraph(f"Tarix: {sifaris.tarix.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"Qalıq Borc: {sifaris.qaliq_borc} AZN", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et

    # Sifariş məhsulları üçün cədvəl
    data = [['Məhsul Adı', 'Brend Kod', 'Oem Kod', 'Miqdar', 'Qiymət', 'Cəmi']]
    for mehsul in sifaris_mehsullari:
        data.append([mehsul.mehsul.adi, mehsul.mehsul.brend_kod, mehsul.mehsul.oem, mehsul.miqdar, f"{mehsul.qiymet} AZN", f"{mehsul.cemi} AZN"])

    # Cədvəl yaradılması
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Başlıq arxa planı
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Başlıq mətni
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Mərkəzləşdirmək
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),  # Başlıq fontu
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Başlıq padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Cədvəl arxa planı
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cədvəl xətləri
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font ölçüsünü tənzimləyin
        ('TOPPADDING', (0, 0), (-1, 0), 10),  # Başlıq üst padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),  # Cədvəl alt padding
        
    ]))

    elements.append(table)
    
    
    # Ümumi məbləği cədvəlin altında göstər
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et
    total_amount = Paragraph(f"<strong>Ümumi Məbləğ: {sifaris.cemi_mebleg} AZN</strong>", styles['Normal'])
    elements.append(total_amount)

    # İmza üçün xətt
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq
    elements.append(Paragraph("Təhvil Aldı: ____________________", styles['Normal']))
    
    # İmza üçün xətt
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq
    elements.append(Paragraph("Təhvil Verdi: ____________________", styles['Normal']))
    
    # İmza üçün xətt
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq
    elements.append(Paragraph("Ödənilən Məbləğ: ___________________________", styles['Normal']))
    
   

    doc.build(elements)
    buffer.seek(0)
    response.write(buffer.read())
    return response


def mehsul_haqqinda(request, mehsul_id):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    return render(request, 'mehsul_haqqinda.html', {
        'mehsul': mehsul
    })

