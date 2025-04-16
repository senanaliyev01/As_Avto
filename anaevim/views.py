from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya
from django.template.defaultfilters import slugify
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

def mehsullar(request):
    # Kateqoriyaları və digər məlumatları əldə edirik
    kateqoriyalar = Kateqoriya.objects.all()
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    mehsullar = Mehsul.objects.all()
    
    # Axtarış parametrini alırıq
    search_query = request.GET.get('q')
    
    # Əgər axtarış parametri varsa, məhsulları filter edirik
    if search_query:
        mehsullar = mehsullar.filter(
            Q(adi__icontains=search_query) | 
            Q(oem__icontains=search_query) |
            Q(brend_kod__icontains=search_query)
        ).distinct()
    
    context = {
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
        'mehsullar': mehsullar,
        'search_query': search_query,
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