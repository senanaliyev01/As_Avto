from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Message
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # İstifadəçinin təsdiq statusunu yoxla
            if not user.profile.is_approved:
                messages.error(request, 
                    'Hesabınız hələ admin tərəfindən təsdiqlənməyib.',
                    extra_tags='auth-error')
                return render(request, 'login.html')
                
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 
                'İstifadəçi adı və ya şifrə yanlışdır.',
                extra_tags='auth-error')
                
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
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Şifrəniz uğurla dəyişdirildi!')
            return redirect('profile')
        else:
            messages.error(request, 'Xəta baş verdi. Zəhmət olmasa məlumatları düzgün daxil edin.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form})

@require_POST
def logout_view(request):
    logout(request)
    return HttpResponse(status=200)

@login_required
def get_messages(request, receiver_id):
    try:
        receiver = User.objects.get(id=receiver_id)
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).order_by('created_at')
        
        # Oxunmamış mesajları oxunmuş et
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        return JsonResponse([{
            'id': msg.id,
            'content': msg.audio_file.url if msg.message_type == 'audio' else msg.content,
            'type': msg.message_type,
            'sender': msg.sender.username,
            'is_mine': msg.sender == request.user,
            'is_read': msg.is_read,
            'is_delivered': msg.is_delivered
        } for msg in messages], safe=False)
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'İstifadəçi tapılmadı'}, status=404)

@login_required
@require_POST
def send_message(request):
    try:
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        message_type = request.POST.get('message_type', 'text')
        
        if not receiver_id or not content:
            return JsonResponse({
                'status': 'error',
                'message': 'Məlumatlar tam deyil'
            })
            
        receiver = User.objects.get(id=receiver_id)
        
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            message_type=message_type,
            is_delivered=True
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'type': message.message_type,
                'created_at': message.created_at.isoformat(),
                'is_mine': True,
                'is_delivered': True,
                'is_read': False
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@login_required
def get_chat_users(request):
    # Admin və normal istifadəçiləri əldə et
    admin_users = User.objects.filter(is_staff=True).exclude(id=request.user.id)
    normal_users = User.objects.filter(is_staff=False).exclude(id=request.user.id)
    
    response_data = {
        'is_admin': request.user.is_staff,
        'admins': [],
        'users': []
    }
    
    # Admin siyahısını hazırla
    for user in admin_users:
        unread_count = Message.objects.filter(
            sender=user,
            receiver=request.user,
            is_read=False
        ).count()
        
        response_data['admins'].append({
            'id': user.id,
            'username': user.username,
            'unread_count': unread_count,
            'is_admin': True
        })
    
    # Əgər current user admindisə, normal istifadəçiləri də əlavə et
    if request.user.is_staff:
        for user in normal_users:
            unread_count = Message.objects.filter(
                sender=user,
                receiver=request.user,
                is_read=False
            ).count()
            
            response_data['users'].append({
                'id': user.id,
                'username': user.username,
                'unread_count': unread_count,
                'is_admin': False
            })
    
    return JsonResponse(response_data)

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
                'message': 'Qeydiyyat uğurla tamamlandı! Zəhmət olmasa admin təsdiqini gözləyin.'
            })

        except Exception as e:
            print(f"Qeydiyyat zamanı xəta: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })

    return render(request, 'register.html')

@login_required
@csrf_exempt
def send_audio_message(request):
    if request.method == 'POST':
        try:
            receiver_id = request.POST.get('receiver_id')
            audio_file = request.FILES.get('audio')
            
            if not audio_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Səs faylı tapılmadı'
                })
                
            try:
                receiver = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'İstifadəçi tapılmadı'
                })
            
            # Səs mesajını yarat
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                audio_file=audio_file,
                message_type='audio',
                is_delivered=True
            )
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.audio_file.url,
                    'type': 'audio',
                    'sender': message.sender.username,
                    'is_mine': True,
                    'is_delivered': True,
                    'is_read': False
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Yanlış sorğu metodu'
    })

@login_required
def delete_message(request, message_id):
    if request.method == 'DELETE':
        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.delete()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Mesaj tapılmadı'
            }, status=404)
    return JsonResponse({
        'status': 'error',
        'message': 'Yanlış sorğu metodu'
    })