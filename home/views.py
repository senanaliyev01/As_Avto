from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Kateqoriya, Sifaris, SifarisItem, Firma, Avtomobil, PopupImage, Header_Message, Vitrin, ProductLike, ProductRating
from django.db.models import Q, Sum, F, Case, When, DecimalField, Avg, Count, FloatField
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
from django.db.models.functions import Concat, Cast
from django.db.models import CharField
from django.db import models
from math import sqrt
import os
import json
import uuid
from django.conf import settings

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
            return JsonResponse({'success': False, 'error': 'Şifrə və ya istifadəçi adı yanlışdır'})
    return redirect('base')


def home_view(request):
    # Yeni məhsulları əldə et
    new_products = Mehsul.objects.filter(yenidir=True).order_by('-id')[:10]
    # Aktiv popup şəkilləri əldə et
    popup_images = PopupImage.objects.filter(aktiv=True)

    # Ən çox satılan məhsullar (top 10)
    most_sold_products = (
        Mehsul.objects.annotate(total_sold=Sum('sifarisitem__miqdar'))
        .filter(total_sold__isnull=False)
        .order_by('-total_sold')[:10]
    )
    # Ən çox bəyənilən məhsullar (top 10)
    most_liked_products = (
        Mehsul.objects.annotate(like_count=Count('likes'))
        .filter(like_count__gt=0)
        .order_by('-like_count')[:10]
    )

    # Wilson score ilə ən yaxşı reytinqli məhsullar (top 10)
    rated_products = (
        Mehsul.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings'),
            sum_rating=Sum('ratings__rating')
        )
        .filter(rating_count__gt=0)
    )
    # Wilson lower bound hesabla və sıralama üçün python-da sort et
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96  # 95% confidence
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score
    rated_products = list(rated_products)
    for m in rated_products:
        m.wilson_score = wilson_score(m.sum_rating, m.rating_count)
        m.avg_rating = m.avg_rating or 0
        m.like_count = m.likes.count()
        m.total_sold = m.sifarisitem_set.aggregate(Sum('miqdar'))['miqdar__sum'] or 0
    most_rated_products = sorted(rated_products, key=lambda m: m.wilson_score, reverse=True)[:10]

    return render(request, 'base.html', {
        'new_products': new_products,
        'popup_images': popup_images,
        'most_sold_products': most_sold_products,
        'most_rated_products': most_rated_products,
        'most_liked_products': most_liked_products,
    })


