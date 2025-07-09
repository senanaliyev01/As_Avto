from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Kateqoriya, Sifaris, SifarisItem, Firma, Avtomobil, PopupImage, Header_Message, Vitrin, ProductLike, ProductRating
from django.db.models import Q, Sum, F, Case, When, DecimalField, Avg
from decimal import Decimal
from django.contrib import messages
import re
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseRedirect, FileResponse, Http404, HttpResponse
from django.db.models.functions import Lower
from django.db.models import Value
from functools import reduce
from operator import and_, or_
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.views.decorators.http import require_http_methods, require_POST
from .forms import MehsulForm, SifarisEditForm, SifarisItemEditForm
import pandas as pd
from django.db import transaction
import math
from django.forms import inlineformset_factory
from collections import defaultdict
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Concat
from django.db.models import CharField
from django.db import models

def truncate_product_name(name, max_length=20):
    """Məhsul adını qısaldır və uzun olarsa ... əlavə edir"""
    if len(name) <= max_length:
        return name
    return name[:max_length-3] + "..."

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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'İstifadəçi adı və ya şifrə yanlışdır'})
    return redirect('base')


def home_view(request):
    # Yeni məhsulları əldə et
    new_products = Mehsul.objects.filter(yenidir=True).order_by('-id')
    # Aktiv popup şəkilləri əldə et
    popup_images = PopupImage.objects.filter(aktiv=True)
    return render(request, 'base.html', {
        'new_products': new_products,
        'popup_images': popup_images
    })


def products_view(request):
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.all().order_by('-id')
    popup_images = PopupImage.objects.filter(aktiv=True)
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            def clean_code(val):
                return re.sub(r'[^a-zA-Z0-9]', '', val.lower()) if val else ''
            brend_kod_ids = [m.id for m in Mehsul.objects.all() if clean_code(search_query) in clean_code(m.brend_kod)]
            brend_kod_filter = Q(id__in=brend_kod_ids)
            if search_words:
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                ad_filter = reduce(and_, ad_filters)
                # search_text üçün AND və AZ variantları ilə
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter | ad_filter | searchtext_and_filter).order_by('-id')
            else:
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter).order_by('-id')
    initial_products = mehsullar[:5]
    has_more = mehsullar.count() > 5
    # Hər məhsul üçün ortalama reytinq və bəyənmə sayı əlavə et
    for m in initial_products:
        m.avg_rating = m.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        m.like_count = m.likes.count()
    return render(request, 'products.html', {
        'mehsullar': initial_products,
        'has_more': has_more,
        'search_query': search_query,
        'popup_images': popup_images
    })


