from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Kateqoriya, Sifaris, SifarisItem, Firma, Avtomobil, PopupImage
from django.db.models import Q
from decimal import Decimal
from django.contrib import messages
import re
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models.functions import Lower
from django.db.models import Value
from functools import reduce
from operator import and_, or_

def normalize_azerbaijani_chars(text):
    # Azərbaycan hərflərinin qarşılıqlı çevrilməsi
    char_map = {
        'ə': 'e', 'e': 'ə', 'Ə': 'E', 'E': 'Ə',
        'ö': 'o', 'o': 'ö', 'Ö': 'O', 'O': 'Ö',
        'ğ': 'g', 'g': 'ğ', 'Ğ': 'G', 'G': 'Ğ',
        'ı': 'i', 'i': 'ı', 'I': 'İ', 'İ': 'I',
        'ü': 'u', 'u': 'ü', 'Ü': 'U', 'U': 'Ü',
        'ş': 's', 's': 'ş', 'Ş': 'S', 'S': 'Ş',
        'ç': 'c', 'c': 'ç', 'Ç': 'C', 'C': 'Ç'
    }
    
    # Orijinal mətni saxla
    variations = {text}
    
    # Kiçik hərflərlə variant
    lower_text = text.lower()
    variations.add(lower_text)
    
    # Böyük hərflərlə variant
    upper_text = text.upper()
    variations.add(upper_text)
    
    # Hər bir variant üçün qarşılıqlı çevirmələr
    all_variations = set()
    for variant in variations:
        current_variations = {variant}
        for char in variant:
            if char in char_map:
                new_variations = set()
                for v in current_variations:
                    new_variations.add(v.replace(char, char_map[char]))
                current_variations.update(new_variations)
        all_variations.update(current_variations)
    
    return all_variations

def custom_404(request, exception=None):
    return HttpResponseNotFound(render(request, '404.html').content)

def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('base')
        else:
            error_message = 'İstifadeçi adı və ya şifrə yanlışdır'
    return render(request, 'login.html', {'error_message': error_message})

@login_required
def home_view(request):
    # Yeni məhsulları əldə et
    new_products = Mehsul.objects.filter(yenidir=True)
    # Aktiv popup şəkilləri əldə et
    popup_images = PopupImage.objects.filter(aktiv=True)
    return render(request, 'base.html', {
        'new_products': new_products,
        'popup_images': popup_images
    })

@login_required
def products_view(request):
    search_query = request.GET.get('search', '')
    kateqoriya = request.GET.get('kateqoriya', '')
    firma = request.GET.get('firma', '')
    avtomobil = request.GET.get('avtomobil', '')
    
    mehsullar = Mehsul.objects.all().order_by('-id')
    popup_images = PopupImage.objects.filter(aktiv=True)
    
    if search_query:
        # Kodlarla axtarış üçün əvvəlki təmizləmə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        
        # İki ayrı filter tətbiq edək
        if clean_search:
            # Kod ilə axtarış
            kod_filter = Q(kodlar__icontains=clean_search)
            
            # Ad ilə təkmilləşdirilmiş axtarış
            # Çoxlu boşluq və təbləri tək boşluğa çeviririk
            processed_query = re.sub(r'\s+', ' ', search_query).strip()
            
            # Axtarış sözlərini ayırırıq
            search_words = processed_query.split()
            
            if search_words:
                # Hər bir söz üçün bütün mümkün variantları yarat
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                
                # "AND" operatoru ilə birləşdiririk - bütün sözlər olmalıdır
                ad_filter = reduce(and_, ad_filters)
                
                # Kod və ad filterini "OR" operatoru ilə birləşdiririk
                mehsullar = mehsullar.filter(kod_filter | ad_filter)
            else:
                # Əgər heç bir söz yoxdursa, yalnız kod ilə axtarış
                mehsullar = mehsullar.filter(kod_filter)
    
    if kateqoriya:
        mehsullar = mehsullar.filter(kateqoriya__adi=kateqoriya)
        
    if firma:
        mehsullar = mehsullar.filter(firma__adi=firma)
        
    if avtomobil:
        mehsullar = mehsullar.filter(avtomobil__adi=avtomobil)
    
    # İlk 15 məhsulu götür
    initial_products = mehsullar[:15]
    has_more = mehsullar.count() > 15
    
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    
    return render(request, 'products.html', {
        'mehsullar': initial_products,
        'has_more': has_more,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
        'search_query': search_query,
        'selected_kateqoriya': kateqoriya,
        'selected_firma': firma,
        'selected_avtomobil': avtomobil,
        'popup_images': popup_images
    })

