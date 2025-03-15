from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Sebet, Kateqoriya, Brend, Marka, Sifaris, SifarisMehsul, OEMKod, SebetItem, AxtarisSozleri
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
from istifadeciler.models import Profile
from django.contrib import messages

@login_required
def umumibaxis(request):
    # Bütün məhsulları əldə edirik
    mehsullar = Mehsul.objects.all()
    
    # Şablona göndəriləcək konteksti yaradırıq
    context = {
        'mehsullar': mehsullar,
    }
    
    return render(request, 'umumibaxis.html', context)


@login_required
def about(request):
    return render(request, 'about.html')



@login_required
def sebet_ekle(request, mehsul_id):
    try:
        mehsul = get_object_or_404(Mehsul, id=mehsul_id)
        miqdar = int(request.GET.get('miqdar', 1))  # Default olaraq 1

        if miqdar <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Miqdar 0-dan böyük olmalıdır'
            }, status=400)

        if miqdar > 999:
            return JsonResponse({
                'success': False,
                'error': 'Maksimum 999 ədəd sifariş edə bilərsiniz'
            }, status=400)

        sebet, created = Sebet.objects.get_or_create(user=request.user, mehsul=mehsul)
        
        if created:
            sebet.miqdar = miqdar
        else:
            sebet.miqdar += miqdar
            
        if sebet.miqdar > 999:
            return JsonResponse({
                'success': False,
                'error': 'Səbətdəki ümumi miqdar 999-dan çox ola bilməz'
            }, status=400)
            
        sebet.save()

        return JsonResponse({
            'success': True,
            'mehsul': {
                'adi': mehsul.adi,
                'sekil': mehsul.sekil.url if mehsul.sekil else None,
                'oem': mehsul.oem,
                'miqdar': sebet.miqdar
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

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

def normalize_search_text(text):
    if not text:
        return "", []
    
    # Azərbaycan hərflərini ingilis hərflərinə çevirmək üçün mapping
    az_to_en = {
        'ə': 'e', 'Ə': 'E',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S',
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G'
    }
    
    # Bütün mətni kiçik hərflərə çevir
    text = text.lower()
    
    # Azərbaycan hərflərini ingilis hərflərinə çevir
    for az, en in az_to_en.items():
        text = text.replace(az, en)
    
    # Yalnız hərf və rəqəmləri saxla, digər bütün simvolları boşluqla əvəz et
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    
    # Birdən çox boşluğu tək boşluqla əvəz et
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Əvvəl və sondakı boşluqları sil
    normalized = normalized.strip()
    
    # Sözləri ayır
    words = normalized.split()
    
    # Axtarış üçün faydalı kombinasiyalar yaradırıq (permutasiyalar əvəzinə)
    word_combinations = []
    
    # Orijinal birləşmiş variant (bütün sözlər birləşdirilmiş)
    if words:
        word_combinations.append(''.join(words))
    
    # Orijinal mətn (boşluqlarla)
    if normalized:
        word_combinations.append(normalized)
    
    # Hər bir sözü ayrıca əlavə et
    word_combinations.extend(words)
    
    # Ardıcıl iki sözü birləşdirərək əlavə et (daha çox axtarış variantı üçün)
    if len(words) >= 2:
        for i in range(len(words) - 1):
            word_combinations.append(words[i] + words[i + 1])
    
    # Təkrarları silmək üçün set istifadə edirik
    return normalized, list(set(word_combinations))

@login_required
def products_list(request):
    # Başlanğıc olaraq bütün məhsulları götürürük
    mehsullar = Mehsul.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    axtaris_sozleri = AxtarisSozleri.objects.all()

    # Axtarış parametrlərini alırıq
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    axtaris = request.GET.get('axtaris')
    search_text = request.GET.get('search_text')

    # Brend, kateqoriya və marka üçün dəqiq filtrasiya
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)
        
    if axtaris:
        mehsullar = mehsullar.filter(axtaris_sozleri__adi=axtaris)

    # Axtarış mətni varsa
    if search_text:
        # Axtarış mətnini normalize et
        normalized_search, search_combinations = normalize_search_text(search_text)
        
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_text)
        
        # Axtarış sorğusunu yarat - daha effektiv sorğu
        query = Q()
        
        # OEM kodlarında axtarış
        query |= Q(oem_kodlar__kod__icontains=clean_search)
        
        # Axtarış sözlərində axtarış
        query |= Q(axtaris_sozleri__sozler__icontains=clean_search)
        
        # Hər bir axtarış kombinasiyası üçün sorğu əlavə et
        # Amma çox böyük sorğular yaratmamaq üçün maksimum 5 kombinasiya istifadə et
        for combo in search_combinations[:5]:
            query |= Q(axtaris_sozleri__sozler__icontains=combo)
        
        # Sorğunu tətbiq et
        mehsullar = mehsullar.filter(query).distinct()

    return render(request, 'products_list.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
        'axtaris_sozleri': axtaris_sozleri
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
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'total': cemi_mebleg,
                'is_empty': not sebet.exists()
            })
        else:
            messages.success(request, 'Məhsul səbətdən silindi')
            return redirect('view_cart')
            
    except Sebet.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Məhsul tapılmadı'
            }, status=404)
        else:
            messages.error(request, 'Məhsul tapılmadı')
            return redirect('view_cart')

