from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Message, LoginCode, EmailVerification
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
import re
from esasevim.views import esasevim
from django.core.mail import send_mail
from django.conf import settings
import random
import string

def check_code_expiration(request):
    """Təhlükəsizlik kodunun müddətini yoxlayır"""
    if request.method == 'GET':
        user_id = request.session.get('temp_user_id')
        if not user_id:
            return JsonResponse({'expired': True})
        
        try:
            user = User.objects.get(id=user_id)
            login_code = LoginCode.objects.filter(
                user=user,
                is_used=False
            ).latest('created_at')
            
            now = timezone.now()
            expiration_time = login_code.created_at + timezone.timedelta(minutes=3)
            remaining_seconds = int((expiration_time - now).total_seconds())
            
            if remaining_seconds <= 0:
                # Sessiyanı təmizlə
                request.session.pop('temp_user_id', None)
                request.session.pop('temp_remember_me', None)
                return JsonResponse({
                    'expired': True,
                    'message': 'Təhlükəsizlik kodunun müddəti bitib.'
                })
            
            return JsonResponse({
                'expired': False,
                'remaining_seconds': remaining_seconds
            })
            
        except (User.DoesNotExist, LoginCode.DoesNotExist):
            return JsonResponse({'expired': True})
    
    return JsonResponse({'error': 'Invalid request method'})