def products_view(request):
    search_query = request.GET.get('search', '')
    mehsullar = Mehsul.objects.all()
    popup_images = PopupImage.objects.filter(aktiv=True)
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
    initial_products = list(mehsullar[:5])
    has_more = mehsullar.count() > 5

    # Wilson score hesabla (base.html-dəki kimi)
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96  # 95% confidence
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score

    for m in initial_products:
        m.avg_rating = m.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        m.like_count = m.likes.count()
        m.sum_rating = m.ratings.aggregate(Sum('rating'))['rating__sum'] or 0
        m.rating_count = m.ratings.count()
        m.wilson_score = wilson_score(m.sum_rating, m.rating_count)

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
    mehsullar = Mehsul.objects.all()
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
    products = mehsullar[offset:offset + limit]
    has_more = mehsullar.count() > (offset + limit)

    from math import sqrt
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score

    products_data = []
    for product in products:
        avg_rating = product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        like_count = product.likes.count()
        sum_rating = product.ratings.aggregate(Sum('rating'))['rating__sum'] or 0
        rating_count = product.ratings.count()
        wilson = wilson_score(sum_rating, rating_count)
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
            'wilson_score': wilson,
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
        messages.warning(request, 'Bəzi məhsullar səbətdən silindi, çünki artıq mövcud deyil.')
    
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
            response_data['message'] = f'Yalnız {product.stok} vahid {product.adi} mövcuddur!'
            return JsonResponse(response_data)
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        cart = request.session['cart']
        current_quantity = cart.get(str(product_id), 0)
        new_quantity = current_quantity + quantity
        
        if new_quantity > product.stok:
            response_data['message'] = f'Yalnız {product.stok} vahid {product.adi} mövcuddur!'
            return JsonResponse(response_data)
        
        cart[str(product_id)] = new_quantity
        request.session['cart'] = cart
        request.session.modified = True
        
        response_data.update({
            'status': 'success',
            'message': f'{quantity} vahid {product.adi} səbətə əlavə edildi!',
            'cart_count': len(cart)
        })
        
        return JsonResponse(response_data)
    
    return JsonResponse({'status': 'error', 'message': 'Səhv məlumat daxil edildi'})

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
        'message': 'Səhv məlumat daxil edildi'
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
            messages.error(request, 'Ən azı bir məhsul seçin.')
            return redirect('cart')
            
        if not catdirilma_usulu:
            messages.error(request, 'Göndərmə üsulu seçin.')
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
                    errors.append(f'{product.adi} üçün kifayət qədər stok yoxdur.')
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
                messages.success(request, 'Sifariş uğurla yaradıldı.')
            elif len(created_orders) > 1:
                messages.success(request, f'{len(created_orders)} fərqli satıcılar üçün sifariş yaradıldı.')
            else:
                messages.error(request, 'Sifariş yaradılmadı.')
            return redirect('orders')
        except Exception as e:
            # Əgər hər hansı bir order yaradılıbsa, onları sil
            for order in created_orders:
                order.delete()
            messages.error(request, 'Sifariş yaradılırken xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin.')
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
                response_data['message'] = f'Yalnız {product.stok} vahid {product.adi} mövcuddur!'
                return JsonResponse(response_data)
            
            if quantity < 1:
                response_data['message'] = 'Vahid sayı 1-dən az ola bilməz!'
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
                'message': f'{product.adi} üçün vahid sayı yeniləndi!',
                'subtotal': f'{subtotal} ₼',
                'cart_total': f'{cart_total} ₼'
            })
            
            return JsonResponse(response_data)
            
        except ValueError:
            return JsonResponse({
                'status': 'error',
                'message': 'Səhv vahid sayı daxil edildi!'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Səhv məlumat daxil edildi'
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
        mehsullar = Mehsul.objects.all()
        mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)[:5]
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
    mehsullar = Mehsul.objects.filter(yenidir=True)
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
    initial_products = list(mehsullar[:5])
    has_more = mehsullar.count() > 5
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    popup_images = PopupImage.objects.filter(aktiv=True)

    from math import sqrt
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score

    for m in initial_products:
        m.avg_rating = m.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        m.like_count = m.likes.count()
        m.sum_rating = m.ratings.aggregate(Sum('rating'))['rating__sum'] or 0
        m.rating_count = m.ratings.count()
        m.wilson_score = wilson_score(m.sum_rating, m.rating_count)

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
    mehsullar = Mehsul.objects.filter(yenidir=True)
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
    products = mehsullar[offset:offset + limit]
    has_more = mehsullar.count() > (offset + limit)

    from math import sqrt
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score

    products_data = []
    for product in products:
        avg_rating = product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        like_count = product.likes.count()
        sum_rating = product.ratings.aggregate(Sum('rating'))['rating__sum'] or 0
        rating_count = product.ratings.count()
        wilson = wilson_score(sum_rating, rating_count)
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
            'wilson_score': wilson,
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
    mehsullar = Mehsul.objects.filter(sahib=request.user)
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
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
    mehsullar = Mehsul.objects.filter(sahib=request.user)
    mehsullar = get_search_filtered_products(mehsullar, search_query, order_by_wilson=True)
    products = mehsullar[offset:offset+limit]
    has_more = mehsullar.count() > (offset + limit)

    from math import sqrt
    def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
        if not rating_count or not sum_rating:
            return 0
        z = 1.96
        phat = (sum_rating / rating_count) / max_rating
        n = rating_count
        denominator = 1 + z*z/n
        centre = phat + z*z/(2*n)
        margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
        score = (centre - margin) / denominator
        return score

    products_data = []
    for product in products:
        avg_rating = product.ratings.aggregate(models.Avg('rating'))['rating__avg'] or 0
        like_count = product.likes.count()
        sum_rating = product.ratings.aggregate(Sum('rating'))['rating__sum'] or 0
        rating_count = product.ratings.count()
        wilson = wilson_score(sum_rating, rating_count)
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
            'avg_rating': avg_rating,
            'like_count': like_count,
            'wilson_score': wilson,
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
            messages.error(request, "Xətaları düzəltin.")

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
        messages.error(request, 'Bu əməliyyatı yerinə yetirmək üçün icazəniz yoxdur.')
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
        messages.error(request, 'Bu əməliyyatı yerinə yetirmək üçün icazəniz yoxdur.')
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
            'message': 'Xəta baş verdi. Zəhmət olmasa, yenidən cəhd edin.'
        }
    
    return JsonResponse(data)