@login_required
def sifarisi_gonder(request):
    if request.method == "POST":
        try:
            # JSON data-nı parse et
            data = json.loads(request.body)
            selected_items = data.get('selected_items', [])
            
            if not selected_items:
                return JsonResponse({
                    'success': False,
                    'message': 'Heç bir məhsul seçilməyib'
                }, status=400)

            # Seçilmiş məhsulları əldə et
            sebet_items = Sebet.objects.filter(
                user=request.user,
                id__in=selected_items
            )

            if not sebet_items.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Seçilmiş məhsullar tapılmadı'
                }, status=404)

            # Yeni sifarişi yarat
            sifaris = Sifaris.objects.create(
                user=request.user,
                cemi_mebleg=0
            )

            total_amount = 0
            # Seçilmiş məhsulları sifarişə əlavə et
            for item in sebet_items:
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

            # Yalnız seçilmiş məhsulları səbətdən sil
            sebet_items.delete()

            return JsonResponse({
                'success': True,
                'message': 'Sifarişiniz uğurla qeydə alındı'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Yanlış format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Xəta baş verdi: {str(e)}'
            }, status=500)

    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu'
    }, status=405)


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
        # Tarixi Bakı1 saatına uyğunlaşdırırıq
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
    sebet = Sebet.objects.filter(user=request.user)
    count = sebet.count()
    cemi_mebleg = sebet.aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0
    
    return JsonResponse({
        'count': count,
        'total': cemi_mebleg
    })

@login_required
def get_cart_items(request):
    sebet = Sebet.objects.filter(user=request.user)
    cemi_mebleg = sebet.aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0
    
    items = []
    for item in sebet:
        items.append({
            'id': item.id,
            'name': item.mehsul.adi,
            'brand': item.mehsul.brend.adi if item.mehsul.brend else '',
            'model': item.mehsul.marka.adi if item.mehsul.marka else '',
            'oem': item.mehsul.oem,
            'brend_kod': item.mehsul.brend_kod,
            'price': item.mehsul.qiymet,
            'quantity': item.miqdar,
            'image': item.mehsul.sekil.url if item.mehsul.sekil else None,
            'total': item.mehsul.qiymet * item.miqdar
        })
    
    return JsonResponse({
        'items': items,
        'total': cemi_mebleg
    })

@login_required
def update_quantity(request, item_id, new_quantity):
    try:
        cart_item = get_object_or_404(Sebet, id=item_id, user=request.user)
        
        try:
            new_quantity = int(new_quantity)
            if new_quantity < 1:
                new_quantity = 1
            elif new_quantity > 999:
                return JsonResponse({
                    'success': False,
                    'error': 'Maksimum 999 ədəd sifariş edə bilərsiniz'
                }, status=400)
                
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Düzgün miqdar daxil edin'
            }, status=400)

        # Miqdarı yenilə
        cart_item.miqdar = new_quantity
        cart_item.save()

        # Yeni məbləğləri hesabla
        item_total = float(cart_item.mehsul.qiymet * new_quantity)
        
        # Ümumi səbət məbləğini hesabla
        cart_total = float(Sebet.objects.filter(user=request.user).aggregate(
            total=Sum(F('miqdar') * F('mehsul__qiymet'))
        )['total'] or 0)

        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'item_total': round(item_total, 2),
            'total_amount': round(cart_total, 2)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def mehsul_axtaris(request):
    query = request.GET.get('q')
    if query:
        # Başlanğıc sorğunu yaradırıq
        mehsullar = Mehsul.objects.all()
        
        # Axtarış mətnini normalize et və kombinasiyaları al
        normalized_query, query_combinations = normalize_search_text(query)
        
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_query = re.sub(r'[^a-zA-Z0-9]', '', query)
        
        # Axtarış sorğusunu yarat - daha effektiv sorğu
        search_query = Q()
        
        # OEM kodlarında axtarış
        search_query |= Q(oem_kodlar__kod__icontains=clean_query)
        
        # Axtarış sözlərində axtarış
        search_query |= Q(axtaris_sozleri__sozler__icontains=clean_query)
        
        # Hər bir axtarış kombinasiyası üçün sorğu əlavə et
        # Amma çox böyük sorğular yaratmamaq üçün maksimum 5 kombinasiya istifadə et
        for combo in query_combinations[:5]:
            search_query |= Q(axtaris_sozleri__sozler__icontains=combo)
        
        # Sorğunu tətbiq et
        mehsullar = mehsullar.filter(search_query).distinct()
        
        # Nəticələri qaytarırıq
        return JsonResponse({
            'success': True,
            'mehsullar': list(mehsullar.values(
                'id', 
                'adi', 
                'brend__adi', 
                'marka__adi',
                'oem', 
                'brend_kod', 
                'qiymet',
                'stok',
                'haqqinda',
                'axtaris_sozleri__adi'
            ))
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Axtarış parametri daxil edilməyib'
    })