def login_view(request):
    if request.user.is_authenticated:
        if not request.session.get('remember_me', False) and request.session.get_expiry_age() <= 0:
            logout(request)
            messages.info(request, 'Sessiya müddəti bitdi. Zəhmət olmasa yenidən daxil olun.')
            return redirect('login')
        return redirect('esasevim:main')

    if request.method == 'POST':
        if 'code' in request.POST:
            # Təhlükəsizlik kodunun yoxlanması
            code = request.POST.get('code')
            user_id = request.session.get('temp_user_id')
            
            if not user_id:
                messages.error(request, 'Sessiya müddəti bitib. Zəhmət olmasa yenidən cəhd edin.')
                return render(request, 'login.html', {'show_code_input': False})
            
            try:
                user = User.objects.get(id=user_id)
                login_code = LoginCode.objects.filter(user=user, code=code, is_used=False).latest('created_at')
                
                if login_code.is_valid():
                    login_code.is_used = True
                    login_code.save()
                    
                    login(request, user)
                    
                    remember_me = request.session.get('temp_remember_me', False)
                    if remember_me:
                        request.session.set_expiry(31536000)  # 365 gün
                        request.session['remember_me'] = True
                    else:
                        request.session.set_expiry(0)
                        request.session['remember_me'] = False
                    
                    # Təmizlə
                    request.session.pop('temp_user_id', None)
                    request.session.pop('temp_remember_me', None)
                    
                    next_url = request.session.pop('next', None)
                    if next_url:
                        return redirect(next_url)
                    return redirect('esasevim:main')
                else:
                    messages.error(request, 'Kod etibarsızdır və ya müddəti bitib.')
            except User.DoesNotExist:
                messages.error(request, 'İstifadəçi tapılmadı.')
            except LoginCode.DoesNotExist:
                messages.error(request, 'Yanlış və ya etibarsız kod.')
            except Exception as e:
                messages.error(request, f'Xəta baş verdi: {str(e)}')
            
            return render(request, 'login.html', {'show_code_input': True})
        else:
            # İlkin giriş məlumatlarının yoxlanması
            username = request.POST.get('username')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me') == 'on'
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                try:
                    # Təhlükəsizlik kodu yarat və saxla
                    code = LoginCode.generate_code()
                    login_code = LoginCode.objects.create(user=user, code=code)
                    
                    # Müvəqqəti məlumatları sessiyada saxla
                    request.session['temp_user_id'] = user.id
                    request.session['temp_remember_me'] = remember_me
                    
                    if request.GET.get('next'):
                        request.session['next'] = request.GET['next']
                    
                    messages.info(request, 'Təhlükəsizlik kodu göndərildi. Zəhmət olmasa administratorla əlaqə saxlayın.')
                    return render(request, 'login.html', {
                        'show_code_input': True,
                        'code_created_at': login_code.created_at.isoformat()
                    })
                except Exception as e:
                    messages.error(request, f'Təhlükəsizlik kodu yaradılarkən xəta baş verdi: {str(e)}')
                    return render(request, 'login.html', {'show_code_input': False})
            else:
                messages.error(request, 'İstifadəçi adı və ya şifrə yanlışdır!')
    
    return render(request, 'login.html', {'show_code_input': False})

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
                password=password,
                is_active=False  # Email təsdiqlənənə qədər hesab aktiv olmayacaq
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
            
            # Email təsdiq kodu yarat və göndər
            verification_code = EmailVerification.generate_code()
            EmailVerification.objects.create(
                user=user,
                code=verification_code,
                email=email
            )
            
            # Email göndər
            email_sent = send_verification_email(user, email, verification_code)
            
            if not email_sent:
                # Email göndərilə bilmədisə, istifadəçini sil
                user.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email göndərilə bilmədi. Zəhmət olmasa daha sonra yenidən cəhd edin.'
                })

            # Təsdiq səhifəsinə yönləndir
            request.session['pending_verification_email'] = email
            
            return JsonResponse({
                'status': 'success',
                'message': 'Qeydiyyatınız uğurla tamamlandı! Email ünvanınıza təsdiq kodu göndərildi. Zəhmət olmasa emailinizi yoxlayın.',
                'redirect': reverse('verify_email')
            })

        except Exception as e:
            print(f"Qeydiyyat zamanı xəta: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })

    return render(request, 'register.html')

def verify_email(request):
    """Email təsdiqi səhifəsi"""
    email = request.session.get('pending_verification_email')
    
    if not email:
        messages.error(request, 'Təsdiq ediləcək email tapılmadı.')
        return redirect('login')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        
        try:
            verification = EmailVerification.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if verification.is_valid():
                user = verification.user
                user.is_active = True
                user.save()
                
                verification.is_used = True
                verification.save()
                
                # Sessiyadan təmizlə
                request.session.pop('pending_verification_email', None)
                
                messages.success(request, 'Email ünvanınız uğurla təsdiqləndi! İndi daxil ola bilərsiniz.')
                return redirect('login')
            else:
                messages.error(request, 'Təsdiq kodu etibarsızdır və ya müddəti bitib.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Yanlış təsdiq kodu.')
    
    return render(request, 'verify_email.html', {'email': email})

def resend_verification_email(request):
    """Təsdiq emailini yenidən göndərir"""
    email = request.session.get('pending_verification_email')
    
    if not email:
        return JsonResponse({
            'status': 'error',
            'message': 'Təsdiq ediləcək email tapılmadı.'
        })
    
    try:
        user = User.objects.get(email=email, is_active=False)
        
        # Köhnə kodları deaktiv et
        EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Yeni kod yarat və göndər
        verification_code = EmailVerification.generate_code()
        EmailVerification.objects.create(
            user=user,
            code=verification_code,
            email=email
        )
        
        # Email göndər
        email_sent = send_verification_email(user, email, verification_code)
        
        if not email_sent:
            return JsonResponse({
                'status': 'error',
                'message': 'Email göndərilə bilmədi. Zəhmət olmasa daha sonra yenidən cəhd edin.'
            })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Təsdiq kodu yenidən göndərildi. Zəhmət olmasa emailinizi yoxlayın.'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'İstifadəçi tapılmadı.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Xəta baş verdi: {str(e)}'
        })

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
    print("get_chat_users called") # Debug üçün
    
    try:
        # Admin və normal istifadəçiləri əldə et
        admin_users = User.objects.filter(is_staff=True).exclude(id=request.user.id)
        normal_users = User.objects.filter(is_staff=False).exclude(id=request.user.id)
        
        print(f"Found {admin_users.count()} admins and {normal_users.count()} users") # Debug üçün
        
        # Admin və normal istifadəçilər üçün məlumatları hazırla
        admins = []
        users = []
        
        for user in admin_users:
            try:
                unread_count = Message.objects.filter(
                    sender=user,
                    receiver=request.user,
                    is_read=False
                ).count()
                
                admins.append({
                    'id': user.id,
                    'username': user.username,
                    'unread_count': unread_count,
                    'is_admin': True
                })
            except Exception as e:
                print(f"Admin istifadəçi məlumatları hazırlanarkən xəta: {str(e)}")
        
        for user in normal_users:
            try:
                unread_count = Message.objects.filter(
                    sender=user,
                    receiver=request.user,
                    is_read=False
                ).count()
                
                users.append({
                    'id': user.id,
                    'username': user.username,
                    'unread_count': unread_count,
                    'is_admin': False
                })
            except Exception as e:
                print(f"Normal istifadəçi məlumatları hazırlanarkən xəta: {str(e)}")
        
        response_data = {
            'admins': admins,
            'users': users
        }
        print("Sending response:", response_data) # Debug üçün
        return JsonResponse(response_data)
    except Exception as e:
        print(f"get_chat_users funksiyasında xəta: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def send_verification_email(user, email, code, is_password_reset=False):
    """Email vasitəsilə təsdiq kodu göndərir"""
    subject = "Şifrə Sıfırlama Kodu" if is_password_reset else "Email Təsdiq Kodu"
    
    message = f"""
    Hörmətli {user.username},
    
    {"Şifrənizi sıfırlamaq" if is_password_reset else "Email ünvanınızı təsdiqləmək"} üçün kodunuz: {code}
    
    Bu kod 10 dəqiqə ərzində etibarlıdır.
    
    Əgər bu sorğunu siz göndərməmisinizsə, bu emaili nəzərə almayın.
    
    Hörmətlə,
    AS AVTO Komandası
    """
    
    from_email = "senan.eliyev.9997@gmail.com"
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except Exception as e:
        print(f"Email göndərmə xətası: {str(e)}")
        return False

def forgot_password(request):
    """Şifrə sıfırlama səhifəsi"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Köhnə kodları deaktiv et
            EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Yeni kod yarat və göndər
            reset_code = EmailVerification.generate_code()
            EmailVerification.objects.create(
                user=user,
                code=reset_code,
                email=email
            )
            
            # Email göndər
            email_sent = send_verification_email(user, email, reset_code, is_password_reset=True)
            
            if not email_sent:
                messages.error(request, 'Email göndərilə bilmədi. Zəhmət olmasa daha sonra yenidən cəhd edin.')
                return render(request, 'forgot_password.html')
            
            # Sessiyada saxla
            request.session['reset_password_email'] = email
            
            messages.success(request, 'Şifrə sıfırlama kodu email ünvanınıza göndərildi.')
            return redirect('reset_password')
            
        except User.DoesNotExist:
            messages.error(request, 'Bu email ünvanı ilə qeydiyyatdan keçmiş istifadəçi tapılmadı.')
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
    
    return render(request, 'forgot_password.html')

def reset_password(request):
    """Şifrə sıfırlama kodu təsdiqi və yeni şifrə təyini"""
    email = request.session.get('reset_password_email')
    
    if not email:
        messages.error(request, 'Şifrə sıfırlama sorğusu tapılmadı.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Şifrələrin uyğunluğunu yoxla
        if new_password != confirm_password:
            messages.error(request, 'Şifrələr uyğun gəlmir!')
            return render(request, 'reset_password.html', {'email': email})
        
        # Şifrə tələblərini yoxla
        if len(new_password) < 8:
            messages.error(request, 'Şifrə ən azı 8 simvol olmalıdır!')
            return render(request, 'reset_password.html', {'email': email})
        
        if not re.search(r'[A-Z]', new_password):
            messages.error(request, 'Şifrədə ən azı 1 böyük hərf olmalıdır!')
            return render(request, 'reset_password.html', {'email': email})
        
        if not re.search(r'[0-9]', new_password):
            messages.error(request, 'Şifrədə ən azı 1 rəqəm olmalıdır!')
            return render(request, 'reset_password.html', {'email': email})
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            messages.error(request, 'Şifrədə ən azı 1 xüsusi simvol olmalıdır!')
            return render(request, 'reset_password.html', {'email': email})
        
        try:
            verification = EmailVerification.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).latest('created_at')
            
            if verification.is_valid():
                user = verification.user
                user.set_password(new_password)
                user.save()
                
                verification.is_used = True
                verification.save()
                
                # Sessiyadan təmizlə
                request.session.pop('reset_password_email', None)
                
                messages.success(request, 'Şifrəniz uğurla yeniləndi! İndi yeni şifrənizlə daxil ola bilərsiniz.')
                return redirect('login')
            else:
                messages.error(request, 'Təsdiq kodu etibarsızdır və ya müddəti bitib.')
        except EmailVerification.DoesNotExist:
            messages.error(request, 'Yanlış təsdiq kodu.')
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
    
    return render(request, 'reset_password.html', {'email': email})

def resend_reset_code(request):
    """Şifrə sıfırlama kodunu yenidən göndərir"""
    email = request.session.get('reset_password_email')
    
    if not email:
        return JsonResponse({
            'status': 'error',
            'message': 'Şifrə sıfırlama sorğusu tapılmadı.'
        })
    
    try:
        user = User.objects.get(email=email)
        
        # Köhnə kodları deaktiv et
        EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Yeni kod yarat və göndər
        reset_code = EmailVerification.generate_code()
        EmailVerification.objects.create(
            user=user,
            code=reset_code,
            email=email
        )
        
        # Email göndər
        email_sent = send_verification_email(user, email, reset_code, is_password_reset=True)
        
        if not email_sent:
            return JsonResponse({
                'status': 'error',
                'message': 'Email göndərilə bilmədi. Zəhmət olmasa daha sonra yenidən cəhd edin.'
            })
        
        return JsonResponse({
            'status': 'success',
            'message': 'Şifrə sıfırlama kodu yenidən göndərildi. Zəhmət olmasa emailinizi yoxlayın.'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'İstifadəçi tapılmadı.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Xəta baş verdi: {str(e)}'
        })