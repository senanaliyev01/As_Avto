from django.db import models

# Create your models here.

class HeroSlide(models.Model):
    sekil = models.ImageField(upload_to='hero_slides/', verbose_name='Şəkil')
    basliq = models.CharField(max_length=200, verbose_name='Başlıq', null=True, blank=True)
    alt_basliq = models.CharField(max_length=300, verbose_name='Alt Başlıq', null=True, blank=True)
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
        ordering = ['-yaradilma_tarixi']
    
    def __str__(self):
        return self.basliq
