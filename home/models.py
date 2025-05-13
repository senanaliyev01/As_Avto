from django.contrib.auth.models import User
from django.db import models
import re
from PIL import Image
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import uuid

class Kateqoriya(models.Model):
    adi = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.adi}"
    
    class Meta:
        verbose_name = 'Kateqoriya'
        verbose_name_plural = 'Kateqoriyalar' 


class Firma(models.Model):
    adi = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)

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

class Vitrin(models.Model):
    nomre = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.nomre}"
    
    class Meta:
        verbose_name = 'Vitrin'
        verbose_name_plural = 'Vitrinlər'

    
class Mehsul(models.Model):
    adi = models.CharField(max_length=100)
    kateqoriya = models.ForeignKey(Kateqoriya,on_delete=models.CASCADE, null=True, blank=True)
    firma = models.ForeignKey(Firma,on_delete=models.CASCADE)
    avtomobil = models.ForeignKey(Avtomobil,on_delete=models.CASCADE)
    brend_kod = models.CharField(max_length=100)
    oem = models.CharField(max_length=100)
    olcu = models.CharField(max_length=50,null=True,blank=True)
    vitrin = models.ForeignKey(Vitrin,on_delete=models.CASCADE,null=True,blank=True)
    maya_qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    stok = models.IntegerField()
    kodlar = models.TextField(null=True,blank=True)
    melumat = models.TextField(null=True, blank=True)
    sekil = models.ImageField(upload_to='mehsul_sekilleri', default='mehsul_sekilleri/no_image.webp',null=True, blank=True)    
    yenidir = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.kodlar:
            # Yalnız hərf, rəqəm və boşluq saxla
            self.kodlar = re.sub(r'[^a-zA-Z0-9 ]', '', self.kodlar)
        
        # Şəkil emalı
        if self.sekil and hasattr(self.sekil, 'file'):
            # Əgər şəkil yenidirsə və no_image.webp deyilsə
            if isinstance(self.sekil.file, InMemoryUploadedFile) and 'no_image.webp' not in self.sekil.name:
                # Şəkli aç
                image = Image.open(self.sekil)
                
                # Şəkli RGBA formatına çevir (webp üçün)
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Yeni fayl adı yarat
                new_name = f"{uuid.uuid4().hex[:10]}_{self.brend_kod}.webp"
                
                # BytesIO buffer yarat
                output = BytesIO()
                
                # Şəkli webp formatında saxla
                image.save(output, format='WEBP', quality=85, optimize=True)
                output.seek(0)
                
                # Köhnə şəkli sil (əgər varsa və default deyilsə)
                if self.pk:
                    try:
                        old_instance = Mehsul.objects.get(pk=self.pk)
                        if old_instance.sekil and old_instance.sekil.name != 'mehsul_sekilleri/no_image.webp':
                            if os.path.isfile(old_instance.sekil.path):
                                os.remove(old_instance.sekil.path)
                    except:
                        pass
                
                # Yeni şəkli təyin et
                self.sekil = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    new_name,
                    'image/webp',
                    output.tell(),
                    None
                )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.adi} - {self.brend_kod} - {self.oem}"
    
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