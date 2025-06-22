from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Kateqoriya, Sifaris, SifarisItem, Firma, Avtomobil, PopupImage, Header_Message, Vitrin
from django.db.models import Q, Sum, F, Case, When, DecimalField
from decimal import Decimal
from django.contrib import messages
import re
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from django.db.models.functions import Lower
from django.db.models import Value
from functools import reduce
from operator import and_, or_
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.views.decorators.http import require_http_methods
from .forms import MehsulForm, SifarisEditForm, SifarisItemEditForm
import pandas as pd
from django.db import transaction
import math
from django.forms import inlineformset_factory

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
            # Profil təsdiqlənmə yoxlaması
            if not user.profile.is_verified:
                error_message = 'Giriş üçün icazəniz yoxdur !'
                return render(request, 'login.html', {'error_message': error_message})
            
            login(request, user)
            return redirect('base')
        else:
            error_message = 'İstifadəçi adı və ya şifrə yanlışdır'
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
            # Kod və ölçü ilə axtarış
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            
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
                
                # Kod, ölçü və ad filterini "OR" operatoru ilə birləşdiririk
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | ad_filter)
            else:
                # Əgər heç bir söz yoxdursa, yalnız kod və ölçü ilə axtarış
                mehsullar = mehsullar.filter(kod_filter | olcu_filter)
    
    if kateqoriya:
        mehsullar = mehsullar.filter(kateqoriya__adi=kateqoriya)
        
    if firma:
        mehsullar = mehsullar.filter(firma__adi=firma)
        
    if avtomobil:
        mehsullar = mehsullar.filter(avtomobil__adi=avtomobil)
    
    # İlk 5 məhsulu götür
    initial_products = mehsullar[:5]
    has_more = mehsullar.count() > 5
    
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
    limit = 5
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
            'sahib_id': product.sahib.id if product.sahib else None,
            'sahib_username': product.sahib.username if product.sahib else 'AS-AVTO',
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
            
            response_data = {
                'status': 'error',
                'message': ''
            }
            
            if quantity > product.stok:
                response_data['message'] = f'{product.adi} məhsulundan stokda yalnız {product.stok} ədəd var!'
                return JsonResponse(response_data)
            
            if quantity < 1:
                response_data['message'] = 'Miqdar 1-dən az ola bilməz!'
                return JsonResponse(response_data)
            
            cart = request.session.get('cart', {})
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            
            # Calculate new subtotal and cart total
            subtotal = product.qiymet * quantity
            cart_total = sum(
                Mehsul.objects.get(id=int(pid)).qiymet * qty
                for pid, qty in cart.items()
            )
            
            response_data.update({
                'status': 'success',
                'message': f'{product.adi} məhsulunun miqdarı yeniləndi!',
                'subtotal': f'{subtotal} ₼',
                'cart_total': f'{cart_total} ₼'
            })
            
            return JsonResponse(response_data)
            
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Yanlış miqdar daxil edildi!'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

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
            # Kod və ölçü ilə axtarış
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            
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
                
                # Kod, ölçü və ad filterini "OR" operatoru ilə birləşdiririk
                mehsullar = Mehsul.objects.filter(kod_filter | olcu_filter | ad_filter)[:5]
            else:
                # Əgər heç bir söz yoxdursa, yalnız kod və ölçü ilə axtarış
                mehsullar = Mehsul.objects.filter(kod_filter | olcu_filter)[:5]
            
            suggestions = []
            for mehsul in mehsullar:
                suggestions.append({
                    'id': mehsul.id,
                    'adi': mehsul.adi,
                    'brend_kod': mehsul.brend_kod,
                    'oem': mehsul.oem,
                    'olcu': mehsul.olcu,
                    'qiymet': str(mehsul.qiymet),
                    'sekil_url': mehsul.sekil.url if mehsul.sekil else None,
                })
            return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'suggestions': []})

@login_required
def new_products_view(request):
    # Yeni məhsulları əldə et
    mehsullar = Mehsul.objects.filter(yenidir=True).order_by('-id')  # Ən son əlavə edilən yeni məhsullardan başla
    
    # İlk 5 məhsulu götür
    initial_products = mehsullar[:5]
    has_more = mehsullar.count() > 5
    
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    popup_images = PopupImage.objects.filter(aktiv=True)
    
    return render(request, 'new_products.html', {
        'mehsullar': initial_products,
        'has_more': has_more,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
        'popup_images': popup_images
    })

