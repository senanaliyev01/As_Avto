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
from django.urls import reverse
import re
from esasevim.views import esasevim

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
def get_messages(request, receiver_id):
    try:
        print(f"get_messages called: receiver_id={receiver_id}") # Debug üçün
        
        receiver = User.objects.get(id=receiver_id)
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).order_by('created_at')
        
        print(f"Found {messages.count()} messages") # Debug üçün
        
        # Oxunmamış mesajları oxunmuş et
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        response_data = [{
            'id': msg.id,
            'content': msg.content,
            'sender': msg.sender.username,
            'is_mine': msg.sender == request.user,
            'is_read': msg.is_read,
            'is_delivered': msg.is_delivered
        } for msg in messages]
        
        return JsonResponse(response_data, safe=False)
        
    except User.DoesNotExist:
        print(f"İstifadəçi tapılmadı: receiver_id={receiver_id}")
        return JsonResponse({'error': 'İstifadəçi tapılmadı'}, status=404)
    except Exception as e:
        print(f"get_messages funksiyasında xəta: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            receiver_id = request.POST.get('receiver_id')
            content = request.POST.get('content')
            
            print(f"send_message called: receiver_id={receiver_id}, content={content}") # Debug üçün
            
            if not content:
                return JsonResponse({'status': 'error', 'message': 'Mesaj boş ola bilməz'})
                
            receiver = User.objects.get(id=receiver_id)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                is_delivered=True  # Avtomatik çatdırıldı kimi qeyd et
            )
            
            print(f"Mesaj yaradıldı: id={message.id}") # Debug üçün
            
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'is_mine': True,
                    'is_delivered': True,
                    'is_read': False
                }
            })
            
        except User.DoesNotExist:
            print(f"İstifadəçi tapılmadı: receiver_id={receiver_id}")
            return JsonResponse({'status': 'error', 'message': 'İstifadəçi tapılmadı'})
        except Exception as e:
            print(f"send_message funksiyasında xəta: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Yanlış sorğu metodu'})

@login_required
def get_chat_users(request):
    """
    Chat üçün istifadəçiləri qaytarır
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Admin istifadəçilər
        admins = User.objects.filter(is_staff=True).exclude(id=request.user.id)
        admin_data = []
        
        for admin in admins:
            # Oxunmamış mesajların sayını hesabla
            unread_count = Message.objects.filter(
                sender=admin,
                receiver=request.user,
                is_read=False
            ).count()
            
            # Profil şəklini əldə et
            profile_image = None
            try:
                if hasattr(admin, 'profile') and admin.profile.sekil:
                    profile_image = admin.profile.sekil.url
            except:
                pass
            
            admin_data.append({
                'id': admin.id,
                'username': admin.username,
                'is_admin': True,
                'unread_count': unread_count,
                'is_online': True,  # Burada online statusu əlavə edə bilərsiniz
                'sekil': profile_image
            })
        
        # Normal istifadəçilər (yalnız adminlər üçün)
        users_data = []
        if request.user.is_staff:
            users = User.objects.filter(is_staff=False)
            
            for user in users:
                # Oxunmamış mesajların sayını hesabla
                unread_count = Message.objects.filter(
                    sender=user,
                    receiver=request.user,
                    is_read=False
                ).count()
                
                # Profil şəklini əldə et
                profile_image = None
                try:
                    if hasattr(user, 'profile') and user.profile.sekil:
                        profile_image = user.profile.sekil.url
                except:
                    pass
                
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'is_admin': False,
                    'unread_count': unread_count,
                    'is_online': False,  # Burada online statusu əlavə edə bilərsiniz
                    'sekil': profile_image
                })
        
        return JsonResponse({
            'admins': admin_data,
            'users': users_data
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)