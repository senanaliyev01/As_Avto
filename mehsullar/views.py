from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Sebet, Kateqoriya, Brend, Marka,Sifaris,SifarisMehsul
from django.db.models import F, Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def about(request):
    return render(request, 'about.html')



@login_required
def sebet_ekle(request, mehsul_id):
    mehsul = get_object_or_404(Mehsul, id=mehsul_id)
    sebet, created = Sebet.objects.get_or_create(user=request.user, mehsul=mehsul)
    if not created:
        sebet.miqdar += 1
        sebet.save()

    # Yalnız uğurlu əlavə üçün cavab
    return HttpResponse(status=204)
@login_required
def view_cart(request):
    sebet = Sebet.objects.filter(user=request.user)
    cemi_mebleg = sebet.aggregate(total=Sum(F('miqdar') * F('mehsul__qiymet')))['total'] or 0

    return render(request, 'cart.html', {
        'sebet': sebet,
        'cemi_mebleg': cemi_mebleg
    })
@login_required
def products_list(request):
    # Məhsulları və axtarış nəticələrini idarə edir
    mehsullar = Mehsul.objects.all()
    kateqoriyalar = Kateqoriya.objects.all()
    brendlər = Brend.objects.all()
    markalar = Marka.objects.all()

    # Axtarış parametrlərini idarə edir
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    model = request.GET.get('model')
    search_text = request.GET.get('search_text')

    if category:
        mehsullar = mehsullar.filter(kateqoriya__adi__icontains=category)
    if brand:
        mehsullar = mehsullar.filter(brend__adi__icontains=brand)
    if model:
        mehsullar = mehsullar.filter(marka__adi__icontains=model)
    if search_text:
        mehsullar = mehsullar.filter(brend_kod__icontains=search_text) | mehsullar.filter(oem_kod__icontains=search_text)

    return render(request, 'products_list.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'brendlər': brendlər,
        'markalar': markalar
    })


@login_required
def sebetden_sil(request, sebet_id):
    # Sebetdən məhsulu silmək
    try:
        sebet_item = Sebet.objects.get(id=sebet_id, user=request.user)
        sebet_item.delete()
    except Sebet.DoesNotExist:
        # Əgər səbət elementi tapılmasa, heç bir əməliyyat etməyin
        pass

    # İstifadəçini əvvəlki səhifəyə yönləndirmək
    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))

@login_required
def sifarisi_gonder(request):
    if request.method == "POST":
        # Yeni sifarişi yarat
        sifaris = Sifaris.objects.create(

            user=request.user,
            cemi_mebleg=0,
        )

        # Səbətdəki məhsulları götür
        sebet = Sebet.objects.filter(user=request.user)  # istifadəçi əsaslı

        # Məhsul və miqdarları sifarişə əlavə et
        for item in sebet:
            SifarisMehsul.objects.create(
                sifaris=sifaris,
                mehsul=item.mehsul,
                miqdar=item.miqdar,
                qiymet=item.mehsul.qiymet
            )
            sifaris.cemi_mebleg += item.mehsul.qiymet * item.miqdar  # Məbləği hesabla
            sifaris.save()

        # Səbəti təmizləyin (isteğe bağlı)
        sebet.delete()

        # Sifarişi tamamla
        sifaris.status = 'Tamamlanıb'  # Tamamlandığını göstər
        sifaris.save()

       # Admin panelinə yönləndirin

    return redirect('products_list')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sifaris

@login_required
def sifaris_izle(request):
    sifarisler = Sifaris.objects.filter(user=request.user)

    toplam_mebleg = sum(sifaris.cemi_mebleg for sifaris in sifarisler)
    odenilen_mebleg = sum(sifaris.odenilen_mebleg for sifaris in sifarisler)
    qaliq_borc = toplam_mebleg - odenilen_mebleg

    status_text = {
        'gozleyir': 'Gözləyir',
        'hazirlanir': 'Hazırlanır',
        'yoldadir': 'Yoldadır',
        'catdirildi': 'Çatdırıldı'
    }

    # Hər sifarişə status əlavə edirik
    for sifaris in sifarisler:
        sifaris.display_status = status_text.get(sifaris.status, 'Gözləyir')

    return render(request, 'sifaris_izleme.html', {
        'sifarisler': sifarisler,
        'toplam_mebleg': toplam_mebleg,
        'odenilen_mebleg': odenilen_mebleg,
        'qaliq_borc': qaliq_borc,
    })


@login_required
def get_cart_count(request):
    # İstifadəçinin səbətini alır və məhsul sayını hesablayır
    sebet = Sebet.objects.filter(user=request.user)
    count = sebet.count()
    return JsonResponse({'count': count})

@csrf_exempt
def update_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('id')
        action = data.get('action')

        try:
            cart_item = Sebet.objects.get(id=product_id)  # `Sebet` sizin səbət modelinizdir
            if action == 'increase':
                cart_item.miqdar += 1
            elif action == 'decrease' and cart_item.miqdar > 1:
                cart_item.miqdar -= 1
            cart_item.save()

            return JsonResponse({'success': True, 'new_quantity': cart_item.miqdar})
        except Sebet.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Məhsul tapılmadı.'})
    return JsonResponse({'success': False, 'error': 'Düzgün sorğu deyil.'})