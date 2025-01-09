from django.contrib import admin
from .models import Profile, Message
from django.utils.html import format_html
from django.urls import reverse

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

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'ad', 'soyad', 'telefon')
    search_fields = ('user__username', 'ad', 'soyad', 'telefon')
    list_filter = ('user__is_active',)