def load_more_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 5
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.all().order_by('-id')
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            brend_kod_filter = Q(brend_kod__icontains=search_query)
            if search_words:
                ad_filters = []
                for word in search_words:
                    ad_filters.append(Q(adi__icontains=word))
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | brend_kod_filter | ad_filter | searchtext_and_filter).order_by('-id')
            else:
                mehsullar = mehsullar.filter(kod_filter | brend_kod_filter).order_by('-id')
    products = mehsullar[offset:offset + limit]
    has_more = mehsullar.count() > (offset + limit)
    products_data = []
    for product in products:
        avg_rating = product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        like_count = product.likes.count()
        products_data.append({
            'id': product.id,
            'adi': product.adi,
            'sekil_url': product.sekil.url if product.sekil else None,
            'firma': product.firma.adi,
            'firma_logo_url': product.firma.logo.url if product.firma and product.firma.logo else '',
            'avtomobil': product.avtomobil.adi if product.avtomobil else '',
            'avtomobil_logo_urls': [logo.sekil.url for logo in product.avtomobil.logolar.all()],
            'brend_kod': product.brend_kod,
            'oem': product.oem,
            'stok': product.stok,
            'qiymet': str(product.qiymet),
            'yenidir': product.yenidir,
            'sahib_id': product.sahib.id if product.sahib else None,
            'sahib_username': product.sahib.username if product.sahib else 'AS-AVTO',
            'avg_rating': avg_rating,
            'like_count': like_count,
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
        remaining_cart = {}  # Seçilməmiş məhsullar üçün
        order_items_by_seller = {}
        errors = []

        # Məhsulları satıcıya görə qruplaşdırırıq
        for product_id, quantity in cart.items():
            if product_id in selected_items:
                product = get_object_or_404(Mehsul, id=product_id)
                if product.stok < quantity:
                    errors.append(f'{product.adi} məhsulundan kifayət qədər stok yoxdur.')
                    continue
                seller_id = product.sahib.id if product.sahib else 'asavto'
                if seller_id not in order_items_by_seller:
                    order_items_by_seller[seller_id] = {
                        'seller': product.sahib,
                        'items': []
                    }
                order_items_by_seller[seller_id]['items'].append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.qiymet
                })
            else:
                # Seçilməmiş məhsulları yeni səbətə əlavə et
                remaining_cart[product_id] = quantity

        if errors:
            for err in errors:
                messages.error(request, err)
            return redirect('cart')

        created_orders = []
        try:
            for seller_id, data in order_items_by_seller.items():
                items = data['items']
                total = sum(item['price'] * item['quantity'] for item in items)
                order = Sifaris.objects.create(
                    istifadeci=request.user,
                    umumi_mebleg=total,
                    catdirilma_usulu=catdirilma_usulu
                )
                for item in items:
                    SifarisItem.objects.create(
                        sifaris=order,
                        mehsul=item['product'],
                        miqdar=item['quantity'],
                        qiymet=item['price']
                    )
                # Satıcıya yeni sifariş bildirişi
                if seller_id:
                    try:
                        seller = User.objects.get(id=seller_id)
                        if hasattr(seller, 'profile'):
                            seller.profile.yeni_unread_sales += 1
                            seller.profile.save()
                    except User.DoesNotExist:
                        pass
                created_orders.append(order)

            # Səbəti yeniləyirik (yalnız seçilməmiş məhsulları saxlayırıq)
            request.session['cart'] = remaining_cart
            request.session.modified = True

            if len(created_orders) == 1:
                messages.success(request, 'Sifarişiniz uğurla yaradıldı.')
            elif len(created_orders) > 1:
                messages.success(request, f'{len(created_orders)} ayrı sifariş yaradıldı (fərqli satıcılar üçün).')
            else:
                messages.error(request, 'Sifariş yaradılmadı.')
            return redirect('orders')
        except Exception as e:
            # Əgər hər hansı bir order yaradılıbsa, onları sil
            for order in created_orders:
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


def search_suggestions(request):
    search_query = request.GET.get('search', '')
    if search_query:
        mehsullar = Mehsul.objects.all().annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            def clean_code(val):
                return re.sub(r'[^a-zA-Z0-9]', '', val.lower()) if val else ''
            brend_kod_ids = [m.id for m in mehsullar if clean_code(search_query) in clean_code(m.brend_kod)]
            brend_kod_filter = Q(id__in=brend_kod_ids)
            if search_words:
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter | ad_filter | searchtext_and_filter)[:5]
            else:
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter)[:5]
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
                    'satici': mehsul.sahib.username if mehsul.sahib else 'AS-AVTO',
                })
            return JsonResponse({'suggestions': suggestions})
    return JsonResponse({'suggestions': []})


def new_products_view(request):
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.filter(yenidir=True).order_by('-id')
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            def clean_code(val):
                return re.sub(r'[^a-zA-Z0-9]', '', val.lower()) if val else ''
            brend_kod_ids = [m.id for m in mehsullar if clean_code(search_query) in clean_code(m.brend_kod)]
            brend_kod_filter = Q(id__in=brend_kod_ids)
            if search_words:
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter | ad_filter | searchtext_and_filter)
            else:
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter)
    initial_products = mehsullar[:5]
    has_more = mehsullar.count() > 5
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    popup_images = PopupImage.objects.filter(aktiv=True)
    for m in initial_products:
        m.avg_rating = m.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        m.like_count = m.likes.count()
    return render(request, 'new_products.html', {
        'mehsullar': initial_products,
        'has_more': has_more,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
        'popup_images': popup_images
    })


