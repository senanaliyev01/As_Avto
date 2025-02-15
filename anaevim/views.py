from django.shortcuts import render, get_object_or_404
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
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

