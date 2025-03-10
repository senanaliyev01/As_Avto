from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Profile, Message, LoginCode

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'soyad', 'telefon')
    search_fields = ('user__username', 'ad', 'soyad', 'telefon')

@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_used', 'is_valid_status')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'code')
    readonly_fields = ('created_at',)
    
    def is_valid_status(self, obj):
        is_valid = obj.is_valid()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if is_valid else 'red',
            'Aktiv' if is_valid else 'Bitib'
        )
    is_valid_status.short_description = 'Status'

class CustomUserAdmin(admin.ModelAdmin):
    def user_avatar(self, obj):
        # İstifadəçinin profil şəkili varsa, onu göstər, əks halda default şəkil
        profile = Profile.objects.filter(user=obj).first()
        if profile and profile.sekil:
            return format_html('<img src="{}" width="30" class="img-circle elevation-2" />', profile.sekil.url)
        return format_html('<img src="/static/vendor/adminlte/img/user2-160x160.jpg" width="30" class="img-circle elevation-2" />')

    list_display = ("username", "email", "user_avatar")  # Admin paneldə avatar göstərmək üçün

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
        return format_html(
            '<a class="deletelink" href="{}" onclick="return confirm(\'Bu mesajı silmək istədiyinizə əminsiniz?\');">'
            'Sil</a>',
            delete_url
        )
    delete_button.short_description = 'Əməliyyatlar'
    delete_button.allow_tags = True

    def has_add_permission(self, request):
        return False  # Yeni mesaj əlavə etməyə icazə vermə