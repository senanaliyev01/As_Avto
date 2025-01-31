from django.db import models

# Create your models here.

class Car(models.Model):
    CAR_TYPE_CHOICES = [
        ('rent', 'İcarə'),
        ('sale', 'Satış'),
    ]

    name = models.CharField(max_length=100, verbose_name='Maşının Adı')
    engine_capacity = models.FloatField(verbose_name='Motor Həcmi (L)')
    car_type = models.CharField(max_length=4, choices=CAR_TYPE_CHOICES, verbose_name='İcarə/Satış')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Satış Qiyməti')
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='İcarə Qiyməti')
    description = models.TextField(verbose_name='Haqqında')
    images = models.ManyToManyField('CarImage', related_name='cars', blank=True)

    def __str__(self):
        return self.name

class CarImage(models.Model):
    image = models.ImageField(upload_to='cars/', verbose_name='Maşının Şəkli')

    def __str__(self):
        return f"Şəkil - {self.id}"
