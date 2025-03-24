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
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    @classmethod
    def generate_code(cls):
        # 10 xanalı təsadüfi kod yaratmaq (hərf, rəqəm və xüsusi simvollar)
        upper_letters = string.ascii_uppercase
        digits = string.digits
        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Bütün mümkün simvolları birləşdir
        all_chars = upper_letters + digits + special_chars
        
        # Ən azı bir böyük hərf, bir rəqəm və bir xüsusi simvol olmasını təmin et
        code = [
            random.choice(upper_letters),   # Ən azı bir böyük hərf
            random.choice(digits),          # Ən azı bir rəqəm 
            random.choice(special_chars)    # Ən azı bir xüsusi simvol
        ]
        
        # Qalan 7 simvolu təsadüfi seç
        code.extend(random.choice(all_chars) for _ in range(7))
        
        # Simvolların sırasını qarışdır
        random.shuffle(code)
        
        # Simvolları birləşdirib string halına gətir
        return ''.join(code)

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
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.username} to {self.receiver.username}'
    
    class Meta:
        verbose_name = 'Mesajlar'
        verbose_name_plural = 'Mesajlar'