from django.db import models

# Create your models here.

class MainSlider(models.Model):
    sekil = models.ImageField(upload_to='slider/', verbose_name='Şəkil')
    basliq = models.CharField(max_length=200, verbose_name='Başlıq')
    alt_basliq = models.CharField(max_length=300, verbose_name='Alt Başlıq')
    aktiv = models.BooleanField(default=True, verbose_name='Aktiv')
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Əsas Slider'
        verbose_name_plural = 'Əsas Sliderlər'
        ordering = ['-yaradilma_tarixi']

    def __str__(self):
        return self.basliq
