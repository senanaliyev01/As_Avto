from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Mesaj: {self.sender.username} -> {self.receiver.username}'
    
    class Meta:
        verbose_name = 'Mesaj'
        verbose_name_plural = 'Mesajlar'
        ordering = ['-timestamp']

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