def load_more_new_products(request):
    offset = int(request.GET.get('offset', 0))
    limit = 5
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.filter(yenidir=True).order_by('-id')
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            brend_kod_filter = Q(brend_kod__icontains=search_query)
            if search_words:
                ad_filters = []
                for word in search_words:
                    ad_filters.append(Q(adi__icontains=word))
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | brend_kod_filter | ad_filter | searchtext_and_filter)
            else:
                mehsullar = mehsullar.filter(kod_filter | brend_kod_filter)
    products = mehsullar[offset:offset + limit]
    has_more = mehsullar.count() > (offset + limit)
    products_data = []
    for product in products:
        avg_rating = product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        like_count = product.likes.count()
        products_data.append({
            'id': product.id,
            'adi': product.adi,
            'sekil_url': product.sekil.url if product.sekil else None,
            'firma': product.firma.adi,
            'firma_logo_url': product.firma.logo.url if product.firma and product.firma.logo else '',
            'avtomobil': product.avtomobil.adi if product.avtomobil else '',
            'avtomobil_logo_urls': [logo.sekil.url for logo in product.avtomobil.logolar.all()],
            'brend_kod': product.brend_kod,
            'oem': product.oem,
            'stok': product.stok,
            'qiymet': str(product.qiymet),
            'yenidir': product.yenidir,
            'sahib_id': product.sahib.id if product.sahib else None,
            'sahib_username': product.sahib.username if product.sahib else 'AS-AVTO',
            'avg_rating': avg_rating,
            'like_count': like_count,
        })
    return JsonResponse({
        'products': products_data,
        'has_more': has_more
    })

@require_http_methods(["POST"])
@login_required
def logout_view(request):
    logout(request)
    request.session.flush()
    return JsonResponse({'success': True})

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Bu istifadəçi adı artıq mövcuddur'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Bu email artıq mövcuddur'})
        if phone and hasattr(User, 'profile') and hasattr(User.profile, 'phone') and User.objects.filter(profile__phone=phone).exists():
            return JsonResponse({'success': False, 'error': 'Bu telefon nömrəsi artıq mövcuddur'})
        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.phone = phone
        user.profile.address = address
        user.profile.save()
        login(request, user)
        return JsonResponse({'success': True})
    return redirect('base')




@login_required
def my_products_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu səhifəyə giriş üçün icazəniz yoxdur.')
        return redirect('base')
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.filter(sahib=request.user).order_by('-id')
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            def clean_code(val):
                return re.sub(r'[^a-zA-Z0-9]', '', val.lower()) if val else ''
            brend_kod_ids = [m.id for m in mehsullar if clean_code(search_query) in clean_code(m.brend_kod)]
            brend_kod_filter = Q(id__in=brend_kod_ids)
            if search_words:
                ad_filters = []
                for word in search_words:
                    word_variations = normalize_azerbaijani_chars(word)
                    word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                    ad_filters.append(word_filter)
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter | ad_filter | searchtext_and_filter)
            else:
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter)
    initial_products = mehsullar[:5]
    has_more = mehsullar.count() > 5
    return render(request, 'my_products.html', {
        'mehsullar': initial_products,
        'has_more': has_more,
        'search_query': search_query,
        'now': timezone.now(),
    })

@login_required
def load_more_my_products(request):
    if not request.user.profile.is_verified:
        return JsonResponse({'products': [], 'has_more': False})
    offset = int(request.GET.get('offset', 0))
    limit = 5
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.filter(sahib=request.user).order_by('-id')
    if search_query:
        mehsullar = mehsullar.annotate(
            search_text=Concat(
                'adi', Value(' '),
                'brend_kod', Value(' '),
                'firma__adi', Value(' '),
                'avtomobil__adi', Value(' '),
                'kodlar',
                output_field=CharField()
            )
        )
        processed_query = re.sub(r'\s+', ' ', search_query).strip()
        search_words = processed_query.split()
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())
        if clean_search:
            kod_filter = Q(kodlar__icontains=clean_search)
            olcu_filter = Q(olcu__icontains=clean_search)
            brend_kod_filter = Q(brend_kod__icontains=search_query)
            if search_words:
                ad_filters = []
                for word in search_words:
                    ad_filters.append(Q(adi__icontains=word))
                ad_filter = reduce(and_, ad_filters)
                searchtext_and_filter = reduce(
                    and_,
                    [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
                )
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter | ad_filter | searchtext_and_filter)
            else:
                mehsullar = mehsullar.filter(kod_filter | olcu_filter | brend_kod_filter)
    products = mehsullar[offset:offset+limit]
    has_more = mehsullar.count() > (offset + limit)
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'adi': product.adi,
            'sekil_url': product.sekil.url if product.sekil else None,
            'firma': product.firma.adi if product.firma else '',
            'brend_kod': product.brend_kod,
            'stok': product.stok,
            'qiymet': str(product.qiymet),
            'yenidir': product.yenidir,
            'qalan_vaxt': product.qalan_vaxt() if product.yenidir else None,
        })
    return JsonResponse({'products': products_data, 'has_more': has_more})

