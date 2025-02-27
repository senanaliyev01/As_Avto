from django.db import models

# Create your models here.

class slider(models.Model):
    sekil = models.ImageField(upload_to='hero_slider/', verbose_name='Şəkil')
    basliq = models.CharField(max_length=200, verbose_name='Başlıq')
    metn = models.TextField(verbose_name='Mətn')

    class Meta:
        verbose_name = 'Slider'
        verbose_name_plural = 'Slider'

    def __str__(self):
        return self.basliq
