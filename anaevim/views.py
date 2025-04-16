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
    # Kateqoriyaları və digər məlumatları əldə edirik
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    mehsullar = Mehsul.objects.all()
    
    # Axtarış parametrini alırıq
    search_query = request.GET.get('q')
    search_performed = False
    
    # Əgər axtarış parametri varsa, məhsulları filter edirik
    if search_query:
        search_performed = True
        # Xüsusi simvolları təmizlə (əlavə OEM kodları üçün)
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query)
        
        # Məhsul adı və əlavə OEM kodları ilə axtarış
        # Qeyd: OEMKod modelində əlavə OEM kodları saxlanılır və mehsul ilə ForeignKey əlaqəsi var
        # Buna görə də "oem_kodlar__kod" ilə axtarış aparırıq (related_name = 'oem_kodlar')
        mehsullar = mehsullar.filter(
            Q(adi__icontains=search_query) |           # Məhsul adı ilə axtarış
            Q(oem_kodlar__kod__icontains=clean_search)  # Əlavə OEM kodları ilə axtarış
        ).distinct()  # Təkrarlanmaları aradan qaldırmaq üçün distinct() istifadə edirik
    
    # Axtarış nəticəsi boşdursa və axtarış edilmişdirsə, konsola mesaj çap edirik (debug məqsədilə)
    if search_performed and not mehsullar.exists():
        print(f"OEM axtarışı üçün heç bir nəticə tapılmadı: {search_query} (təmizlənmiş: {clean_search})")
    
    context = {
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
        'mehsullar': mehsullar,
        'search_query': search_query,
        'search_performed': search_performed
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