@login_required
def load_more_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 15
    search_query = request.GET.get('search', '')
    kateqoriya = request.GET.get('kateqoriya', '')
    firma = request.GET.get('firma', '')
    avtomobil = request.GET.get('avtomobil', '')
    
    mehsullar = Mehsul.objects.all().order_by('-id')
    
    if search_query:
        # Kodlarla axtarış üçün əvvəlki təmizləmə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        
        # İki ayrı filter tətbiq edək
        if clean_search:
            # Kod ilə axtarış
            kod_filter = Q(kodlar__icontains=clean_search)
            
            # Ad ilə təkmilləşdirilmiş axtarış
            # Çoxlu boşluq və təbləri tək boşluğa çeviririk
            processed_query = re.sub(r'\s+', ' ', search_query).strip()
            
            # Axtarış sözlərini ayırırıq
            search_words = processed_query.split()
            
            if search_words:
                # Hər bir söz məhsulun adında olmalıdır (sıradan asılı olmayaraq)
                ad_filters = []
                for word in search_words:
                    ad_filters.append(Q(adi__icontains=word))
                
                # "AND" operatoru ilə birləşdiririk - bütün sözlər olmalıdır
                ad_filter = reduce(and_, ad_filters)
                
                # Kod və ad filterini "OR" operatoru ilə birləşdiririk
                mehsullar = mehsullar.filter(kod_filter | ad_filter)
            else:
                # Əgər heç bir söz yoxdursa, yalnız kod ilə axtarış
                mehsullar = mehsullar.filter(kod_filter)
    
    if kateqoriya:
        mehsullar = mehsullar.filter(kateqoriya__adi=kateqoriya)
        
    if firma:
        mehsullar = mehsullar.filter(firma__adi=firma)
        
    if avtomobil:
        mehsullar = mehsullar.filter(avtomobil__adi=avtomobil)
    
    # Get next batch of products
    products = mehsullar[offset:offset + limit]
    has_more = mehsullar.count() > (offset + limit)
    
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'adi': product.adi,
            'sekil_url': product.sekil.url if product.sekil else None,
            'firma': product.firma.adi,
            'brend_kod': product.brend_kod,
            'oem': product.oem,
            'stok': product.stok,
            'qiymet': str(product.qiymet),
            'yenidir': product.yenidir,
        })
    
    return JsonResponse({
        'products': products_data,
        'has_more': has_more
    })

