from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
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

def catalogue(request):
    mehsullar = []
    is_searched = False
    search_query = request.GET.get('q', '')
    
    # Filter datalarını hazırla
    kateqoriyalar = Mehsul.objects.values_list('kateqoriya__adi', flat=True).distinct()
    brendler = Mehsul.objects.values_list('brend__adi', flat=True).distinct()
    markalar = Mehsul.objects.values_list('marka__adi', flat=True).distinct()
    
    if search_query:
        is_searched = True
        # Xüsusi simvolları təmizlə
        clean_query = re.sub(r'[^a-zA-Z0-9]', '', search_query)
        
        # OEM kodlarında, AS kodunda və məhsul adında axtarış
        mehsullar = Mehsul.objects.filter(
            Q(oem_kodlar__kod__icontains=clean_query) | 
            Q(adi__icontains=search_query) |
            Q(brend_kod__icontains=search_query) |
            Q(as_kodu__icontains=clean_query)
        ).distinct()
    
    context = {
        'mehsullar': mehsullar,
        'is_searched': is_searched,
        'search_query': search_query,
        'kateqoriyalar': kateqoriyalar,
        'brendler': brendler,
        'markalar': markalar,
    }
    
    return render(request, 'catalogue.html', context)

