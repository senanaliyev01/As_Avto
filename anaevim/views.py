from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil, Kateqoriya
from django.template.defaultfilters import slugify

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
    # Filterləmə parametrləri
    kateqoriya_id = request.GET.get('kateqoriya')
    brend_id = request.GET.get('brend')
    marka_id = request.GET.get('marka')
    search_query = request.GET.get('q')
    
    # Bütün məlumatları əldə et
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    mehsullar = Mehsul.objects.all()
    
    # Filtr parametrlərinə əsasən məhsulları filtrləmək
    if kateqoriya_id:
        mehsullar = mehsullar.filter(kateqoriya_id=kateqoriya_id)
    
    if brend_id:
        mehsullar = mehsullar.filter(brend_id=brend_id)
    
    if marka_id:
        mehsullar = mehsullar.filter(marka_id=marka_id)
    
    if search_query:
        mehsullar = mehsullar.filter(adi__icontains=search_query)
    
    context = {
        'brendler': brendler,
        'markalar': markalar,
        'kateqoriyalar': kateqoriyalar,
        'mehsullar': mehsullar,
        'selected_category': kateqoriya_id,
        'selected_brend': brend_id,
        'selected_marka': marka_id,
        'query': search_query,
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