@login_required
def load_more_new_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 5
    
    mehsullar = Mehsul.objects.filter(yenidir=True).order_by('-id')
    
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
            'sahib_id': product.sahib.id if product.sahib else None,
            'sahib_username': product.sahib.username if product.sahib else 'AS-AVTO',
        })
    
    return JsonResponse({
        'products': products_data,
        'has_more': has_more
    })

@login_required
def logout_view(request):
    logout(request)
    # Sessiya və keşi təmizləyirik
    request.session.flush()
    
    # İstifadəçini login səhifəsinə yönləndiririk
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        
        # Username validasiyası
        if not username:
            messages.error(request, 'İstifadəçi adı boş ola bilməz!')
            return render(request, 'register.html')
            
        # Username formatı yoxlaması
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            messages.error(request, 'İstifadəçi adı yalnız ingilis hərfləri, rəqəmlər və _ simvolundan ibarət ola bilər!')
            return render(request, 'register.html')
            
        # Şifrə validasiyası
        if len(password) < 8:
            messages.error(request, 'Şifrə minimum 8 simvol olmalıdır!')
            return render(request, 'register.html')
            
        # Telefon nömrəsi validasiyası
        if not phone.startswith('+994'):
            messages.error(request, 'Telefon nömrəsi +994 ilə başlamalıdır!')
            return render(request, 'register.html')
            
        # Unvan validasiyası
        if not address:
            messages.error(request, 'Ünvan boş ola bilməz!')
            return render(request, 'register.html')
            
        # Username mövcudluğu yoxlaması
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu istifadəçi adı artıq mövcuddur!')
            return render(request, 'register.html')
            
        # Telefon nömrəsi mövcudluğu yoxlaması
        if User.objects.filter(profile__phone=phone).exists():
            messages.error(request, 'Bu telefon nömrəsi artıq qeydiyyatdan keçirilib!')
            return render(request, 'register.html')
            
        try:
            # Yeni istifadəçi yaradırıq
            user = User.objects.create_user(username=username, password=password)
            
            # Profil məlumatlarını əlavə edirik
            user.profile.phone = phone
            user.profile.address = address
            user.profile.is_verified = False  # Profil təsdiqlənməmiş olaraq yaradılır
            user.profile.save()
            
            messages.success(request, 'Qeydiyyat uğurla tamamlandı!')
            return redirect('register')
            
        except Exception as e:
            messages.error(request, 'Qeydiyyat zamanı xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
            return render(request, 'register.html')
            
    return render(request, 'register.html')

@require_http_methods(["GET"])
def product_details(request, product_id):
    try:
        product = Mehsul.objects.get(id=product_id)
        data = {
            'status': 'success',
            'product': {
                'id': product.id,
                'adi': product.adi,
                'kateqoriya': product.kateqoriya.adi if product.kateqoriya else None,
                'firma': product.firma.adi,
                'avtomobil': product.avtomobil.adi,
                'brend_kod': product.brend_kod,
                'oem': product.oem,
                'olcu': product.olcu,
                'qiymet': str(product.qiymet),
                'stok': product.stok,
                'melumat': product.melumat,
                'sekil_url': product.sekil.url if product.sekil else None,
            }
        }
    except Mehsul.DoesNotExist:
        data = {
            'status': 'error',
            'message': 'Məhsul tapılmadı.'
        }
    except Exception as e:
        data = {
            'status': 'error',
            'message': 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'
        }
    
    return JsonResponse(data)

@login_required
def my_products_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu səhifəyə giriş üçün icazəniz yoxdur.')
        return redirect('base')
    
    mehsullar = Mehsul.objects.filter(sahib=request.user).order_by('-id')
    return render(request, 'my_products.html', {'mehsullar': mehsullar})

@login_required
def my_sales_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu səhifəyə giriş üçün icazəniz yoxdur.')
        return redirect('base')

    # İstifadəçinin məhsullarının olduğu sifarişləri tap və təkrarlanmanın qarşısını al
    orders = Sifaris.objects.filter(sifarisitem__mehsul__sahib=request.user).distinct().order_by('-tarix')

    # Bu sifarişlər əsasında statistikaları hesabla
    stats_data = orders.aggregate(
        total_amount=Sum('umumi_mebleg'),
        total_paid=Sum('odenilen_mebleg')
    )
    
    total_amount = stats_data.get('total_amount') or 0
    total_paid = stats_data.get('total_paid') or 0

    stats = {
        'total_orders': orders.count(),
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_debt': total_amount - total_paid
    }

    context = {
        'orders': orders,
        'stats': stats
    }
    return render(request, 'my_sales.html', context)

@login_required
def edit_my_sale_view(request, order_id):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu səhifəyə giriş üçün icazəniz yoxdur.')
        return redirect('my_sales')

    order = get_object_or_404(Sifaris, id=order_id)
    # Yalnız həmin satıcıya aid məhsulları olan sifarişlərə baxmaq üçün yoxlama
    if not SifarisItem.objects.filter(sifaris=order, mehsul__sahib=request.user).exists():
        messages.error(request, 'Bu sifarişi redaktə etmək üçün icazəniz yoxdur.')
        return redirect('my_sales')

    # Sifarişin öz məhsulları üçün formset yarat
    SifarisItemFormSet = inlineformset_factory(
        Sifaris, 
        SifarisItem, 
        form=SifarisItemEditForm, 
        extra=0, 
        can_delete=False
    )
    
    # Formset-ə yalnız satıcının öz məhsullarını daxil et
    queryset = order.sifarisitem_set.filter(mehsul__sahib=request.user)

    if request.method == 'POST':
        form = SifarisEditForm(request.POST, instance=order)
        formset = SifarisItemFormSet(request.POST, instance=order, queryset=queryset)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            order.update_total() # Formset save olanda onsuz da total update olur, amma zəmanət üçün
            messages.success(request, f"Sifariş #{order.id} uğurla yeniləndi.")
            return redirect('edit_my_sale', order_id=order.id)
        else:
            messages.error(request, "Zəhmət olmasa xətaları düzəldin.")

    else:
        form = SifarisEditForm(instance=order)
        formset = SifarisItemFormSet(instance=order, queryset=queryset)

    context = {
        'order': order,
        'form': form,
        'formset': formset,
        'order_items': order.sifarisitem_set.filter(mehsul__sahib=request.user) # Yalnız bu istifadəçiyə aid məhsullar
    }
    return render(request, 'edit_my_sale.html', context)

@login_required
def add_edit_product_view(request, product_id=None):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu əməliyyatı etmək üçün icazəniz yoxdur.')
        return redirect('my_products')

    if product_id:
        mehsul = get_object_or_404(Mehsul, id=product_id)
        if mehsul.sahib != request.user:
            messages.error(request, 'Bu məhsulu redaktə etmək üçün icazəniz yoxdur.')
            return redirect('my_products')
    else:
        mehsul = None

    if request.method == 'POST':
        form = MehsulForm(request.POST, request.FILES, instance=mehsul)
        if form.is_valid():
            yeni_mehsul = form.save(commit=False)
            yeni_mehsul.sahib = request.user
            yeni_mehsul.save()
            messages.success(request, f'Məhsul uğurla {"yeniləndi" if mehsul else "əlavə edildi"}.')
            return redirect('my_products')
    else:
        form = MehsulForm(instance=mehsul)

    return render(request, 'add_edit_product.html', {'form': form})

@login_required
def delete_product_view(request, product_id):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu əməliyyatı etmək üçün icazəniz yoxdur.')
        return redirect('my_products')

    mehsul = get_object_or_404(Mehsul, id=product_id)
    if mehsul.sahib != request.user:
        messages.error(request, 'Bu məhsulu silmək üçün icazəniz yoxdur.')
        return redirect('my_products')
    
    mehsul.delete()
    messages.success(request, 'Məhsul uğurla silindi.')
    return redirect('my_products')

@require_http_methods(["GET"])
def user_details_view(request, user_id):
    try:
        user = User.objects.select_related('profile').get(id=user_id)
        data = {
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'phone': user.profile.phone,
                'address': user.profile.address,
            }
        }
    except User.DoesNotExist:
        data = {
            'status': 'error',
            'message': 'İstifadəçi tapılmadı.'
        }
    except Exception as e:
        data = {
            'status': 'error',
            'message': 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'
        }
    
    return JsonResponse(data)

