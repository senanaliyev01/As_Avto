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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
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
            'content': msg.content,
            'sender': msg.sender.username,
            'is_mine': msg.sender == request.user,
            'is_read': msg.is_read,
            'is_delivered': msg.is_delivered
        } for msg in messages], safe=False)
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'İstifadəçi tapılmadı'}, status=404)

@login_required
@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Mesaj boş ola bilməz'})
            
        try:
            receiver = User.objects.get(id=receiver_id)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                is_delivered=True  # Avtomatik çatdırıldı kimi qeyd et
            )
            
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
            return JsonResponse({'status': 'error', 'message': 'İstifadəçi tapılmadı'})
            
    return JsonResponse({'status': 'error', 'message': 'Yanlış sorğu metodu'})

@login_required
def get_chat_users(request):
    print("get_chat_users called") # Debug üçün
    
    # Admin və normal istifadəçiləri əldə et
    admin_users = User.objects.filter(is_staff=True).exclude(id=request.user.id)
    normal_users = User.objects.filter(is_staff=False).exclude(id=request.user.id)
    
    print(f"Found {admin_users.count()} admins and {normal_users.count()} users") # Debug üçün
    
    # Admin və normal istifadəçilər üçün məlumatları hazırla
    admins = []
    users = []
    
    for user in admin_users:
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
    
    for user in normal_users:
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
    
    response_data = {
        'admins': admins,
        'users': users
    }
    print("Sending response:", response_data) # Debug üçün
    return JsonResponse(response_data)