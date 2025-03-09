from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Message
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from esasevim.views import esasevim
import json
from django.utils import timezone

def login_view(request):
    # Əgər istifadəçi artıq daxil olubsa
    if request.user.is_authenticated:
        # Remember me seçilməyibsə və session müddəti bitibsə
        if not request.session.get('remember_me', False) and request.session.get_expiry_age() <= 0:
            logout(request)
            messages.info(request, 'Sessiya müddəti bitdi. Zəhmət olmasa yenidən daxil olun.')
            return redirect('login')
        # Remember me seçilibsə və ya session aktiv isə ana səhifəyə yönləndir
        return redirect('esasevim:main')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # İstifadəçinin təsdiq statusunu yoxla
            if not user.profile.is_approved:
                messages.error(request, 'Giriş üçün icazəniz yoxdur.')
                return render(request, 'login.html')
                
            login(request, user)
            
            # Remember Me yoxlaması
            if remember_me:
                # 1 illik session
                request.session.set_expiry(31536000)  # 365 gün
                request.session['remember_me'] = True
            else:
                # Browser bağlandıqda session silinəcək
                request.session.set_expiry(0)
                request.session['remember_me'] = False
            
            # Əgər istifadəçi admin panelə giriş etməyə çalışırdısa
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('esasevim:main')
        else:
            messages.error(request, 'İstifadəçi adı və ya şifrə yanlışdır!')
    
    return render(request, 'login.html')

@login_required
def profile(request):
    if request.method == 'POST':
        if request.FILES.get('sekil'):
            try:
                image = request.FILES['sekil']
                
                # Köhnə şəkli sil
                old_image = request.user.profile.sekil
                if old_image and 'default.png' not in str(old_image):
                    try:
                        old_image.delete(save=False)
                    except:
                        pass

                # Yeni şəkli yüklə
                request.user.profile.sekil = image
                request.user.profile.save()

                return JsonResponse({
                    'success': True,
                    'image_url': request.user.profile.sekil.url
                })

            except:
                return JsonResponse({
                    'success': False,
                    'error': 'Şəkil yüklənərkən xəta baş verdi. Yenidən cəhd edin.'
                })
        else:
            # Profil məlumatlarının yenilənməsi
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profil məlumatlarınız uğurla yeniləndi!')
                return redirect('profile')
            else:
                messages.error(request, 'Xəta baş verdi. Zəhmət olmasa məlumatları düzgün daxil edin.')

    # Normal səhifə yükləmə
    context = {
        'user_form': UserUpdateForm(instance=request.user),
        'profile_form': ProfileUpdateForm(instance=request.user.profile)
    }
    return render(request, 'profile.html', context)

