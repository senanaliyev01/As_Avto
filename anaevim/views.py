from django.shortcuts import render, get_object_or_404
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil

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

def mehsul_etrafli(request, mehsul_id, mehsul_adi, mehsul_brend_adi, mehsul_marka_adi, mehsul_brend_kod, mehsul_oem, mehsul_kateqoriya_adi):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id , adi=mehsul_adi, brend=mehsul_brend_adi, marka=mehsul_marka_adi,brend_kod=mehsul_brend_kod,oem=mehsul_oem,kateqoriya=mehsul_kateqoriya_adi)
    context = {
        'mehsul': mehsul
    }
    return render(request, 'mehsul_etrafli.html', context)