@login_required
def cart_view(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    cart_items = []
    total = Decimal('0.00')
    popup_images = PopupImage.objects.filter(aktiv=True)
    invalid_products = []  # Mövcud olmayan məhsulları izləmək üçün
    
    for product_id, quantity in cart.items():
        try:
            product = Mehsul.objects.get(id=product_id)
            subtotal = product.qiymet * Decimal(str(quantity))
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total += subtotal
        except Mehsul.DoesNotExist:
            invalid_products.append(product_id)  # Mövcud olmayan məhsulu qeyd et
    
    # Mövcud olmayan məhsulları səbətdən sil
    if invalid_products:
        for product_id in invalid_products:
            if str(product_id) in cart:
                del cart[str(product_id)]
        request.session.modified = True
        messages.warning(request, 'Bəzi məhsullar artıq mövcud olmadığı üçün səbətdən silindi.')
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'popup_images': popup_images
    })

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Mehsul, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        response_data = {
            'status': 'error',
            'message': ''
        }
        
        if quantity > product.stok:
            response_data['message'] = f'{product.adi} məhsulundan stokda yalnız {product.stok} ədəd var!'
            return JsonResponse(response_data)
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        cart = request.session['cart']
        current_quantity = cart.get(str(product_id), 0)
        new_quantity = current_quantity + quantity
        
        if new_quantity > product.stok:
            response_data['message'] = f'{product.adi} məhsulundan stokda yalnız {product.stok} ədəd var!'
            return JsonResponse(response_data)
        
        cart[str(product_id)] = new_quantity
        request.session['cart'] = cart
        request.session.modified = True
        
        response_data.update({
            'status': 'success',
            'message': f'{product.adi} məhsulundan {quantity} ədəd səbətə əlavə edildi!',
            'cart_count': len(cart)
        })
        
        return JsonResponse(response_data)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        if 'cart' in request.session:
            cart = request.session['cart']
            if str(product_id) in cart:
                del cart[str(product_id)]
                request.session.modified = True
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Məhsul səbətdən silindi!',
                    'cart_count': len(cart)
                })
    
        return JsonResponse({
            'status': 'error',
            'message': 'Məhsul tapılmadı!'
        })
        
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def orders_view(request):
    orders = Sifaris.objects.filter(istifadeci=request.user).order_by('-tarix')
    statistics = Sifaris.get_order_statistics(request.user)
    popup_images = PopupImage.objects.filter(aktiv=True)
    
    return render(request, 'orders.html', {
        'orders': orders,
        'statistics': statistics,
        'popup_images': popup_images
    })

