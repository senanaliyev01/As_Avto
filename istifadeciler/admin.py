from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Profile, Message, LoginCode
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'soyad', 'telefon')
    search_fields = ('user__username', 'ad', 'soyad', 'telefon')

@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used', 'is_valid_status', 'remaining_time')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)  # Ən son kodlar əvvəldə
    
    def is_valid_status(self, obj):
        is_valid = obj.is_valid()
        return mark_safe(
            '<span style="color: {}; font-weight: bold;">{}</span>'.format(
                'green' if is_valid else 'red',
                'AKTİV' if is_valid else 'BİTİB'
            )
        )
    is_valid_status.short_description = 'Status'

    def remaining_time(self, obj):
        if not obj.is_used:
            now = timezone.now()
            expiration_time = obj.created_at + timezone.timedelta(minutes=3)
            if now <= expiration_time:
                remaining = expiration_time - now
                seconds = int(remaining.total_seconds())
                minutes = seconds // 60
                seconds = seconds % 60
                return mark_safe(
                    '<span style="color: blue;">{:02d}:{:02d}</span>'.format(
                        minutes, seconds
                    )
                )
        return mark_safe('<span style="color: red;">Vaxt bitib</span>')
    remaining_time.short_description = 'Qalan vaxt'

    def has_add_permission(self, request):
        return False  # Əl ilə kod əlavə etməyə 22icaz1ə vermə

    def has_change_permission(self, request, obj=None):
        return False  # Kodları dəyişməyə icazə vermə

class CustomUserAdmin(admin.ModelAdmin):
    def user_avatar(self, obj):
        # İstifadəçinin profil şəkili varsa, onu göstər, əks halda default şəkil
        profile = Profile.objects.filter(user=obj).first()
        if profile and profile.sekil:
            return mark_safe('<img src="{}" width="30" class="img-circle elevation-2" />'.format(profile.sekil.url))
        return mark_safe('<img src="/static/vendor/adminlte/img/user2-160x160.jpg" width="30" class="img-circle elevation-2" />')
    
    def reset_password(self, obj):
        return mark_safe(
            '<a href="{}?user_id={}" class="button" style="background-color: #ff9800; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">Şifrəni Sıfırla</a>'.format(
                reverse('admin:reset_user_password'), obj.id
            )
        )
    reset_password.short_description = 'Şifrə Əməliyyatları'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('reset-password/', self.admin_site.admin_view(self.reset_password_view), name='reset_user_password'),
        ]
        return custom_urls + urls
    
    def reset_password_view(self, request):
        user_id = request.GET.get('user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            # Yeni təsadüfi şifrə yaratmaq (6 simvol)
            import random
            import string
            new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            
            # İstifadəçinin şifrəsini yeniləmək
            user.set_password(new_password)
            user.save()
            
            self.message_user(request, f"İstifadəçi '{user.username}' üçün şifrə sıfırlandı. Yeni şifrə: {new_password}")
            
        return HttpResponseRedirect(reverse('admin:auth_user_changelist'))

    list_display = ("username", "email", "user_avatar", "reset_password")  # Admin paneldə avatar və şifrə sıfırlama düyməsi göstərmək üçün

admin.site.unregister(User)  # Əvvəlki User adminini silirik
admin.site.register(User, CustomUserAdmin)  # Yeni Custom Admini qeydiyyatdan keçiririk

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender_username', 'receiver_username', 'short_content', 'created_at', 'is_read', 'delete_button')
    list_filter = ('is_read', 'created_at', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 50

    def sender_username(self, obj):
        return obj.sender.username
    sender_username.short_description = 'Göndərən'

    def receiver_username(self, obj):
        return obj.receiver.username
    receiver_username.short_description = 'Alan'

    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Mesaj'

    def delete_button(self, obj):
        delete_url = reverse('admin:istifadeciler_message_delete', args=[obj.id])
        return mark_safe(
            '<a class="deletelink" href="{}" onclick="return confirm(\'Bu mesajı silmək istədiyinizə əminsiniz?\');">'
            'Sil</a>'.format(delete_url)
        )
    delete_button.short_description = 'Əməliyyatlar'
    delete_button.allow_tags = True

    def has_add_permission(self, request):
        return False  # Yeni mesaj əlavə etməyə icazə vermə