from django.contrib.auth.models import User
from django.db import models
import re
from PIL import Image
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

class Header_Message(models.Model):
    mesaj = models.CharField(max_length=100)
    aktiv = models.BooleanField(default=True, verbose_name='Aktivdir')

    def __str__(self):
        return f"{self.mesaj}"
    
    class Meta:
        verbose_name = 'Header Mesajı'
        verbose_name_plural = 'Header Mesajları'

class Kateqoriya(models.Model):
    adi = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.adi}"
    
    class Meta:
        verbose_name = 'Kateqoriya'
        verbose_name_plural = 'Kateqoriyalar' 


class Firma(models.Model):
    adi = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to='firma_sekilleri',null=True, blank=True)    

    def __str__(self):
        return f"{self.adi}"
    
    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmalar'


class Avtomobil(models.Model):
    adi = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.adi}"
    
    class Meta:
        verbose_name = 'Avtomobil'
        verbose_name_plural = 'Avtomobillər'

class AvtomobilLogo(models.Model):
    avtomobil = models.ForeignKey('Avtomobil', on_delete=models.CASCADE, related_name='logolar')
    sekil = models.ImageField(upload_to='avtomobil_sekilleri')
    def __str__(self):
        return f"{self.avtomobil.adi} logo"

class Vitrin(models.Model):
    nomre = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.nomre}"
    
    class Meta:
        verbose_name = 'Vitrin'
        verbose_name_plural = 'Vitrinlər'

    
