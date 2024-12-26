from pickle import FALSE

from django.db import models
from django.contrib.auth.models import User

class Kateqoriya(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi

class Brend(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi

class Marka(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi

class Mehsul(models.Model):
    adi = models.CharField(max_length=255)
    kateqoriya = models.ForeignKey(Kateqoriya, on_delete=models.CASCADE)
    brend = models.ForeignKey(Brend, on_delete=models.CASCADE)
    marka = models.ForeignKey(Marka, on_delete=models.CASCADE)
    brend_kod = models.CharField(max_length=50, unique=True)
    oem_kod = models.CharField(max_length=50, unique=True)
    stok = models.IntegerField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.adi

class Sebet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.mehsul.adi}"


from django.db import models
from django.contrib.auth.models import User

class Sifaris(models.Model):
    STATUS_CHOICES = [
        ('gozleyir', 'Gözləyir'),
        ('hazirlanir', 'Hazırlanır'),
        ('yoldadir', 'Yoldadır'),
        ('catdirildi', 'Çatdırıldı'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    cemi_mebleg = models.DecimalField(max_digits=10, decimal_places=2)
    odenilen_mebleg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tarix = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='gozleyir')
    tamamlandi = models.BooleanField(default=False)

    def borc(self):
        return self.cemi_mebleg - self.odenilen_mebleg

    def __str__(self):
        return f"Sifariş {self.id} - {self.tarix}"


class SifarisMehsul(models.Model):
    sifaris = models.ForeignKey(Sifaris, related_name='mehsullar', on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.mehsul.adi} - {self.mehsul.kateqoriya} - {self.mehsul.brend_kod} - {self.mehsul.oem_kod} - {self.miqdar} ədəd"

    def total_price(self):
        return self.miqdar * self.qiymet


