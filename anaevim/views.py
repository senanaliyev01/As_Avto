from django.shortcuts import render, get_object_or_404, redirect
from mehsullar.models import Brend, Marka, Mehsul, MarkaSekil
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    # Əsas məlumatlar
    brendler = Brend.objects.all()
    markalar = Marka.objects.all()
    mehsullar_list = Mehsul.objects.all()
    
    # Axtarış parametrləri
    search_query = request.GET.get('search', '')
    selected_marka = request.GET.get('marka', '')
    selected_brend = request.GET.get('brend', '')
    
    # Axtarış sorğuları
    if search_query:
        mehsullar_list = mehsullar_list.filter(
            Q(adi__icontains=search_query) | 
            Q(oem__icontains=search_query) | 
            Q(brend_kod__icontains=search_query)
        )
    
    if selected_marka:
        mehsullar_list = mehsullar_list.filter(marka_id=selected_marka)
    
    if selected_brend:
        mehsullar_list = mehsullar_list.filter(brend_id=selected_brend)
    
    # Səhifələmə
    page = request.GET.get('page', 1)
    paginator = Paginator(mehsullar_list, 12)  # Hər səhifədə 12 məhsul
    
    try:
        mehsullar = paginator.page(page)
    except PageNotAnInteger:
        mehsullar = paginator.page(1)
    except EmptyPage:
        mehsullar = paginator.page(paginator.num_pages)
    
    # Axtarış parametrlərini saxlamaq
    search_params = ""
    if search_query:
        search_params += f"search={search_query}"
    if selected_marka:
        search_params += f"&marka={selected_marka}" if search_params else f"marka={selected_marka}"
    if selected_brend:
        search_params += f"&brend={selected_brend}" if search_params else f"brend={selected_brend}"
    
    context = {
        'brendler': brendler,
        'markalar': markalar,
        'mehsullar': mehsullar,
        'search_query': search_query,
        'selected_marka': selected_marka,
        'selected_brend': selected_brend,
        'search_params': search_params,
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