class Mehsul(models.Model):
    sahib = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mehsullar', null=True, blank=True, verbose_name='Məhsulun Sahibi')
    adi = models.CharField(max_length=100)
    kateqoriya = models.ForeignKey(Kateqoriya,on_delete=models.CASCADE, null=True, blank=True)
    firma = models.ForeignKey(Firma,on_delete=models.CASCADE)
    avtomobil = models.ForeignKey(Avtomobil,on_delete=models.CASCADE)
    brend_kod = models.CharField(max_length=100)
    oem = models.CharField(max_length=100, null=True,blank=True)
    olcu = models.CharField(max_length=50,null=True,blank=True)
    vitrin = models.ForeignKey(Vitrin,on_delete=models.CASCADE,null=True,blank=True)
    maya_qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.IntegerField()
    kodlar = models.TextField(null=True,blank=True)
    melumat = models.TextField(null=True, blank=True)
    sekil = models.ImageField(upload_to='mehsul_sekilleri', default='mehsul_sekilleri/no_image.webp',null=True, blank=True)    
    yenidir = models.BooleanField(default=False)
    yeni_edildiyi_tarix = models.DateTimeField(null=True, blank=True, verbose_name='Yeni edildiyi tarix')

    def save(self, *args, **kwargs):
        if self.kodlar:
            # Yalnız hərf, rəqəm və boşluq saxla
            self.kodlar = re.sub(r'[^a-zA-Z0-9 ]', '', self.kodlar)

        

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adi} - {self.brend_kod} - {self.oem}"
    
    def qalan_vaxt(self):
        """Məhsulun yeni statusundan çıxmasına qalan vaxtı hesablayır"""
        if not self.yenidir or not self.yeni_edildiyi_tarix:
            return None
        
        indiki_vaxt = timezone.now()
        bitis_vaxti = self.yeni_edildiyi_tarix + timedelta(days=3)
        qalan = bitis_vaxti - indiki_vaxt
        
        if qalan.total_seconds() <= 0:
            return "Vaxt bitdi"
        
        gun = int(qalan.days)
        saat = int(qalan.seconds // 3600)
        deqiqe = int((qalan.seconds % 3600) // 60)
        
        if gun > 0:
            return f"{gun} gün {saat} saat"
        elif saat > 0:
            return f"{saat} saat {deqiqe} dəqiqə"
        else:
            return f"{deqiqe} dəqiqə"
    
    class Meta:
        verbose_name = 'Məhsul'
        verbose_name_plural = 'Məhsullar'


class Sifaris(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Gözləyir'),
        ('PROCESSING', 'İşlənir'),
        ('COMPLETED', 'Tamamlandı'),
        ('CANCELLED', 'Ləğv edildi'),
    ]
    
    DELIVERY_CHOICES = [
        ('TAXI', 'Taksi ilə çatdırılma'),
        ('PICKUP', 'Özüm götürəcəm'),
    ]

    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE)
    tarix = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    catdirilma_usulu = models.CharField(max_length=20, choices=DELIVERY_CHOICES, null=True, blank=True, verbose_name='Çatdırılma üsulu')
    umumi_mebleg = models.DecimalField(max_digits=10, decimal_places=2)
    odenilen_mebleg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qeyd = models.TextField(null=True, blank=True)

    def update_total(self):
        total = sum(item.umumi_mebleg for item in self.sifarisitem_set.all())
        self.umumi_mebleg = total
        self.save()

    @property
    def qaliq_borc(self):
        return self.umumi_mebleg - self.odenilen_mebleg

    @classmethod
    def get_order_statistics(cls, user):
        sifarisler = cls.objects.filter(istifadeci=user)
        return {
            'umumi_sifaris_sayi': sifarisler.count(),
            'umumi_mebleg': sum(sifaris.umumi_mebleg for sifaris in sifarisler),
            'umumi_odenilen': sum(sifaris.odenilen_mebleg for sifaris in sifarisler),
            'umumi_borc': sum(sifaris.qaliq_borc for sifaris in sifarisler)
        }

    def __str__(self):
        return f"Sifariş #{self.id} - {self.istifadeci.username}"

    class Meta:
        verbose_name = 'Sifariş'
        verbose_name_plural = 'Sifarişlər'
        ordering = ['-tarix']


class SifarisItem(models.Model):
    sifaris = models.ForeignKey(Sifaris, on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sifaris.update_total()

    @property
    def umumi_mebleg(self):
        return self.qiymet * self.miqdar

    def __str__(self):
        return f"{self.mehsul.adi} - {self.miqdar} ədəd"

    class Meta:
        verbose_name = 'Sifariş elementi'
        verbose_name_plural = 'Sifariş elementləri'

class PopupImage(models.Model):
    sekil = models.ImageField(upload_to='popup_sekilleri', verbose_name='Şəkil')
    basliq = models.CharField(max_length=100, blank=True, null=True, verbose_name='Başlıq')
    link = models.URLField(blank=True, null=True, verbose_name='Keçid linki')
    aktiv = models.BooleanField(default=True, verbose_name='Aktivdir')
    sira = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Popup şəkil {self.id}"

    class Meta:
        verbose_name = 'Popup Şəkil'
        verbose_name_plural = 'Popup Şəkillər'
        ordering = ['sira', '-yaradilma_tarixi']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='Təsdiqlənib')
    sekil = models.ImageField(upload_to='profile_pics', default='profile_pics/no_image.webp', null=True, blank=True, verbose_name='Profil şəkli')
    yeni_unread_sales = models.IntegerField(default=0, verbose_name='Yeni sifarişlər (görülməmiş)')
    
    def __str__(self):
        return f"{self.user.username} profili"
    
    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profillər'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class ProductLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_products')
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'mehsul')
        verbose_name = 'Məhsul Bəyənməsi'
        verbose_name_plural = 'Məhsul Bəyənmələri'

    def __str__(self):
        return f"{self.user.username} - {self.mehsul.adi} (like)"

class ProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rated_products')
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'mehsul')
        verbose_name = 'Məhsul Qiymətləndirməsi'
        verbose_name_plural = 'Məhsul Qiymətləndirmələri'

    def __str__(self):
        return f"{self.user.username} - {self.mehsul.adi} ({self.rating} ulduz)"


