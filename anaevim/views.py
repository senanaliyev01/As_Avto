from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
from django.template.defaultfilters import slugify
from django.urls import reverse

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
    
    # Düzgün URL-i yarat
    duzgun_url = reverse('mehsul_etrafli', kwargs={
        'mehsul_id': mehsul.id,
        'mehsul_adi': mehsul.adi.replace(' ', '-'),
        'mehsul_oem': mehsul.oem,
        'mehsul_brend_kod': mehsul.brend_kod
    })
    
    # Cari URL ilə düzgün URL-i müqayisə et
    cari_url = request.path
    if cari_url != duzgun_url:
        return redirect(duzgun_url, permanent=True)  # 301 yönləndirmə
    
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