@login_required
@transaction.atomic
def import_user_products_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, "Bu əməliyyatı etmək üçün icazəniz yoxdur.")
        return redirect('my_products')

    if request.method == 'POST':
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            messages.error(request, 'Zəhmət olmasa Excel faylı seçin')
            return redirect('my_products')
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Yalnız .xlsx faylları qəbul edilir')
            return redirect('my_products')
            
        try:
            df = pd.read_excel(excel_file)
            
            new_count = 0
            update_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    row = {str(k).strip().lower(): v for k, v in row.items()}
                    
                    kateqoriya = None
                    firma = None
                    avtomobil = None
                    vitrin = None
                    
                    if 'kateqoriya' in row and pd.notna(row['kateqoriya']):
                        kateqoriya, _ = Kateqoriya.objects.get_or_create(adi=str(row['kateqoriya']).strip())
                    
                    if 'firma' in row and pd.notna(row['firma']):
                        firma, _ = Firma.objects.get_or_create(adi=str(row['firma']).strip())
                    
                    if 'avtomobil' in row and pd.notna(row['avtomobil']):
                        avtomobil, _ = Avtomobil.objects.get_or_create(adi=str(row['avtomobil']).strip())

                    if 'vitrin' in row and pd.notna(row['vitrin']):
                        vitrin, _ = Vitrin.objects.get_or_create(nomre=str(row['vitrin']).strip())

                    if 'adi' not in row or pd.isna(row['adi']):
                        messages.error(request, f'Sətir {index + 2}: Məhsulun adı boşdur.', level=messages.ERROR)
                        error_count += 1
                        continue

                    temiz_ad = str(row['adi']).strip()
                    temiz_ad = ' '.join(temiz_ad.split())

                    brend_kod = None
                    if 'brend_kod' in row and pd.notna(row['brend_kod']):
                        value = row['brend_kod']
                        if isinstance(value, float) and math.isnan(value):
                            brend_kod = None
                        else:
                            brend_kod = str(value).strip()
                            if brend_kod.lower() == 'nan' or brend_kod == '':
                                brend_kod = None

                    if not brend_kod:
                        messages.error(request, f'Sətir {index + 2}: Brend kodu boşdur.', level=messages.ERROR)
                        error_count += 1
                        continue

                    existing_product = Mehsul.objects.filter(brend_kod=brend_kod, sahib=request.user).first()

                    if existing_product:
                        # Sahib onsuz da request.user olduğu üçün bu yoxlamaya ehtiyac yoxdur.
                        # Mövcud məhsulu yeniləyirik.
                        existing_product.adi = temiz_ad
                        existing_product.kateqoriya = kateqoriya
                        existing_product.firma = firma
                        existing_product.avtomobil = avtomobil
                        existing_product.vitrin = vitrin
                        existing_product.olcu = str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else ''
                        existing_product.maya_qiymet = float(row['maya_qiymet']) if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0
                        existing_product.qiymet = float(row['qiymet']) if 'qiymet' in row and pd.notna(row['qiymet']) else 0
                        existing_product.stok = int(row['stok']) if 'stok' in row and pd.notna(row['stok']) else 0
                        existing_product.kodlar = str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else ''
                        existing_product.melumat = str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else ''
                        
                        existing_product.save()
                        update_count += 1
                    else:
                        # Yeni məhsul yaradırıq
                        mehsul_data = {
                            'adi': temiz_ad,
                            'sahib': request.user,
                            'kateqoriya': kateqoriya,
                            'firma': firma,
                            'avtomobil': avtomobil,
                            'vitrin': vitrin,
                            'brend_kod': brend_kod,
                            'oem': '',
                            'olcu': str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else '',
                            'maya_qiymet': float(row['maya_qiymet']) if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0,
                            'qiymet': float(row['qiymet']) if 'qiymet' in row and pd.notna(row['qiymet']) else 0,
                            'stok': int(row['stok']) if 'stok' in row and pd.notna(row['stok']) else 0,
                            'kodlar': str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else '',
                            'melumat': str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else '',
                            'yenidir': False
                        }
                        Mehsul.objects.create(**mehsul_data)
                        new_count += 1

                except Exception as e:
                    messages.error(request, f'Sətir {index + 2} emal edilərkən xəta baş verdi: {e}', level=messages.ERROR)
                    error_count += 1
                    continue
            
            success_message = f"Excel faylı uğurla import edildi! "
            if new_count > 0:
                success_message += f"{new_count} yeni məhsul əlavə edildi. "
            if update_count > 0:
                success_message += f"{update_count} məhsul yeniləndi. "
            
            if error_count > 0:
                messages.warning(request, f"{error_count} sətirdə xəta baş verdi.")
            
            if new_count > 0 or update_count > 0:
                messages.success(request, success_message)
            elif error_count == 0:
                messages.info(request, "Faylda heç bir dəyişiklik edilmədi.")

        except Exception as e:
            messages.error(request, f'Excel faylı oxunarkən xəta: {e}', level=messages.ERROR)
        
        return redirect('my_products')
    
    return redirect('my_products')