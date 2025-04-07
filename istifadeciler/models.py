from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random
import string

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ad = models.CharField(max_length=50, blank=True, null=True)
    soyad = models.CharField(max_length=50, blank=True, null=True)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    unvan = models.TextField(blank=True, null=True)
    sekil = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png')
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} Profili'
    
    class Meta:
        verbose_name = 'Profillər'
        verbose_name_plural = 'Profillər'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

class LoginCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        # 6 xanalı təsadüfi kod yaratmaq (hərf və rəqəmlər)
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(10))

    def is_valid(self):
        # Kodun 3 dəqiqə ərzində aktiv olmasını yoxlayır
        now = timezone.now()
        expiration_time = self.created_at + timezone.timedelta(minutes=3)
        return not self.is_used and now <= expiration_time

    class Meta:
        verbose_name = 'Giriş Kodları'
        verbose_name_plural = 'Giriş Kodları'

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Yeni sahələr
    message_type = models.CharField(max_length=20, choices=[
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
        ('link', 'Link')
    ], default='text')
    
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)  # Fayl ölçüsü bayt cinsindən
    file_url = models.URLField(max_length=500, null=True, blank=True)  # Link üçün
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.content[:50]}"
    
    def get_file_size_display(self):
        if not self.file_size:
            return "0 B"
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Mesajlar'
        verbose_name_plural = 'Mesajlar'

class ChatGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Qrup adı")
    description = models.TextField(blank=True, null=True, verbose_name="Qrup təsviri")
    avatar = models.ImageField(upload_to='group_avatars/', default='group_avatars/default_group.png', verbose_name="Qrup avatarı")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', verbose_name="Yaradıcı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaradılma tarixi")
    is_active = models.BooleanField(default=True, verbose_name="Aktivdir")

    class Meta:
        verbose_name = 'Chat Qrupu'
        verbose_name_plural = 'Chat Qrupları'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='members', verbose_name="Qrup")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships', verbose_name="İstifadəçi")
    is_admin = models.BooleanField(default=False, verbose_name="Qrup adminidir")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Qoşulma tarixi")
    
    class Meta:
        verbose_name = 'Qrup üzvü'
        verbose_name_plural = 'Qrup üzvləri'
        unique_together = ['group', 'user']  # Bir istifadəçi eyni qrupa bir dəfə əlavə oluna bilər
        
    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages', verbose_name="Qrup")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages', verbose_name="Göndərən")
    content = models.TextField(verbose_name="Məzmun")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Göndərilmə tarixi")
    
    class Meta:
        verbose_name = 'Qrup mesajı'
        verbose_name_plural = 'Qrup mesajları'
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.sender.username} - {self.group.name}: {self.content[:20]}..."