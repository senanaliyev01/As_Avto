from django.db import models

# Create your models here.

class HeroSlider(models.Model):
    sekil = models.ImageField(upload_to='hero_slider/', verbose_name='Slider Şəkli')
    basliq = models.CharField(max_length=200, verbose_name='Başlıq')
    alt_basliq = models.CharField(max_length=300, verbose_name='Alt Başlıq')
    aktiv = models.BooleanField(default=True, verbose_name='Aktiv')
    sira = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    
    class Meta:
        verbose_name = 'Hero Slider'
        verbose_name_plural = 'Hero Slider'
        ordering = ['sira']
    
    def __str__(self):
        return self.basliq
