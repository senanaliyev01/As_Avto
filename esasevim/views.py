from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_list_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from mehsullar.models import Kateqoriya, Brend, Marka, Mehsul, MusteriReyi
from django.views.decorators.cache import never_cache
from django.db.models import Count, Avg
from django.contrib import messages

@login_required
def rey_elave_et(request):
    if request.method == 'POST':
        qiymetlendirme = request.POST.get('qiymetlendirme')
        rey_metni = request.POST.get('rey')
        
        if qiymetlendirme and rey_metni:
            try:
                MusteriReyi.objects.create(
                    musteri=request.user,
                    qiymetlendirme=qiymetlendirme,
                    rey=rey_metni,
                    tesdiq=False  # Admin təsdiqləyənə qədər false olacaq
                )
                return JsonResponse({
                    'success': True,
                    'message': 'Rəyiniz uğurla göndərildi və təsdiq gözləyir.'
                })
            except Exception as e:
                print(f"Xəta: {str(e)}")  # Xətanı console-da göstər
                return JsonResponse({
                    'success': False,
                    'message': 'Xəta baş verdi. Zəhmət olmasa bir az sonra yenidən cəhd edin.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Zəhmət olmasa ulduz seçin və rəyinizi yazın.'
            })
    
    return JsonResponse({
        'success': False, 
        'message': 'Yanlış sorğu metodu.'
    })

@login_required
def esasevim(request):
    # Təsdiqlənmiş rəylər
    tesdiqli_reyler = MusteriReyi.objects.filter(tesdiq=True)
    
    # Yeni məhsulları əldə et (limitsiz)
    yeni_mehsullar = Mehsul.objects.filter(yenidir=True)
    
    # Ümumi statistika
    rey_statistikasi = MusteriReyi.objects.filter(tesdiq=True).aggregate(
        ortalama=Avg('qiymetlendirme'),
        toplam=Count('id')
    )
    
    # Ulduz saylarına görə statistika
    ulduz_statistikasi = []
    if rey_statistikasi['toplam'] > 0:
        ulduz_statistikasi = MusteriReyi.objects.filter(tesdiq=True).values(
            'qiymetlendirme'
        ).annotate(
            sayi=Count('id')
        ).order_by('qiymetlendirme')
    
    context = {
        'reyler': tesdiqli_reyler,
        'rey_statistikasi': rey_statistikasi,
        'ulduz_statistikasi': ulduz_statistikasi,
        'yeni_mehsullar': yeni_mehsullar  # Context-ə yeni məhsulları əlavə et
    }
    
    return render(request, 'main.html', context)

@login_required
@never_cache
def get_statistics(request):
    try:
        # İstifadəçi sayı
        user_count = User.objects.count()
        
        # Birbaşa model sayları
        categories = Kateqoriya.objects.count()
        brands = Brend.objects.count()
        car_brands = Marka.objects.count()
        products = Mehsul.objects.count()

        # Debug məlumatı
        print(f"""
        Statistika:
        - İstifadəçilər: {user_count}
        - Kateqoriyalar: {categories}
        - Brendlər: {brands}
        - Markalar: {car_brands}
        - Məhsullar: {products}
        """)

        return JsonResponse({
            'users': user_count,
            'categories': categories,
            'brands': brands,
            'car_brands': car_brands,
            'products': products
        })

    except Exception as e:
        print(f"Xəta baş verdi: {str(e)}")
        return JsonResponse({
            'users': 0,
            'categories': 0,
            'brands': 0,
            'car_brands': 0,
            'products': 0
        })

@login_required
def yeni_mehsullar_view(request):
    yeni_mehsullar = get_list_or_404(Mehsul, yenidir=True)
    context = {
        'yeni_mehsullar': yeni_mehsullar
    }
    return render(request, 'yeni_mehsullar.html', context)