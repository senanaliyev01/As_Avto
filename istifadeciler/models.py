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
