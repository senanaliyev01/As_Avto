from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
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

def mehsul_etrafli(request, mehsul_id, mehsul_adi, mehsul_oem, mehsul_brend_kod):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    
    # Düzgün URL formatını yoxlayırıq
    duzgun_mehsul_adi = slugify(mehsul.mehsul_adi)
    duzgun_oem = slugify(mehsul.oem)
    duzgun_brend_kod = slugify(mehsul.brend_kodu)
    
    # Əgər URL parametrləri düzgün deyilsə, düzgün URL-ə 301 yönləndirmə edirik
    if mehsul_adi != duzgun_mehsul_adi or mehsul_oem != duzgun_oem or mehsul_brend_kod != duzgun_brend_kod:
        duzgun_url = f'/product/{duzgun_mehsul_adi}-{duzgun_oem}-{duzgun_brend_kod}/{mehsul_id}/'
        return redirect(duzgun_url, permanent=True)  # permanent=True 301 yönləndirməsini təmin edir
    
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