@login_required
def sifaris_detallari(request, sifaris_id):
    # Sifarişin yalnız cari istifadəçiyə aid olub olmadığını yoxlayır
    try:
        sifaris = Sifaris.objects.get(id=sifaris_id)
    except Sifaris.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Sifariş tapılmadı'}, status=404)

    sifaris_mehsullari = SifarisMehsul.objects.filter(sifaris=sifaris)
    
    # Müştəri nömrəsini profile modelindən al
    profile = get_object_or_404(Profile, user=sifaris.user)  # Müştərinin profilini əldə et

    # Hər məhsul üçün cəmi məbləği hesablayaq
    for mehsul in sifaris_mehsullari:
        mehsul.cemi = mehsul.qiymet * mehsul.miqdar
    
    # Qalıq borcu hesablayaq
    sifaris.qaliq_borc = sifaris.cemi_mebleg - sifaris.odenilen_mebleg
    
    sifarisler = Sifaris.objects.filter(user=sifaris.user)
    toplam_mebleg = sum(sifaris.cemi_mebleg for sifaris in sifarisler)
    odenilen_mebleg = sum(sifaris.odenilen_mebleg for sifaris in sifarisler)
    sifaris.qaliq_borc = toplam_mebleg - odenilen_mebleg  # Burada qalıq borcu hesablayırıq
    
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
        'musteri_novresi': profile.telefon,
        'musteri_unvani': profile.unvan  
    }
    
    if request.GET.get('pdf'):
        return generate_pdf(sifaris, sifaris_mehsullari, profile)

    return render(request, 'sifaris_detallari.html', context)