@login_required
def checkout(request):
    if request.method == 'POST':
        if 'cart' not in request.session or not request.session['cart']:
            messages.error(request, 'Səbətiniz boşdur.')
            return redirect('cart')

        # Seçilmiş məhsulları al
        selected_items = request.POST.getlist('selected_items[]')
        catdirilma_usulu = request.POST.get('catdirilma_usulu')
        
        if not selected_items:
            messages.error(request, 'Zəhmət olmasa ən azı bir məhsul seçin.')
            return redirect('cart')
            
        if not catdirilma_usulu:
            messages.error(request, 'Zəhmət olmasa çatdırılma üsulunu seçin.')
            return redirect('cart')

        cart = request.session['cart']
        total = Decimal('0.00')
        order_items = []
        remaining_cart = {}  # Seçilməmiş məhsullar üçün

        # Məhsulları və ümumi məbləği hesablayırıq
        for product_id, quantity in cart.items():
            if product_id in selected_items:
                product = get_object_or_404(Mehsul, id=product_id)
                if product.stok < quantity:
                    messages.error(request, f'{product.adi} məhsulundan kifayət qədər stok yoxdur.')
                    return redirect('cart')
                
                subtotal = product.qiymet * Decimal(str(quantity))
                total += subtotal
                order_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.qiymet
                })
            else:
                # Seçilməmiş məhsulları yeni səbətə əlavə et
                remaining_cart[product_id] = quantity

        try:
            # Sifariş yaradırıq
            order = Sifaris.objects.create(
                istifadeci=request.user,
                umumi_mebleg=total,
                catdirilma_usulu=catdirilma_usulu
            )

            # Sifariş elementlərini yaradırıq
            for item in order_items:
                SifarisItem.objects.create(
                    sifaris=order,
                    mehsul=item['product'],
                    miqdar=item['quantity'],
                    qiymet=item['price']
                )

            # Səbəti yeniləyirik (yalnız seçilməmiş məhsulları saxlayırıq)
            request.session['cart'] = remaining_cart
            request.session.modified = True
            
            messages.success(request, 'Sifarişiniz uğurla yaradıldı.')
            return redirect('orders')
            
        except Exception as e:
            if 'order' in locals():
                order.delete()
            messages.error(request, 'Sifariş yaradılarkən xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
            return redirect('cart')

    return redirect('cart')

@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Mehsul, id=product_id)
            quantity = int(request.POST.get('quantity', 1))
            
            if quantity > product.stok:
                messages.error(request, f'{product.adi} məhsulundan stokda yalnız {product.stok} ədəd var!')
                return redirect('cart')
            
            if quantity < 1:
                messages.error(request, 'Miqdar 1-dən az ola bilməz!')
                return redirect('cart')
            
            cart = request.session.get('cart', {})
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            
            messages.success(request, f'{product.adi} məhsulunun miqdarı yeniləndi!')
            return redirect('cart')
            
        except ValueError:
            messages.error(request, 'Yanlış miqdar daxil edildi!')
            return redirect('cart')
        except Exception as e:
            messages.error(request, 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
            return redirect('cart')
    
    return redirect('cart')

@login_required
def order_detail_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    order = get_object_or_404(Sifaris, id=order_id, istifadeci=request.user)
    popup_images = PopupImage.objects.filter(aktiv=True)
    
    return render(request, 'order_detail.html', {
        'order': order,
        'popup_images': popup_images
    })

@login_required
def search_suggestions(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Kodlarla axtarış üçün əvvəlki təmizləmə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        
        if clean_search:
            # Kod ilə axtarış
            kod_filter = Q(kodlar__icontains=clean_search)
            
            # Ad ilə təkmilləşdirilmiş axtarış
            # Çoxlu boşluq və təbləri tək boşluğa çeviririk
            processed_query = re.sub(r'\s+', ' ', search_query).strip()
            
            # Axtarış sözlərini ayırırıq
            search_words = processed_query.split()
            
            if search_words:
                # Hər bir söz üçün bütün mümkün variantları yarat
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                
                # "AND" operatoru ilə birləşdiririk - bütün sözlər olmalıdır
                ad_filter = reduce(and_, ad_filters)
                
                # Kod və ad filterini "OR" operatoru ilə birləşdiririk
                mehsullar = Mehsul.objects.filter(kod_filter | ad_filter)[:5]
            else:
                # Əgər heç bir söz yoxdursa, yalnız kod ilə axtarış
                mehsullar = Mehsul.objects.filter(kod_filter)[:5]
            
            suggestions = []
            for mehsul in mehsullar:
                suggestions.append({
                    'id': mehsul.id,
                    'adi': mehsul.adi,
                    'brend_kod': mehsul.brend_kod,
                    'oem': mehsul.oem,
                    'qiymet': str(mehsul.qiymet),
                    'sekil_url': mehsul.sekil.url if mehsul.sekil else None,
                })
            return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'suggestions': []})

@login_required
def new_products_view(request):
    # Yeni məhsulları əldə et
    mehsullar = Mehsul.objects.filter(yenidir=True).order_by('-id')  # Ən son əlavə edilən yeni məhsullardan başla
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    popup_images = PopupImage.objects.filter(aktiv=True)
    
    return render(request, 'new_products.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
        'popup_images': popup_images
    })

@login_required
def logout_view(request):
    logout(request)
    # Sessiya və keşi təmizləyirik
    request.session.flush()
    
    # İstifadəçini login səhifəsinə yönləndiririk
    return redirect('login')

@login_required
def get_cart_items(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = request.session.get('cart', {})
        items = []
        total = Decimal('0.00')
        
        for product_id, quantity in cart.items():
            try:
                product = Mehsul.objects.get(id=product_id)
                subtotal = product.qiymet * Decimal(str(quantity))
                items.append({
                    'id': product.id,
                    'name': product.adi,
                    'image': product.sekil.url if product.sekil else None,
                    'price': str(product.qiymet),
                    'quantity': quantity,
                    'subtotal': str(subtotal)
                })
                total += subtotal
            except Mehsul.DoesNotExist:
                continue
        
        return JsonResponse({
            'items': items,
            'total': str(total)
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)