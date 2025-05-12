from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Mehsul, Kateqoriya, Sifaris, SifarisItem, Firma, Avtomobil
from django.db.models import Q
from decimal import Decimal
from django.contrib import messages
import re
from django.http import JsonResponse, HttpResponseNotFound

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
    return render(request, 'base.html', {'new_products': new_products})

@login_required
def products_view(request):
    search_query = request.GET.get('search', '')
    kateqoriya = request.GET.get('kateqoriya', '')
    firma = request.GET.get('firma', '')
    avtomobil = request.GET.get('avtomobil', '')
    
    mehsullar = Mehsul.objects.all().order_by('-id')  # Ən son əlavə edilən məhsullardan başla
    
    if search_query:
        # Xüsusi simvolları və boşluqları təmizlə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query)
        if clean_search:  # Əgər təmizlənmiş axtarış mətni boş deyilsə
            mehsullar = mehsullar.filter(kodlar__icontains=clean_search)
    
    if kateqoriya:
        mehsullar = mehsullar.filter(kateqoriya__adi=kateqoriya)
        
    if firma:
        mehsullar = mehsullar.filter(firma__adi=firma)
        
    if avtomobil:
        mehsullar = mehsullar.filter(avtomobil__adi=avtomobil)
    
    kateqoriyalar = Kateqoriya.objects.all()
    firmalar = Firma.objects.all()
    avtomobiller = Avtomobil.objects.all()
    
    return render(request, 'products.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
        'search_query': search_query,
        'selected_kateqoriya': kateqoriya,
        'selected_firma': firma,
        'selected_avtomobil': avtomobil
    })

@login_required
def cart_view(request):
    if 'cart' not in request.session:
        request.session['cart'] = {}
    
    cart = request.session['cart']
    cart_items = []
    total = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Mehsul, id=product_id)
        subtotal = product.qiymet * Decimal(str(quantity))
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
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
            'message': f'{product.adi} məhsulundan {quantity} ədəd səbətə əlavə edildi!'
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
                    'message': 'Məhsul səbətdən silindi!'
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
    
    return render(request, 'orders.html', {
        'orders': orders,
        'statistics': statistics
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

def order_detail_view(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    order = get_object_or_404(Sifaris, id=order_id, istifadeci=request.user)
    return render(request, 'order_detail.html', {
        'order': order
    })

def search_suggestions(request):
    search_query = request.GET.get('search', '')
    
    if search_query:
        # Xüsusi simvolları və boşluqları təmizlə
        clean_search = re.sub(r'[^a-zA-Z0-9]', '', search_query)
        if clean_search:
            mehsullar = Mehsul.objects.filter(kodlar__icontains=clean_search)[:5]
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
    
    return render(request, 'new_products.html', {
        'mehsullar': mehsullar,
        'kateqoriyalar': kateqoriyalar,
        'firmalar': firmalar,
        'avtomobiller': avtomobiller,
    })
