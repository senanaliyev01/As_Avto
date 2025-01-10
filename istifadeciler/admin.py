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
    list_display = ('sender', 'receiver', 'short_content', 'message_type', 'created_at', 'is_read', 'is_delivered')
    list_filter = ('message_type', 'is_read', 'is_delivered', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def short_content(self, obj):
        if obj.message_type == 'audio':
            return 'Audio Message'
        elif obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return 'Empty message'
    
    short_content.short_description = 'Message Content'
