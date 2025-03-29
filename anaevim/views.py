from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya, OEMKod
from django.template.defaultfilters import slugify
from django.db.models import Q
import re

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
    # Filtrləmə parametrləri üçün lazımi modellər
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    
    # Axtarış parametrlərini alırıq
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    search_text = request.GET.get('search_text')
    
    # Başlanğıc olaraq bütün məhsulları götürürük
    mehsullar = Mehsul.objects.all()
    
    # Filtrləmə əməliyyatları
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)
    
    # OEM kodu ilə axtarış
    if search_text:
        # Xüsusi simvolları təmizlə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_text)
        
        # Birbaşa OEM və ya OEM_kodlar cədvəlində axtarış
        mehsullar = mehsullar.filter(
            Q(oem__icontains=clean_search) | 
            Q(oem_kodlar__kod__icontains=clean_search)
        ).distinct()
    
    context = {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
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