@login_required
@transaction.atomic
def import_user_products_view(request):
    if not request.user.profile.is_verified:
        messages.error(request, "Bu əməliyyatı yerinə yetirmək üçün icazəniz yoxdur.")
        return redirect('my_products')

    if request.method == 'POST':
        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            messages.error(request, 'Excel faylı seçin')
            return redirect('my_products')
        
        if not excel_file.name.endswith('.xlsx'):
            messages.error(request, 'Yalnız .xlsx faylı qəbul edilir')
            return redirect('my_products')
            
        try:
            df = pd.read_excel(excel_file)
            
            new_count = 0
            update_count = 0
            error_count = 0
            deleted_count = 0
            # Excel faylındakı məhsulların açarları: (brend_kod, firma_id)
            excel_product_keys = set()
            
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
                        messages.error(request, f'Xəta baş verdi, sətir {index + 2} işlənir: Məhsulun adı boşdur.', level=messages.ERROR)
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
                        messages.error(request, f'Xəta baş verdi, sətir {index + 2} işlənir: Brend kodu boşdur.', level=messages.ERROR)
                        error_count += 1
                        continue

                    # Bu sətirdəki məhsulun açarını yadda saxla
                    excel_product_keys.add((brend_kod, firma.id if firma else None))

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
                    messages.error(request, f'Xəta baş verdi, sətir {index + 2} işlənir: {e}', level=messages.ERROR)
                    error_count += 1
                    continue
            
            # Excel-də olmayan məhsulları sil (yalnız bu istifadəçiyə aid)
            if excel_product_keys:
                user_products_qs = Mehsul.objects.filter(sahib=request.user)
                to_delete_ids = [
                    p.id for p in user_products_qs.only('id', 'brend_kod', 'firma_id')
                    if (p.brend_kod, p.firma_id) not in excel_product_keys
                ]
                if to_delete_ids:
                    deleted_count, _ = Mehsul.objects.filter(id__in=to_delete_ids).delete()

            success_message = f"Excel fayl uğurla əlavə edildi! "
            if new_count > 0:
                success_message += f"{new_count} yeni məhsul əlavə edildi. "
            if update_count > 0:
                success_message += f"{update_count} məhsul yeniləndi. "
            if deleted_count > 0:
                success_message += f"{deleted_count} məhsul Excel-də olmadığı üçün silindi. "
            
            if error_count > 0:
                messages.warning(request, f"Xətalar {error_count} sətirdə baş verdi.")
            
            if new_count > 0 or update_count > 0 or deleted_count > 0:
                messages.success(request, success_message)
            elif error_count == 0:
                messages.info(request, "Fayldakı dəyişikliklər yoxdur.")

        except Exception as e:
            messages.error(request, f'Excel fayl oxunurken xəta baş verdi: {e}', level=messages.ERROR)
        
        return redirect('my_products')
    
    return redirect('my_products')


