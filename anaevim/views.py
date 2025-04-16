from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya
from django.template.defaultfilters import slugify
from django.db.models import Q
import re
from django.http import JsonResponse

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

def mehsullar(request):
    # Başlanğıc olaraq bütün məhsulları götürürük
    mehsullar = Mehsul.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    
    # Axtarış və filtr parametrlərini alırıq
    search_text = request.GET.get('search_text')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    
    # Kateqoriya filtrləmə
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    # Brend filtlrləmə - vergüllə ayrılmış dəyərlər ola bilər
    if brand:
        brand_list = brand.split(',')
        q_objects = Q()
        for b in brand_list:
            q_objects |= Q(brend__adi=b)
        mehsullar = mehsullar.filter(q_objects)
    
    # Model/Marka filtrləmə - vergüllə ayrılmış dəyərlər ola bilər
    if model:
        model_list = model.split(',')
        q_objects = Q()
        for m in model_list:
            q_objects |= Q(marka__adi=m)
        mehsullar = mehsullar.filter(q_objects)
    
    # Axtarış mətni varsa
    if search_text:
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_text)
        
        # OEM kodlarında və məhsul adında axtarış
        mehsullar = mehsullar.filter(
            Q(oem__icontains=clean_search) |
            Q(brend_kod__icontains=clean_search) |
            Q(adi__icontains=search_text)  # Məhsul adı ilə axtarış
        ).distinct()
    
    context = {
        'brendler': brendler,
        'markalar': markalar,
        'kateqoriyalar': kateqoriyalar,
        'mehsullar': mehsullar,
    }
    
    return render(request, 'mehsullar.html', context)

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

def gizlilik(request):
    return render(request,'gizlilik.html')

def realtime_search(request):
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    # Xüsusi simvolları təmizlə
    clean_query = re.sub(r'[^a-zA-Z0-9]', '', query)
    
    # Axtarış sorğusu
    mehsullar = Mehsul.objects.filter(
        Q(adi__icontains=query) |                    # Ad
        Q(brend_kod__icontains=query) |              # Brend kodu
        Q(oem__icontains=clean_query)                # OEM kod
    ).distinct()[:20]  # Performans üçün maksimum 20 nəticə
    
    results = []
    for mehsul in mehsullar:
        results.append({
            'id': mehsul.id,
            'adi': mehsul.adi,
            'brend': mehsul.brend.adi if mehsul.brend else "",
            'marka': mehsul.marka.adi if mehsul.marka else "",
            'brend_kod': mehsul.brend_kod or "",
            'oem': mehsul.oem or "",
            'qiymet': str(mehsul.qiymet),
            'stok': mehsul.stok,
            'sekil_url': mehsul.sekil.url if mehsul.sekil else None
        })
    
    return JsonResponse({'results': results})