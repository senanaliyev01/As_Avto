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

def kataloq(request):
    # Başlanğıc olaraq bütün məhsulları götürürük
    mehsullar = Mehsul.objects.all()
    
    # Filter üçün lazım olan məlumatları çəkirik
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    
    # Axtarış parametrini alırıq
    search_query = request.GET.get('search', '')
    kateqoriya = request.GET.get('kateqoriya')
    brend = request.GET.get('brend')
    marka = request.GET.get('marka')
    
    # Əgər axtarış mətni varsa, filtrasiya tətbiq edirik
    if search_query:
        # Xüsusi simvolları təmizlə
        clean_query = re.sub(r'[^a-zA-Z0-9]', '', search_query)
        
        # Məhsul adı, OEM kodu, AS kodu və brendə görə axtarış
        mehsullar = mehsullar.filter(
            Q(adi__icontains=search_query) | 
            Q(oem_kodlar__kod__icontains=clean_query) |
            Q(brend_kod__icontains=search_query)
        ).distinct()
    
    # Əgər kateqoriya seçilibsə
    if kateqoriya:
        mehsullar = mehsullar.filter(kateqoriya__adi=kateqoriya)
    
    # Əgər brend seçilibsə
    if brend:
        mehsullar = mehsullar.filter(brend__adi=brend)
    
    # Əgər marka seçilibsə
    if marka:
        mehsullar = mehsullar.filter(marka__adi=marka)
    
    context = {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
        'search_query': search_query,
        'selected_kateqoriya': kateqoriya,
        'selected_brend': brend,
        'selected_marka': marka
    }
    
    return render(request, 'kataloq.html', context)

