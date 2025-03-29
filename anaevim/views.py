from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya
from django.template.defaultfilters import slugify
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

def mehsullar(request):
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
    oem_search = request.GET.get('oem_search')

    # Brend, kateqoriya və marka üçün dəqiq filtrasiya
    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi=category)
    
    if brand:
        mehsullar = mehsullar.filter(brend__adi=brand)
    
    if model:
        mehsullar = mehsullar.filter(marka__adi=model)

    # Axtarış mətni varsa
    if search_text:
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_text)
        
        # OEM kodlarında axtarış
        mehsullar = mehsullar.filter(oem_kodlar__kod__icontains=clean_search).distinct()
    
    # Xüsusi OEM axtarışı
    if oem_search:
        # Xüsusi simvolları təmizlə
        clean_oem = re.sub(r'[^a-zA-Z0-9]', '', oem_search)
        
        # OEM kodları ilə genişləndirilmiş axtarış
        mehsullar = mehsullar.filter(
            Q(oem_kodlar__kod__icontains=clean_oem) |
            Q(adi__icontains=oem_search) |
            Q(brend_kod__icontains=oem_search)
        ).distinct()

    return render(request, 'mehsullar.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar
    })

