from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya
from django.template.defaultfilters import slugify
from django.http import JsonResponse
import re
from django.db.models import Q

def anaevim(request):
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    mehsullar = Mehsul.objects.all()
    marka_sekiller = MarkaSekil.objects.all()
    
    context = {
        'brendler': brendler,
        'markalar': markalar,
        'mehsullar': mehsullar,
    }
    
    return render(request, 'home.html', context)

def mehsul_etrafli(request, mehsul_id, mehsul_adi=None, mehsul_oem=None, mehsul_brend_kod=None):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    
    # Düzgün URL-i yarat
    duzgun_url = f'/product/{slugify(mehsul.adi)}-{mehsul.oem}-{mehsul.brend_kod}/{mehsul.id}/'
    
    # Əgər URL düzgün deyilsə, 301 yönləndirmə et
    if request.path != duzgun_url:
        return redirect(duzgun_url, permanent=True)
    
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

def catalogue(request):
    """
    Jikiu.jp tipli kataloq səhifəsi.
    Məhsulları müxtəlif parametrlərə görə axtarmaq üçün səhifə.
    """
    # Kataloqda göstəriləcək məlumatları əldə edirik
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    
    # Məlumatlar
    context = {
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler, 
        'markalar': markalar,
    }
    
    return render(request, 'catalogue.html', context)

def catalogue_search(request):
    """
    Kataloq axtarışı üçün API. Məhsulları müxtəlif parametrlərə görə axtarır.
    """
    search_type = request.GET.get('search_type', 'product_no')
    query = request.GET.get('query', '').strip()
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    year = request.GET.get('year')
    engine = request.GET.get('engine')
    
    # Nəticələr siyahısı
    mehsullar = Mehsul.objects.all()
    
    # Əsas axtarış məntiqi
    if search_type == 'product_no' and query:
        # Xüsusi simvolları təmizlə
        clean_query = re.sub(r'[^a-zA-Z0-9]', '', query)
        
        # OEM, AS kodu və brend kodu ilə axtarış
        mehsullar = mehsullar.filter(
            Q(oem_kodlar__kod__icontains=clean_query) | 
            Q(oem__icontains=clean_query) |
            Q(as_kodu__icontains=clean_query) |
            Q(brend_kod__icontains=query)
        ).distinct()
    
    # Əlavə filterlər
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)
    
    if year:
        # İl filtri model-də il sahəsinə görədir
        mehsullar = mehsullar.filter(model__il__il=year)
    
    if engine:
        # Motor filtri model-də motor sahəsinə görədir
        mehsullar = mehsullar.filter(model__motor__motor=engine)
    
    # Əgər AJAX sorğusu gəlirsə, JSON formatında nəticələri qaytarırıq
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = []
        for mehsul in mehsullar[:50]:  # Maksimum 50 nəticə qaytarırıq
            results.append({
                'id': mehsul.id,
                'adi': mehsul.adi,
                'brend': mehsul.brend.adi if mehsul.brend else "",
                'marka': mehsul.marka.adi if mehsul.marka else "",
                'oem': mehsul.oem,
                'as_kodu': mehsul.as_kodu,
                'brend_kod': mehsul.brend_kod,
                'qiymet': str(mehsul.qiymet),
                'stok': mehsul.stok,
                'sekil_url': mehsul.sekil.url if mehsul.sekil else None,
                'oem_kodlar': [kod.kod for kod in mehsul.oem_kodlar.all()],
                'url': f'/product/{slugify(mehsul.adi)}-{mehsul.oem}-{mehsul.brend_kod}/{mehsul.id}/'
            })
        
        return JsonResponse({'results': results})
    
    # Normal sorğu üçün səhifəni göstəririk
    context = {
        'mehsullar': mehsullar[:100],  # Təhlükəsizlik üçün maksimum 100 məhsul
        'kateqoriyalar': Kateqoriya.objects.all(),
        'brendler': Brend.objects.all(),
        'markalar': Marka.objects.all(),
        'search_query': query,
        'search_type': search_type,
        'selected_category': category,
        'selected_brand': brand,
        'selected_model': model
    }
    
    return render(request, 'catalogue_results.html', context)

