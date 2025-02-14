from django.shortcuts import render
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil

def home(request):
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    mehsullar = Mehsul.objects.all()
    marka_sekiller = MarkaSekil.objects.all()
    
    context = {
        'brendler': brendler,
        'markalar': markalar,
        'mehsullar': mehsullar,
        'marka_sekiller': marka_sekiller,
    }
    
    return render(request, 'home.html', context)