# =============== BATCH EXCEL IMPORT (Mərhələli) ===============
@login_required
@csrf_exempt
def import_user_products_init(request):
    """Excel faylını qəbul edir, sətirləri təmizləyib job faylına yazır, job_id qaytarır"""
    if not request.user.profile.is_verified:
        return JsonResponse({'status': 'error', 'message': 'Icazə yoxdur.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

    excel_file = request.FILES.get("excel_file")
    if not excel_file:
        return JsonResponse({'status': 'error', 'message': 'Excel faylı seçin.'}, status=400)
    if not excel_file.name.endswith('.xlsx'):
        return JsonResponse({'status': 'error', 'message': 'Yalnız .xlsx faylı qəbul edilir.'}, status=400)

    # Faylı media/imports altına yaz
    imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
    os.makedirs(imports_dir, exist_ok=True)
    job_id = str(uuid.uuid4())
    saved_path = os.path.join(imports_dir, f'user_{request.user.id}_{job_id}.xlsx')
    with open(saved_path, 'wb+') as dest:
        for chunk in excel_file.chunks():
            dest.write(chunk)

    # Exceli oxu və sətirləri təmizlə
    try:
        df = pd.read_excel(saved_path)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Excel oxunmadı: {e}'}, status=400)

    cleaned_rows = []
    for index, row in df.iterrows():
        row = {str(k).strip().lower(): v for k, v in row.items()}
        cleaned_rows.append(row)

    total_rows = len(cleaned_rows)

    # Job state faylı
    jobs_dir = os.path.join(imports_dir, 'jobs')
    os.makedirs(jobs_dir, exist_ok=True)
    job_state_path = os.path.join(jobs_dir, f'{job_id}.json')
    job_state = {
        'user_id': request.user.id,
        'file_path': saved_path,
        'total_rows': total_rows,
        'processed_rows': 0,
        'new_count': 0,
        'update_count': 0,
        'error_count': 0,
        'deleted_count': 0,
        'excel_product_keys': [],  # (brend_kod, firma_id)
        'error_details': [],  # ['5-ci sətir: ...', ...]
        'rows': cleaned_rows,
    }
    with open(job_state_path, 'w', encoding='utf-8') as f:
        json.dump(job_state, f, ensure_ascii=False)

    return JsonResponse({'status': 'ok', 'job_id': job_id, 'total_rows': total_rows})


@login_required
@csrf_exempt
def import_user_products_batch(request):
    """Verilən interval üzrə (start, size) sətirləri emal edir"""
    if not request.user.profile.is_verified:
        return JsonResponse({'status': 'error', 'message': 'Icazə yoxdur.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

    job_id = request.POST.get('job_id')
    try:
        start = int(request.POST.get('start', 0))
        size = int(request.POST.get('size', 100))
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'start/size yanlışdır.'}, status=400)

    imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
    job_state_path = os.path.join(imports_dir, 'jobs', f'{job_id}.json')
    if not os.path.exists(job_state_path):
        return JsonResponse({'status': 'error', 'message': 'Job tapılmadı.'}, status=404)

    with open(job_state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)

    if state.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': 'Icazə yoxdur.'}, status=403)

    rows = state.get('rows', [])
    subset = rows[start:start+size]
    if not subset:
        return JsonResponse({'status': 'ok', 'message': 'Heç nə yoxdur', 'processed_rows': state['processed_rows'], 'new_count': state['new_count'], 'update_count': state['update_count'], 'error_count': state['error_count']})

    new_count = state['new_count']
    update_count = state['update_count']
    error_count = state['error_count']
    excel_keys = set(tuple(k) for k in state.get('excel_product_keys', []))
    error_details = state.get('error_details', [])
    batch_errors = []

    # Emal məntiqi (mövcud import_user_products_view ilə eyni)
    preview_keys = ['adi', 'brend_kod', 'firma', 'avtomobil', 'qiymet', 'stok', 'kodlar', 'olcu']
    def sanitize_row_values(row_dict):
        safe = {}
        for k, v in row_dict.items():
            try:
                if pd.isna(v):
                    safe[str(k)] = ''
                else:
                    safe[str(k)] = str(v)
            except Exception:
                safe[str(k)] = ''
        return safe

    for idx, row in enumerate(subset, start=start):
        try:
            excel_line_no = idx + 2  # Başlıq 1-ci sətir, data 2-dən başlayır
            row_error_items = []  # [{'field': 'adi', 'message': '...'}]
            sanitized_row = sanitize_row_values(row)
            # Model referansları
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
                row_error_items.append({'field': 'adi', 'message': 'Məhsulun adı boşdur'})

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
                row_error_items.append({'field': 'brend_kod', 'message': 'Brend kodu boşdur'})

            # Rəqəmsal sahələr üçün yoxlama
            def is_floatable(val):
                try:
                    float(val)
                    return True
                except Exception:
                    return False
            def is_intable(val):
                try:
                    int(float(val))
                    return True
                except Exception:
                    return False

            if 'qiymet' in row and pd.notna(row['qiymet']):
                if not is_floatable(row['qiymet']):
                    row_error_items.append({'field': 'qiymet', 'message': 'qiymet rəqəm olmalıdır'})
            if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']):
                if not is_floatable(row['maya_qiymet']):
                    row_error_items.append({'field': 'maya_qiymet', 'message': 'maya_qiymet rəqəm olmalıdır'})
            if 'stok' in row and pd.notna(row['stok']):
                if not is_intable(row['stok']):
                    row_error_items.append({'field': 'stok', 'message': 'stok tam ədəd olmalıdır'})

            # Əgər xəta varsa, bu sətiri emal etmədən saxla
            if row_error_items:
                error_count += 1
                batch_errors.append({
                    'line': excel_line_no,
                    'messages': [e['message'] for e in row_error_items],
                    'fields': [e['field'] for e in row_error_items],
                    'row': sanitized_row
                })
                continue

            excel_keys.add((brend_kod, firma.id if firma else None))

            if firma:
                existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma=firma, sahib=request.user).first()
            else:
                existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma__isnull=True, sahib=request.user).first()

            if existing_product:
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
            error_count += 1
            batch_errors.append({
                'line': excel_line_no,
                'messages': [str(e)],
                'fields': [],
                'row': sanitize_row_values(row)
            })
            continue

    # State-i yenilə
    state['new_count'] = new_count
    state['update_count'] = update_count
    state['error_count'] = error_count
    state['processed_rows'] = min(state['total_rows'], start + len(subset))
    state['excel_product_keys'] = list(excel_keys)
    # Toplam error detallarını yığ
    if batch_errors:
        error_details.extend(batch_errors)
        state['error_details'] = error_details
    with open(job_state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False)

    return JsonResponse({
        'status': 'ok',
        'processed_rows': state['processed_rows'],
        'total_rows': state['total_rows'],
        'new_count': new_count,
        'update_count': update_count,
        'error_count': error_count,
        'errors': batch_errors,
    })


