from django.contrib import admin
from .models import Profile, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'soyad', 'telefon', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('user__username', 'ad', 'soyad', 'telefon')
    list_editable = ('is_approved',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'sender', 'receiver')
    search_fields = ('content', 'sender__username', 'receiver__username')
    ordering = ('-timestamp',)
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Seçilmiş mesajları oxunmuş kimi işarələ"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Seçilmiş mesajları oxunmamış kimi işarələ"

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from istifadeciler.models import Profile  # Modelinizi düzgün import edin

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