@login_required
def generate_pdf(sifaris, sifaris_mehsullari, profile):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sifaris_{sifaris.id}.pdf"'

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=0, bottomMargin=20)
    elements = []

    # Fontu qeyd edirik
    pdfmetrics.registerFont(TTFont('NotoSans', 'mehsullar/NotoSans-Regular.ttf'))  # Düzgün yolu göstərin
    styles = getSampleStyleSheet()
    
    # Normal stilini NotoSans fontu ilə dəyişdirin
    styles['Normal'].fontName = 'NotoSans'
    styles['Title'].fontName = 'NotoSans'  # Başlıq üçün fontu dəyişdirin
    
    # Şirkət loqosunu əlavə edin
    logo_path = 'static/img/Header_Logo.png'  # Loqonun yolu
    logo = Image(logo_path, width=300, height=100)  # Loqonun ölçülərini tənzimləyin
    logo.hAlign = 'CENTER'
    elements.append(logo)
    elements.append(Paragraph("", styles['Normal']))  # Boşluq əlavə et

    # Sifariş nömrəsini mərkəzləşdirərək H1 formatında yazırıq
    order_number_table = Table([[Paragraph(f"Sifariş №{sifaris.id}", styles['Title'])]], colWidths=[None])  # H1 stili üçün 'Title' istifadə edin
    order_number_table.setStyle([('ALIGN', (0, 0), (0, 0), 'CENTER')])  # Mərkəzləşdirmək
    elements.append(order_number_table)
 
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et
 
    # Sifariş məlumatları
    elements.append(Paragraph(f"Satıcı: AS-AVTO ", styles['Normal']))
    elements.append(Paragraph(f"Müştəri: {sifaris.user.username}", styles['Normal']))
    elements.append(Paragraph(f"Müştəri Nömrəsi: {profile.telefon}", styles['Normal']))
    elements.append(Paragraph(f"Müştəri Ünvanı: {profile.unvan}", styles['Normal']))
    elements.append(Paragraph(f"Tarix: {sifaris.tarix.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et

    # Cədvəl yaradılması
    data = [['№', 'Adı', 'Firma', 'Brend', 'Oem', 'Say', 'Qiymət', 'Cəmi']]
    for index, mehsul in enumerate(sifaris_mehsullari, start=1):
        data.append([index, mehsul.mehsul.adi, mehsul.mehsul.brend.adi, mehsul.mehsul.brend_kod, mehsul.mehsul.oem, mehsul.miqdar, f"{mehsul.qiymet} AZN", f"{mehsul.cemi} AZN"])

    # Cədvəl yaradılması
    table = Table(data)  # Sütun genişliklərini təyin etmədən cədvəl yaradın
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Başlıq arxa planı
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Başlıq mətni
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Mərkəzləşdirmək
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),  # Başlıq fontu
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),  # Cədvəl mətni üçün fontu NotoSans ilə dəyişdirin
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Başlıq padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Cədvəl arxa planı
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Cədvəl xətləri
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font ölçüsünü tənzimləyin
        ('TOPPADDING', (0, 0), (-1, 0), 10),  # Başlıq üst padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),  # Cədvəl alt padding
        ('WORD_WRAP', (0, 0), (-1, -1), 'CJK'),  # Yazıların sığması üçün
    ]))

    elements.append(table)
    
    # Ümumi məbləği cədvəlin altında göstər
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq əlavə et
    total_amount = Paragraph(f"<strong>Ümumi Məbləğ: {sifaris.cemi_mebleg} AZN</strong>", styles['Normal'])
    elements.append(total_amount)
    elements.append(Paragraph("<br/><br/>", styles['Normal']))
    elements.append(Paragraph(f"Qalıq Borc (Qaimə Daxil): {sifaris.qaliq_borc} AZN", styles['Normal']))

    # İmza üçün xətt
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq

    # İmzaları yan-yana yerləşdirmək üçün cədvəl yaradın
    imza_data = [
        [Paragraph("Təhvil Aldı: ____________________", styles['Normal']), 
         Paragraph("Təhvil Verdi: ____________________", styles['Normal'])],
    ]
    
    imza_table = Table(imza_data, colWidths=[200, 200])  # İmzaların genişliyini tənzimləyin
    imza_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Sol hizalama
        ('TOPPADDING', (0, 0), (-1, -1), 10),  # Üst padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),  # Alt padding
    ]))

    elements.append(imza_table)

    # Ödənilən məbləği ortada yerləşdirin
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Boşluq
    elements.append(Paragraph("Ödənilən Məbləğ: ___________________________ AZN | İmza:____________________", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response.write(buffer.read())
    return response


@login_required
def mehsul_haqqinda(request, mehsul_id, mehsul_adi, mehsul_oem, mehsul_brend_kod):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    return render(request, 'mehsul_haqqinda.html', {
        'mehsul': mehsul
    })

@login_required
def hesabatlar(request):
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

    return render(request, 'hesabatlar.html', {
        'sifarisler': sifarisler,
        'toplam_mebleg': toplam_mebleg,
        'odenilen_mebleg': odenilen_mebleg,
        'qaliq_borc': qaliq_borc,
    })

@login_required
def realtime_search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    model = request.GET.get('model', '')
    axtaris = request.GET.get('axtaris', '')
    
    mehsullar = Mehsul.objects.all()
    
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)
    if axtaris:
        mehsullar = mehsullar.filter(axtaris_sozleri__adi=axtaris)
    
    if query:
        # Axtarış mətnini normalize et
        normalized_query, query_combinations = normalize_search_text(query)
        
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_query = re.sub(r'[^a-zA-Z0-9]', '', query)
        
        # Axtarış sorğusunu yarat - daha effektiv sorğu
        search_query = Q()
        
        # OEM kodlarında axtarış
        search_query |= Q(oem_kodlar__kod__icontains=clean_query)
        
        # Axtarış sözlərində axtarış
        search_query |= Q(axtaris_sozleri__sozler__icontains=clean_query)
        
        # Hər bir axtarış kombinasiyası üçün sorğu əlavə et
        # Amma çox böyük sorğular yaratmamaq üçün maksimum 5 kombinasiya istifadə et
        for combo in query_combinations[:5]:
            search_query |= Q(axtaris_sozleri__sozler__icontains=combo)
        
        # Sorğunu tətbiq et
        mehsullar = mehsullar.filter(search_query).distinct()
    
    results = []
    for mehsul in mehsullar:
        results.append({
            'id': mehsul.id,
            'adi': mehsul.adi,
            'brend': mehsul.brend.adi,
            'marka': mehsul.marka.adi,
            'brend_kod': mehsul.brend_kod,
            'oem': mehsul.oem,
            'qiymet': str(mehsul.qiymet),
            'stok': mehsul.stok,
            'sekil_url': mehsul.sekil.url if mehsul.sekil else None,
            'haqqinda': mehsul.haqqinda if mehsul.haqqinda else None,
            'axtaris_sozleri': mehsul.axtaris_sozleri.adi if mehsul.axtaris_sozleri else None,
        })
    
    return JsonResponse({'results': results})