@login_required
def my_sales_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, 'Bu səhifəyə giriş üçün icazəniz yoxdur.')
        return redirect('base')

    all_orders = Sifaris.objects.all().order_by('-tarix')
    filtered_orders = []
    total_orders = 0
    total_amount = 0
    total_paid = 0
    for order in all_orders:
        items = order.sifarisitem_set.filter(mehsul__sahib=request.user)
        order_total = sum(item.umumi_mebleg for item in items)
        if order_total > 0:
            # İstifadəçiyə aid məhsullar üçün ödənilən məbləğ (yalnız öz məhsullarına görə)
            seller_paid = order.odenilen_mebleg or 0
            total_orders += 1
            total_amount += order_total
            total_paid += seller_paid
            order.seller_total = order_total
            order.seller_paid = seller_paid
            order.seller_debt = order_total - seller_paid
            filtered_orders.append(order)

    stats = {
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_paid': total_paid,
        'total_debt': total_amount - total_paid
    }

    buyer_stats_dict = defaultdict(lambda: {'username': '', 'order_count': 0, 'total_amount': 0, 'total_paid': 0, 'total_debt': 0, 'user_id': None})
    for order in all_orders:
        items = order.sifarisitem_set.filter(mehsul__sahib=request.user)
        order_total = sum(item.umumi_mebleg for item in items)
        if order_total > 0:
            buyer = order.istifadeci
            buyer_stats = buyer_stats_dict[buyer.id]
            buyer_stats['username'] = buyer.username
            buyer_stats['user_id'] = buyer.id
            buyer_stats['order_count'] += 1
            buyer_stats['total_amount'] += order_total
            buyer_stats['total_paid'] += order.odenilen_mebleg or 0
            buyer_stats['total_debt'] += order_total - (order.odenilen_mebleg or 0)
    buyer_stats = list(buyer_stats_dict.values())

    context = {
        'orders': filtered_orders,
        'stats': stats,
        'buyer_stats': buyer_stats,
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

    # Yalnız bu istifadəçiyə aid məhsulların cəmini tap
    order_items = queryset
    total_amount = sum(item.umumi_mebleg for item in order_items)
    paid_share = 0
    if order.umumi_mebleg > 0:
        paid_share = (order.odenilen_mebleg or 0) * (total_amount / order.umumi_mebleg)
    qaliq_borc = total_amount - paid_share

    if request.method == 'POST':
        form = SifarisEditForm(request.POST, instance=order)
        formset = SifarisItemFormSet(request.POST, instance=order, queryset=queryset)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            order.update_total() # Formset save olanda onsuz da total update olur, amma zəmanət üçün
            messages.success(request, f"Sifariş #{order.id} uğurla yeniləndi.")
            return redirect('my_sales')
        else:
            messages.error(request, "Zəhmət olmasa xətaları düzəldin.")

    else:
        form = SifarisEditForm(instance=order)
        formset = SifarisItemFormSet(instance=order, queryset=queryset)

    context = {
        'order': order,
        'form': form,
        'formset': formset,
        'order_items': order_items,
        'total_amount': total_amount,
        'paid_share': paid_share,
        'qaliq_borc': qaliq_borc,
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
            
            # Əgər yeni edilirsə, tarixi qeyd et
            if yeni_mehsul.yenidir:
                yeni_mehsul.yeni_edildiyi_tarix = timezone.now()
            
            yeni_mehsul.save()
            
            # Əgər məhsul yeni olaraq işarələnibsə, 3 gün sonra avtomatik olaraq yenidən çıxar
            if yeni_mehsul.yenidir:
                import threading
                def auto_remove_new():
                    import time
                    time.sleep(259200)  # 3 gün (72 saat)
                    try:
                        # Məhsulu yenidən yüklə və yenidir statusunu yoxla
                        from django.db import transaction
                        with transaction.atomic():
                            mehsul = Mehsul.objects.select_for_update().get(id=yeni_mehsul.id)
                            if mehsul.yenidir:  # Əgər hələ də yenidirsə
                                mehsul.yenidir = False
                                mehsul.save()
                    except Exception as e:
                        print(f"Auto remove new status error: {e}")
                
                # Thread-i başlat
                thread = threading.Thread(target=auto_remove_new)
                thread.daemon = True
                thread.start()
            
            messages.success(request, f'Məhsul uğurla {"yeniləndi" if mehsul else "əlavə edildi"}.')
            return redirect('my_products')
    else:
        form = MehsulForm(instance=mehsul)

    return render(request, 'add_edit_product.html', {'form': form, 'now': timezone.now()})

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
@login_required
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
                'sekil_url': user.profile.sekil.url if user.profile and user.profile.sekil else '/static/images/no_image.jpg',
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

                    # Mövcud məhsulu həm brend_kod, həm firma, həm də sahib ilə yoxla
                    if firma:
                        existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma=firma, sahib=request.user).first()
                    else:
                        existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma__isnull=True, sahib=request.user).first()

                    if existing_product:
                        # Mövcud məhsulu yenilə, firmaya toxunma!
                        if not existing_product.sahib:
                            existing_product.sahib = request.user
                        existing_product.adi = temiz_ad
                        existing_product.kateqoriya = kateqoriya
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

