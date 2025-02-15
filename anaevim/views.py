from django.shortcuts import render, get_object_or_404
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
from django.utils.text import slugify

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

def clean_url_param(param):
    return slugify(str(param))

def mehsul_etrafli(request, mehsul_id, marka, brend, brend_kod, oem, qiymet):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    return render(request, 'mehsul_etrafli.html', {'mehsul': mehsul})