@login_required
@csrf_exempt
def import_user_products_finalize(request):
    """Excel-də olmayan məhsulları silir və job fayllarını təmizləyir"""
    if not request.user.profile.is_verified:
        return JsonResponse({'status': 'error', 'message': 'Icazə yoxdur.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

    job_id = request.POST.get('job_id')
    imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
    job_state_path = os.path.join(imports_dir, 'jobs', f'{job_id}.json')
    if not os.path.exists(job_state_path):
        return JsonResponse({'status': 'error', 'message': 'Job tapılmadı.'}, status=404)

    with open(job_state_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    if state.get('user_id') != request.user.id:
        return JsonResponse({'status': 'error', 'message': 'Icazə yoxdur.'}, status=403)

    excel_keys = set(tuple(k) for k in state.get('excel_product_keys', []))
    deleted_count = 0
    if excel_keys:
        user_products_qs = Mehsul.objects.filter(sahib=request.user)
        to_delete_ids = [
            p.id for p in user_products_qs.only('id', 'brend_kod', 'firma_id')
            if (p.brend_kod, p.firma_id) not in excel_keys
        ]
        if to_delete_ids:
            deleted_count, _ = Mehsul.objects.filter(id__in=to_delete_ids).delete()

    # Faylları təmizlə
    try:
        if os.path.exists(state.get('file_path', '')):
            os.remove(state['file_path'])
    except Exception:
        pass
    try:
        os.remove(job_state_path)
    except Exception:
        pass

    return JsonResponse({'status': 'ok', 'deleted_count': deleted_count, 'total_errors': len(state.get('error_details', [])), 'error_details': state.get('error_details', [])})

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
            return JsonResponse({'status': 'error', 'message': 'Telefon nömrəsi boş ola bilməz!'}, status=400)
        if profile and phone != profile.phone and User.objects.filter(profile__phone=phone).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu telefon nömrəsi artıq mövcuddur!'}, status=400)
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
                'message': 'Product new status updated'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred'
            })
    return JsonResponse({'success': False, 'message': 'Səhv məlumat daxil edildi'})

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
        return JsonResponse({'success': False, 'error': 'Səhv reyting'}, status=400)
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

def about_view(request):
    return render(request, 'about.html')

def privacy_policy_view(request):
    return render(request, 'privacy_policy.html')

# UNIVERSAL SEARCH FILTER

def get_search_filtered_products(queryset, search_query, order_by_wilson=True):
    import re
    from functools import reduce
    from operator import and_, or_
    from django.db.models import Q, Value, CharField, Avg, Count, Sum, FloatField
    from django.db.models.functions import Concat, Cast
    from math import sqrt

    if not search_query:
        # Wilson score annotasiyası əlavə et
        if order_by_wilson:
            queryset = queryset.annotate(
                sum_rating=Sum('ratings__rating'),
                rating_count=Count('ratings'),
            )
            # Wilson score hesabla (SQL səviyyəsində mümkün deyil, amma annotate ilə təxmini)
            # Ən yaxşısı: python səviyyəsində sort etməkdir, amma burada annotate ilə sıralayırıq
            def wilson_score(sum_rating, rating_count, max_rating=5, confidence=0.95):
                if not rating_count or not sum_rating:
                    return 0
                z = 1.96  # 95% confidence
                phat = (sum_rating / rating_count) / max_rating
                n = rating_count
                denominator = 1 + z*z/n
                centre = phat + z*z/(2*n)
                margin = z * sqrt((phat*(1-phat) + z*z/(4*n)) / n)
                score = (centre - margin) / denominator
                return score
            # Annotate üçün: sadəcə ortalama reytinq və sayına görə sıralayırıq
            queryset = queryset.annotate(
                avg_rating=Avg('ratings__rating'),
                rating_count=Count('ratings'),
            ).order_by(
                '-rating_count', '-avg_rating', '-id'
            )
        return queryset

    queryset = queryset.annotate(
        search_text=Concat(
            'adi', Value(' '),
            'brend_kod', Value(' '),
            'firma__adi', Value(' '),
            'avtomobil__adi', Value(' '),
            'kodlar', Value(' '),
            'olcu', Value(' '),
            'melumat',
            output_field=CharField()
        )
    )
    processed_query = re.sub(r'\s+', ' ', search_query).strip()
    search_words = processed_query.split()
    clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query.lower())

    def normalize_azerbaijani_chars(text):
        char_map = {
            'ə': 'e', 'e': 'ə', 'Ə': 'E', 'E': 'Ə',
            'ö': 'o', 'o': 'ö', 'Ö': 'O', 'O': 'Ö',
            'ğ': 'g', 'g': 'ğ', 'Ğ': 'G', 'G': 'Ğ',
            'ı': 'i', 'i': 'ı', 'I': 'İ', 'İ': 'I',
            'ü': 'u', 'u': 'ü', 'Ü': 'U', 'U': 'Ü',
            'ş': 's', 's': 'ş', 'Ş': 'S', 'S': 'Ş',
            'ç': 'c', 'c': 'ç', 'Ç': 'C', 'C': 'Ç'
        }
        variations = {text}
        lower_text = text.lower()
        variations.add(lower_text)
        upper_text = text.upper()
        variations.add(upper_text)
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

    if clean_search:
        kod_filter = Q(kodlar__icontains=clean_search)
        olcu_filter = Q(olcu__icontains=clean_search)
        melumat_filter = Q(melumat__icontains=clean_search)
        def clean_code(val):
            return re.sub(r'[^a-zA-Z0-9]', '', val.lower()) if val else ''
        brend_kod_ids = [m.id for m in queryset if clean_code(search_query) in clean_code(m.brend_kod)]
        brend_kod_filter = Q(id__in=brend_kod_ids)
        if search_words:
            ad_filters = []
            for word in search_words:
                word_variations = normalize_azerbaijani_chars(word)
                word_filter = reduce(or_, [Q(adi__icontains=variation) for variation in word_variations])
                melumat_word_filter = reduce(or_, [Q(melumat__icontains=variation) for variation in word_variations])
                avtomobil_filter = reduce(or_, [Q(avtomobil__adi__icontains=variation) for variation in word_variations])
                firma_filter = reduce(or_, [Q(firma__adi__icontains=variation) for variation in word_variations])
                ad_filters.append(word_filter | melumat_word_filter | avtomobil_filter | firma_filter)
            ad_filter = reduce(and_, ad_filters)
            searchtext_and_filter = reduce(
                and_,
                [reduce(or_, [Q(search_text__icontains=variation) for variation in normalize_azerbaijani_chars(word)]) for word in search_words]
            )
            queryset = queryset.filter(
                kod_filter | olcu_filter | melumat_filter | brend_kod_filter | ad_filter | searchtext_and_filter
            )
        else:
            queryset = queryset.filter(
                kod_filter | olcu_filter | melumat_filter | brend_kod_filter
            )
    if order_by_wilson:
        queryset = queryset.annotate(
            sum_rating=Sum('ratings__rating'),
            rating_count=Count('ratings'),
            avg_rating=Avg('ratings__rating'),
        ).order_by('-rating_count', '-avg_rating', '-id')
    return queryset