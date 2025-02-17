from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
from django.template.defaultfilters import slugify
from django.http import HttpResponsePermanentRedirect
from urllib.parse import quote

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
    
    # URL-in düzgün formatda olub-olmadığını yoxlayırıq
    duzgun_mehsul_adi = slugify(mehsul.ad)
    duzgun_oem = quote(mehsul.oem_kod) if mehsul.oem_kod else ''
    duzgun_brend = quote(mehsul.brend.kod) if mehsul.brend else ''
    
    # Əgər URL parametrləri düzgün deyilsə, 301 yönləndirmə edirik
    if mehsul_adi != duzgun_mehsul_adi or mehsul_oem != duzgun_oem or mehsul_brend_kod != duzgun_brend:
        duzgun_url = f'/product/{duzgun_mehsul_adi}-{duzgun_oem}-{duzgun_brend}/{mehsul_id}/'
        return HttpResponsePermanentRedirect(duzgun_url)
    
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