@login_required
def my_sale_pdf(request, order_id):
    from home.models import Sifaris, SifarisItem, Profile
    from django.contrib.auth.models import User
    from reportlab.platypus import Table, TableStyle, Image, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    try:
        order = Sifaris.objects.get(id=order_id)
    except Sifaris.DoesNotExist:
        raise Http404("Sifariş tapılmadı")
    items = order.sifarisitem_set.filter(mehsul__sahib=request.user)
    if not items.exists():
        raise Http404("Bu sifarişdə sizin məhsul yoxdur")
    profile = getattr(request.user, 'profile', None)
    phone = profile.phone if profile and profile.phone else ''
    profile_image_path = None
    if profile and profile.sekil:
        profile_image_path = profile.sekil.path
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=0, bottomMargin=20)
    elements = []
    pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'NotoSans'
    styles['Normal'].fontName = 'NotoSans'
    styles['Normal'].spaceBefore = 0
    styles['Normal'].spaceAfter = 0
    az_months = {
        1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
        5: 'May', 6: 'İyun', 7: 'İyul', 8: 'Avqust',
        9: 'Sentyabr', 10: 'Oktyabr', 11: 'Noyabr', 12: 'Dekabr'
    }
    local_time = timezone.localtime(order.tarix)
    az_date = f"{local_time.day} {az_months[local_time.month]} {local_time.year}, {local_time.strftime('%H:%M')}"
    seller_info = []
    if profile_image_path:
        try:
            img = Image(profile_image_path, width=80, height=80)
            seller_info.append([img, Paragraph(f"<b>{request.user.username}</b><br/>{phone}", styles['Normal'])])
        except Exception:
            seller_info.append(['', Paragraph(f"<b>{request.user.username}</b><br/>{phone}", styles['Normal'])])
    else:
        seller_info.append(['', Paragraph(f"<b>{request.user.username}</b><br/>{phone}", styles['Normal'])])
    seller_table = Table(seller_info, colWidths=[90, 180])
    seller_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    order_info_table = Table([
        [Paragraph(f"Müştəri: {order.istifadeci.username}", styles['Normal'])],
        [Paragraph(f"Tarix: {az_date}", styles['Normal'])],
        [Paragraph(f"Çatdırılma: {order.get_catdirilma_usulu_display()}", styles['Normal'])],
        [Paragraph(f"Sifariş №{order.id}", styles['Normal'])]
    ], colWidths=[200])
    order_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    header_table = Table([
        [seller_table, order_info_table]
    ], colWidths=[doc.width-220, 220])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 20))
    headerStyle = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=9,
        textColor=colors.whitesmoke,
        alignment=1,
        spaceAfter=0,
        spaceBefore=0,
        leading=10
    )
    contentStyle = ParagraphStyle(
        'ContentStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=8,
        alignment=1,
        spaceAfter=0,
        spaceBefore=0,
        leading=10
    )
    headers = [
        Paragraph('№', headerStyle),
        Paragraph('Kod', headerStyle),
        Paragraph('Firma', headerStyle),
        Paragraph('Məhsul', headerStyle),
        Paragraph('Vitrin', headerStyle),
        Paragraph('Miqdar', headerStyle),
        Paragraph('Qiymət', headerStyle),
        Paragraph('Cəmi', headerStyle)
    ]
    data = [headers]
    total_amount = 0
    for idx, item in enumerate(items, 1):
        row = [
            Paragraph(str(idx), contentStyle),
            Paragraph(item.mehsul.brend_kod, contentStyle),
            Paragraph(item.mehsul.firma.adi if item.mehsul.firma else '-', contentStyle),
            Paragraph(truncate_product_name(item.mehsul.adi), contentStyle),
            Paragraph(str(item.mehsul.vitrin.nomre) if item.mehsul.vitrin else '-', contentStyle),
            Paragraph(str(item.miqdar), contentStyle),
            Paragraph(f"{item.qiymet} ₼", contentStyle),
            Paragraph(f"{item.umumi_mebleg} ₼", contentStyle)
        ]
        data.append(row)
        total_amount += item.umumi_mebleg
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B5173')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B5173')),
        ('COLWIDTHS', (0, 0), (-1, -1), '*'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))
    # Ümumi borc hesabla (alıcı ilə bu satıcı arasında bütün sifarişlər üzrə)
    all_orders = Sifaris.objects.filter(istifadeci=order.istifadeci)
    umumi_borc = 0
    for o in all_orders:
        seller_items = o.sifarisitem_set.filter(mehsul__sahib=request.user)
        order_total = sum(item.umumi_mebleg for item in seller_items)
        if order_total > 0:
            umumi_borc += order_total - (o.odenilen_mebleg or 0)
    totalStyle = ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=10,
        alignment=0,
        spaceAfter=0,
        spaceBefore=0,
        leading=12
    )
    amountStyle = ParagraphStyle(
        'AmountStyle',
        parent=styles['Normal'],
        fontName='NotoSans',
        fontSize=10,
        alignment=2,
        spaceAfter=0,
        spaceBefore=0,
        leading=12,
        textColor=colors.HexColor('#2B5173')
    )
    total_data = [
        [Paragraph('Ümumi Cəmi :', totalStyle), Paragraph(f"{total_amount} ₼", amountStyle)],
        [Paragraph('Ümumi Borc :', totalStyle), Paragraph(f"{umumi_borc} ₼", amountStyle)]
    ]
    total_table = Table(total_data, colWidths=[100, 100])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (0, -1), 20),
    ]))
    align_table = Table([[total_table]], colWidths=[525])
    align_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ]))
    elements.append(align_table)
    elements.append(Spacer(1, 30))
    # Ödəniş bölməsi
    payment_text = f"Ödənilən Məbləğ: ___________________________ ₼"
    elements.append(Paragraph(payment_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    # İmza bölməsi
    signature_data = [[
        Paragraph("Təhvil Verdi: _________________", styles['Normal']),
        Paragraph(f"Təhvil Aldı: {order.istifadeci.username} _________________", styles['Normal'])
    ]]
    signature_table = Table(signature_data, colWidths=[250, 250])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(signature_table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = FileResponse(io.BytesIO(pdf), as_attachment=True, filename=f'sifaris_{order.id}_satici.pdf')
    return response

@csrf_exempt
@login_required
def update_profile(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        sekil = request.FILES.get('sekil')
        # Username yoxlaması
        if not username:
            return JsonResponse({'status': 'error', 'message': 'İstifadəçi adı boş ola bilməz!'}, status=400)
        if username != user.username and User.objects.filter(username=username).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu istifadəçi adı artıq mövcuddur!'}, status=400)
        # Telefon yoxlaması
        if not phone:
            return JsonResponse({'status': 'error', 'message': 'Telefon boş ola bilməz!'}, status=400)
        if profile and phone != profile.phone and User.objects.filter(profile__phone=phone).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu telefon nömrəsi artıq istifadə olunur!'}, status=400)
        # Ünvan yoxlaması
        if not address:
            return JsonResponse({'status': 'error', 'message': 'Ünvan boş ola bilməz!'}, status=400)
        # Yenilə
        user.username = username
        user.save()
        if profile:
            profile.phone = phone
            profile.address = address
            if sekil:
                profile.sekil = sekil
            profile.save()
        return JsonResponse({
            'status': 'success',
            'username': user.username,
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'sekil_url': profile.sekil.url if profile and profile.sekil else ''
        })
    # GET üçün profil məlumatı qaytar
    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'username': user.username,
            'phone': profile.phone if profile else '',
            'address': profile.address if profile else '',
            'sekil_url': profile.sekil.url if profile and profile.sekil else ''
        })
    return JsonResponse({'status': 'error', 'message': 'Yalnız POST və GET dəstəklənir.'}, status=405)

@login_required
def my_products_pdf(request):
    user = request.user
    mehsullar = Mehsul.objects.filter(sahib=user)
    pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mehsullar.pdf"'
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].fontName = 'NotoSans'
    # Profil nömrəsini əlavə et
    phone = user.profile.phone if hasattr(user, 'profile') and user.profile.phone else ''
    title_text = f"{user.username} ({phone}) Məhsulları" if phone else f"{user.username} Məhsulları"
    title = Paragraph(title_text, styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    headers = ['№', 'Kod', 'Firma', 'Məhsul', 'Vitrin', 'Stok', 'Qiymət']
    data = [headers]
    for index, mehsul in enumerate(mehsullar, 1):
        row = [
            str(index),
            mehsul.brend_kod,
            mehsul.firma.adi if mehsul.firma else '-',
            truncate_product_name(mehsul.adi),
            str(mehsul.vitrin.nomre) if mehsul.vitrin else '-',
            str(mehsul.stok),
            f"{mehsul.qiymet} ₼"
        ]
        data.append(row)
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B5173')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B5173')),
        ('COLWIDTHS', (0, 0), (-1, -1), '*'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@csrf_exempt
@login_required
def unread_sales_count(request):
    if request.method == 'GET':
        count = 0
        if hasattr(request.user, 'profile'):
            count = request.user.profile.yeni_unread_sales
        return JsonResponse({'count': count})
    elif request.method == 'POST':
        # Sıfırla
        if hasattr(request.user, 'profile'):
            request.user.profile.yeni_unread_sales = 0
            request.user.profile.save()
        return JsonResponse({'status': 'ok'})
    
@login_required
def seller_admin_panel(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'profile') or not request.user.profile.is_verified:
        from django.contrib import messages
        messages.error(request, 'Satıcı panelinə giriş üçün icazəniz yoxdur.')
        return redirect('base')
    
    # Dashboard statistikaları
    from django.utils import timezone
    from datetime import timedelta
    
    # Məhsul statistikaları
    total_products = Mehsul.objects.filter(sahib=request.user).count()
    new_products = Mehsul.objects.filter(sahib=request.user, yenidir=True).count()
    out_of_stock_products = Mehsul.objects.filter(sahib=request.user, stok=0).count()
    
    # Satış statistikaları
    from .models import SifarisItem
    all_order_items = SifarisItem.objects.filter(mehsul__sahib=request.user)
    seller_orders = []
    total_sales = 0
    
    # Sifarişləri qruplaşdır
    order_totals = {}
    for item in all_order_items:
        order = item.sifaris
        if order.id not in order_totals:
            order_totals[order.id] = {
                'order': order,
                'total': 0
            }
        order_totals[order.id]['total'] += item.umumi_mebleg
    
    # Ümumi satış hesabla
    for order_data in order_totals.values():
        total_sales += order_data['total']
        seller_orders.append(order_data)
    
    # Son 5 sifariş
    recent_orders = sorted(seller_orders, key=lambda x: x['order'].tarix, reverse=True)[:5]
    
    # Alıcı statistikaları
    buyer_stats = {}
    for order_data in seller_orders:
        buyer = order_data['order'].istifadeci
        if buyer.id not in buyer_stats:
            buyer_stats[buyer.id] = {
                'username': buyer.username,
                'order_count': 0,
                'total_amount': 0
            }
        buyer_stats[buyer.id]['order_count'] += 1
        buyer_stats[buyer.id]['total_amount'] += order_data['total']
    
    # Ən yaxşı alıcılar (top 5)
    top_buyers = sorted(buyer_stats.values(), key=lambda x: x['total_amount'], reverse=True)[:5]
    
    # Kateqoriya üzrə məhsul sayı
    category_stats = {}
    for product in Mehsul.objects.filter(sahib=request.user):
        category_name = product.kateqoriya.adi if product.kateqoriya else 'Kateqoriyasız'
        if category_name not in category_stats:
            category_stats[category_name] = 0
        category_stats[category_name] += 1
    
    # Firma üzrə məhsul sayı
    brand_stats = {}
    for product in Mehsul.objects.filter(sahib=request.user):
        brand_name = product.firma.adi if product.firma else 'Firmasız'
        if brand_name not in brand_stats:
            brand_stats[brand_name] = 0
        brand_stats[brand_name] += 1
    
    # Top 5 firma
    top_brands = sorted(brand_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'total_products': total_products,
        'new_products': new_products,
        'out_of_stock_products': out_of_stock_products,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'top_buyers': top_buyers,
        'category_stats': category_stats,
        'top_brands': top_brands,
        'total_orders': len(seller_orders),
    }
    
    return render(request, 'admin_panel.html', context)

@csrf_exempt
@login_required
def toggle_product_new_status(request, product_id):
    """Məhsulun yeni statusunu dəyişdirir"""
    if request.method == 'POST':
        try:
            mehsul = get_object_or_404(Mehsul, id=product_id, sahib=request.user)
            mehsul.yenidir = not mehsul.yenidir
            
            # Əgər yeni edilirsə, tarixi qeyd et
            if mehsul.yenidir:
                from django.utils import timezone
                mehsul.yeni_edildiyi_tarix = timezone.now()
            else:
                mehsul.yeni_edildiyi_tarix = None
                
            mehsul.save()
            return JsonResponse({
                'success': True,
                'yenidir': mehsul.yenidir,
                'qalan_vaxt': mehsul.qalan_vaxt() if mehsul.yenidir else None,
                'message': 'Məhsul yeni statusu yeniləndi'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Xəta baş verdi'
            })
    return JsonResponse({'success': False, 'message': 'Yanlış sorğu'})

@csrf_exempt
@login_required
def change_product_image(request, product_id):
    """Məhsulun şəklini dəyişmək üçün AJAX endpoint"""
    if request.method == 'POST' and request.FILES.get('sekil'):
        mehsul = get_object_or_404(Mehsul, id=product_id, sahib=request.user)
        sekil = request.FILES['sekil']
        mehsul.sekil = sekil
        mehsul.save()
        return JsonResponse({
            'success': True,
            'sekil_url': mehsul.sekil.url
        })
    return JsonResponse({'success': False, 'message': 'Şəkil yüklənmədi'})

def root_view(request):
    if request.user.is_authenticated:
        return redirect('base')
    else:
        return redirect('login')

def product_detail_view(request, product_id):
    from .models import Mehsul
    from django.http import Http404
    import re
    mehsul = get_object_or_404(Mehsul, id=product_id)
    kodlar_list = []
    if mehsul.kodlar:
        kodlar_list = re.split(r'[\s,\n]+', mehsul.kodlar)
        kodlar_list = [k for k in kodlar_list if k]
    # Yeni: bəyənibmi və neçə ulduz verib
    user_liked = False
    user_rating = 0
    if request.user.is_authenticated:
        user_liked = ProductLike.objects.filter(user=request.user, mehsul=mehsul).exists()
        rating_obj = ProductRating.objects.filter(user=request.user, mehsul=mehsul).first()
        if rating_obj:
            user_rating = rating_obj.rating
    avg_rating = ProductRating.objects.filter(mehsul=mehsul).aggregate(Avg('rating'))['rating__avg'] or 0
    like_count = ProductLike.objects.filter(mehsul=mehsul).count()
    # Bütün şərhlər (ən yenilər birinci)
    reviews = ProductRating.objects.filter(mehsul=mehsul).select_related('user__profile').order_by('-created_at')
    review_count = reviews.count()
    return render(request, 'product_detail.html', {
        'mehsul': mehsul,
        'kodlar_list': kodlar_list,
        'user_liked': user_liked,
        'user_rating': user_rating,
        'avg_rating': round(avg_rating, 2),
        'like_count': like_count,
        'reviews': reviews,
        'review_count': review_count,
    })

@csrf_exempt
@login_required
@require_POST
def like_product(request):
    product_id = request.POST.get('product_id')
    mehsul = get_object_or_404(Mehsul, id=product_id)
    like, created = ProductLike.objects.get_or_create(user=request.user, mehsul=mehsul)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    like_count = ProductLike.objects.filter(mehsul=mehsul).count()
    return JsonResponse({'liked': liked, 'like_count': like_count})

@csrf_exempt
@login_required
@require_POST
def rate_product(request):
    product_id = request.POST.get('product_id')
    rating_value = int(request.POST.get('rating', 0))
    comment = request.POST.get('comment', '').strip()
    mehsul = get_object_or_404(Mehsul, id=product_id)
    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'success': False, 'error': 'Yanlış reytinq'}, status=400)
    rating, created = ProductRating.objects.update_or_create(
        user=request.user, mehsul=mehsul,
        defaults={'rating': rating_value, 'comment': comment}
    )
    avg_rating = ProductRating.objects.filter(mehsul=mehsul).aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = ProductRating.objects.filter(mehsul=mehsul).count()
    return JsonResponse({'success': True, 'avg_rating': round(avg_rating, 2), 'user_rating': rating_value, 'review_count': review_count})

@login_required
def liked_products_view(request):
    liked_products = Mehsul.objects.filter(likes__user=request.user)
    for m in liked_products:
        m.avg_rating = m.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        m.like_count = m.likes.count()
    return render(request, 'liked_products.html', {'mehsullar': liked_products})