@login_required
def password_change(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Boş sahələri yoxla
        if not all([old_password, new_password1, new_password2]):
            messages.error(request, 'Bütün sahələr doldurulmalıdır!')
            return render(request, 'password_change.html')

        # Köhnə şifrəni yoxla
        if not request.user.check_password(old_password):
            messages.error(request, 'Köhnə şifrə düzgün deyil!')
            return render(request, 'password_change.html')

        # Yeni şifrələrin uyğunluğunu yoxla
        if new_password1 != new_password2:
            messages.error(request, 'Yeni şifrələr uyğun gəlmir!')
            return render(request, 'password_change.html')

        # Şifrə tələblərini yoxla
        if len(new_password1) < 8:
            messages.error(request, 'Şifrə ən azı 8 simvol olmalıdır!')
            return render(request, 'password_change.html')

        if not any(char.isupper() for char in new_password1):
            messages.error(request, 'Şifrədə ən azı 1 böyük hərf olmalıdır!')
            return render(request, 'password_change.html')

        if not any(char.islower() for char in new_password1):
            messages.error(request, 'Şifrədə ən azı 1 kiçik hərf olmalıdır!')
            return render(request, 'password_change.html')

        if not any(char.isdigit() for char in new_password1):
            messages.error(request, 'Şifrədə ən azı 1 rəqəm olmalıdır!')
            return render(request, 'password_change.html')

        if not any(char in '!@#$%^&*(),.?":{}|<>' for char in new_password1):
            messages.error(request, 'Şifrədə ən azı 1 xüsusi simvol olmalıdır!')
            return render(request, 'password_change.html')

        # Köhnə və yeni şifrənin eyni olmamasını yoxla
        if old_password == new_password1:
            messages.error(request, 'Yeni şifrə köhnə şifrə ilə eyni ola bilməz!')
            return render(request, 'password_change.html')

        try:
            # Şifrəni yenilə
            request.user.set_password(new_password1)
            request.user.save()
            
            # Sessiyani yenilə
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Şifrəniz uğurla dəyişdirildi!')
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
            return render(request, 'password_change.html')

    return render(request, 'password_change.html')

@require_POST
def logout_view(request):
    logout(request)
    response = HttpResponse(status=200)
    response['Cache-Control'] = 'no-store'  # Cache-i təmizləmək üçün
    return response

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            # Məlumatları əldə et
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            ad = request.POST.get('ad')
            soyad = request.POST.get('soyad')
            telefon = request.POST.get('telefon')
            unvan = request.POST.get('unvan')

            print(f"Qəbul edilən məlumatlar: username={username}, email={email}, ad={ad}, soyad={soyad}, telefon={telefon}")

            # Boş sahələri yoxla
            if not all([username, email, password, confirm_password, ad, soyad, telefon, unvan]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bütün sahələr doldurulmalıdır!'
                })
                     
                 
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return JsonResponse({
                    'status': 'error',
                    'message': 'İstifadəçi adı yalnız İngilis hərfləri, rəqəm və alt xətt (_) simvolundan ibarət ola bilər!'
                })


            # İstifadəçi adının mövcudluğunu yoxla
            if User.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bu istifadəçi adı artıq mövcuddur!'
                })

            # Email-in mövcudluğunu yoxla
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Bu email artıq istifadə olunub!'
                })

            # Şifrələrin uyğunluğunu yoxla
            if password != confirm_password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şifrələr uyğun gəlmir!'
                })

            # Şifrə tələblərini yoxla
            if len(password) < 8:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şifrə ən azı 8 simvol olmalıdır!'
                })

            if not re.search(r'[A-Z]', password):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şifrədə ən azı 1 böyük hərf olmalıdır!'
                })

            if not re.search(r'[0-9]', password):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şifrədə ən azı 1 rəqəm olmalıdır!'
                })

            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şifrədə ən azı 1 xüsusi simvol olmalıdır!'
                })

            # İstifadəçini yarat
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            print(f"İstifadəçi yaradıldı: {user.username}")

            # Profili yenilə
            profile = user.profile
            profile.ad = ad
            profile.soyad = soyad
            profile.telefon = telefon
            profile.unvan = unvan
            profile.save()

            print(f"Profil yeniləndi: {profile}")

            return JsonResponse({
                'status': 'success',
                'message': 'Qeydiyyatınız uğurla tamamlandı! Hesabınızın təsdiqi üçün 24 saat ərzində gözləməyinizi xahiş edirik. Sizinlə əməkdaşlıq etməyə hazırıq!'
            })

        except Exception as e:
            print(f"Qeydiyyat zamanı xəta: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })

    return render(request, 'register.html')

@login_required
def get_unread_message_count(request):
    """İstifadəçinin oxunmamış mesajlarının sayını qaytarır"""
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def get_chat_list(request):
    """İstifadəçinin söhbət siyahısını qaytarır"""
    user = request.user
    
    # Admin istifadəçilər üçün bütün istifadəçiləri göstər
    if user.is_staff:
        # Mesaj göndərmiş və ya qəbul etmiş bütün istifadəçiləri əldə et
        users = User.objects.exclude(id=user.id).annotate(
            unread_count=Count('sent_messages', filter=Q(sent_messages__receiver=user, sent_messages__is_read=False))
        ).order_by('-unread_count')
    else:
        # Yalnız admin istifadəçiləri göstər
        users = User.objects.filter(is_staff=True).annotate(
            unread_count=Count('sent_messages', filter=Q(sent_messages__receiver=user, sent_messages__is_read=False))
        ).order_by('-unread_count')
    
    chat_list = []
    for chat_user in users:
        # Son mesajı əldə et
        last_message = Message.objects.filter(
            (Q(sender=user) & Q(receiver=chat_user)) | 
            (Q(sender=chat_user) & Q(receiver=user))
        ).order_by('-timestamp').first()
        
        # Oxunmamış mesajların sayını əldə et
        unread_count = Message.objects.filter(
            sender=chat_user, receiver=user, is_read=False
        ).count()
        
        if last_message:
            chat_list.append({
                'id': chat_user.id,
                'username': chat_user.username,
                'full_name': f"{chat_user.profile.ad or ''} {chat_user.profile.soyad or ''}".strip() or chat_user.username,
                'avatar': chat_user.profile.sekil.url if hasattr(chat_user, 'profile') and chat_user.profile.sekil else None,
                'last_message': last_message.content[:30] + '...' if len(last_message.content) > 30 else last_message.content,
                'timestamp': last_message.timestamp.strftime('%H:%M'),
                'unread_count': unread_count,
                'is_online': True  # Burada online statusu əlavə edə bilərsiniz
            })
    
    return JsonResponse({'chat_list': chat_list})

@login_required
def get_messages(request, user_id):
    """İki istifadəçi arasındakı mesajları qaytarır"""
    other_user = get_object_or_404(User, id=user_id)
    user = request.user
    
    # İstifadəçi admin deyilsə və digər istifadəçi də admin deyilsə, xəta qaytarın
    if not user.is_staff and not other_user.is_staff:
        return JsonResponse({'error': 'İcazə yoxdur'}, status=403)
    
    # Mesajları əldə et
    messages_query = Message.objects.filter(
        (Q(sender=user) & Q(receiver=other_user)) | 
        (Q(sender=other_user) & Q(receiver=user))
    ).order_by('timestamp')
    
    # Oxunmamış mesajları oxunmuş kimi işarələ
    Message.objects.filter(sender=other_user, receiver=user, is_read=False).update(is_read=True)
    
    messages_list = []
    for msg in messages_query:
        messages_list.append({
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_sender': msg.sender == user,
            'is_read': msg.is_read
        })
    
    return JsonResponse({
        'messages': messages_list,
        'user': {
            'id': other_user.id,
            'username': other_user.username,
            'full_name': f"{other_user.profile.ad or ''} {other_user.profile.soyad or ''}".strip() or other_user.username,
            'avatar': other_user.profile.sekil.url if hasattr(other_user, 'profile') and other_user.profile.sekil else None,
            'is_online': True  # Burada online statusu əlavə edə bilərsiniz
        }
    })

@login_required
@require_POST
def send_message(request):
    """Yeni mesaj göndərir"""
    data = json.loads(request.body)
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not content or not receiver_id:
        return JsonResponse({'error': 'Mesaj və alıcı tələb olunur'}, status=400)
    
    receiver = get_object_or_404(User, id=receiver_id)
    user = request.user
    
    # İstifadəçi admin deyilsə və digər istifadəçi də admin deyilsə, xəta qaytarın
    if not user.is_staff and not receiver.is_staff:
        return JsonResponse({'error': 'İcazə yoxdur'}, status=403)
    
    # Mesajı yarat
    message = Message.objects.create(
        sender=user,
        receiver=receiver,
        content=content
    )
    
    return JsonResponse({
        'id': message.id,
        'content': message.content,
        'timestamp': message.timestamp.strftime('%H:%M'),
        'is_sender': True,
        'is_read': False
    })

@login_required
@require_POST
def mark_as_read(request, message_id):
    """Mesajı oxunmuş kimi işarələyir"""
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.is_read = True
    message.save()
    return JsonResponse({'success': True})

@login_required
@require_POST
def delete_message(request, message_id):
    """Mesajı silir"""
    # Yalnız admin istifadəçilər mesajları silə bilər
    if not request.user.is_staff:
        return JsonResponse({'error': 'İcazə yoxdur'}, status=403)
    
    message = get_object_or_404(Message, id=message_id)
    message.delete()
    return JsonResponse({'success': True})

@login_required
def chat_view(request):
    """Mesajlaşma səhifəsini göstərir"""
    return render(request, 'chat.html')

