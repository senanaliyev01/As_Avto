from django.db import models

# Create your models here.

class Slider(models.Model):
    basliq = models.CharField(max_length=200, verbose_name="Başlıq")
    alt_basliq = models.CharField(max_length=300, blank=True, verbose_name="Alt başlıq")
    sekil = models.ImageField(upload_to='slider/', verbose_name="Şəkil")

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliderlər"

    def __str__(self):
        return self.basliq
