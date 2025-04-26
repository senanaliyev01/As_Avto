from pickle import FALSE
import random
import string
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import os
from django.conf import settings

class Kateqoriya(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi
    
    class Meta:
        verbose_name = 'Kateqoriyalar'
        verbose_name_plural = 'Kateqoriyalar'

class Brend(models.Model):
    adi = models.CharField(max_length=100, unique=True)
    sekil = models.ImageField(upload_to='brend_sekilleri/', null=True, blank=True)
    sekilyazi = models.ImageField(upload_to='brend_yazilari/', null=True, blank=True)
    haqqinda = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.adi
    
    class Meta:
        verbose_name = 'Firmalar'
        verbose_name_plural = 'Firmalar'

class Marka(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi
    
    class Meta:
        verbose_name = 'Markalar'
        verbose_name_plural = 'Markalar'

class MarkaSekil(models.Model):
    marka = models.ForeignKey(Marka, related_name='sekiller', on_delete=models.CASCADE)
    sekil = models.ImageField(upload_to='marka_sekilleri/', null=True, blank=True)

    def __str__(self):
        return f"{self.marka.adi} - Şəkil"
    
    
class Avtomodel(models.Model):
    adi = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.adi
    
    class Meta:
        verbose_name = 'Avtomobil Modelleri'
        verbose_name_plural = 'Avtomobil Modelleri'
    
class Motor(models.Model):
    motor = models.CharField(max_length=100 , unique=True)

    def __str__(self):
        return self.motor
    
    class Meta:
        verbose_name = 'Avtomobil Motorları'
        verbose_name_plural = 'Avtomobil Motorları'
        
class Il(models.Model):
    il = models.CharField(max_length=100 , unique=True)

    def __str__(self):
        return self.il
    
    class Meta:
        verbose_name = 'Avtomobil İlləri'
        verbose_name_plural = 'Avtomobil İlləri'

class Yanacaq(models.Model):
    yanacaq = models.CharField(max_length=100 , unique=True)

    def __str__(self):
        return self.yanacaq
    
    class Meta:
        verbose_name = 'Yanacaq'
        verbose_name_plural = 'Yanacaq'
    
class Model(models.Model):
    avtomobil = models.ForeignKey(Marka, on_delete=models.CASCADE)
    model = models.ForeignKey(Avtomodel, on_delete=models.CASCADE)
    motor = models.ForeignKey(Motor, on_delete=models.CASCADE)
    yanacaq = models.ForeignKey(Yanacaq, on_delete=models.CASCADE)
    il = models.ForeignKey(Il, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.avtomobil} - {self.model} - {self.motor} - {self.yanacaq} - {self.il}"
    
    class Meta:
        verbose_name = 'Modeller'
        verbose_name_plural = 'Modeller'


class Mehsul(models.Model):
    adi = models.CharField(max_length=255, null=True, blank=True)
    kateqoriya = models.ForeignKey(Kateqoriya, on_delete=models.CASCADE, null=True, blank=True)
    brend = models.ForeignKey(Brend, on_delete=models.CASCADE, null=True, blank=True)
    marka = models.ForeignKey(Marka, on_delete=models.CASCADE, null=True, blank=True)
    model = models.ManyToManyField(Model,blank=True)  
    brend_kod = models.CharField(max_length=50, null=True, blank=True)
    oem = models.CharField(max_length=255, null=True, blank=True)
    stok = models.IntegerField(null=True, blank=True)
    maya_qiymet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qiymet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sekil = models.ImageField(upload_to='mehsul_sekilleri/', null=True, blank=True, default='mehsul_sekilleri/noimage.webp')
    haqqinda = models.TextField(null=True, blank=True)
    yenidir = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.adi} - {self.brend_kod} - {self.oem}"
    
    class Meta:
        verbose_name = 'Məhsullar'
        verbose_name_plural = 'Məhsullar'

    @property
    def formatted_qiymet(self):
        return str(self.qiymet).replace(',', '.')

    @property
    def butun_oem_kodlar(self):
        kodlar = [self.oem]
        kodlar.extend([oem.kod for oem in self.oem_kodlar.all()])
        return kodlar
        
    @property
    def butun_axtaris_sozleri(self):
        if self.axtaris_sozleri:
            return self.axtaris_sozleri.sozler.split()
        return []

    def save(self, *args, **kwargs):
        if not self.sekil:
            self.sekil = 'mehsul_sekilleri/noimage.webp'
        elif self.sekil and hasattr(self.sekil, 'name') and not self.sekil.name.startswith('mehsul_sekilleri/noimage'):
            # Şəkil var və default olmayan şəkil əlavə edilib
            img = Image.open(self.sekil)
            
            # Əgər şəkil RGBA modundadırsa (alpha kanalı varsa), RGB-yə çevir
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                
            # Şəklin eni və hündürlüyünə baxaq, lazım gələrsə ölçüsünü dəyişək
            if img.width > 1920 or img.height > 1080:
                output_size = (1920, 1080)
                img.thumbnail(output_size, Image.LANCZOS)
                
            # Şəklin parlaqlığını azaldaq (solğunlaşdıraq)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(0.85)  # 15% solğunlaşdırma
            
            # Favicon/loqo üçün şəffaf layı əlavə et
            # Şəklin mərkəzini tapmaq
            width, height = img.size
            
            # Şəffaf arxa fon yaratmaq
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            
            # Şəffaf şüşə rəngi (açıq mavi tonunda) ilə arxa fon qatı yaradaq
            overlay = Image.new('RGBA', img.size, (173, 216, 230, 80))  # RGBA - açıq mavi + 30% şəffaflıq
            
            # "AS" yazısını əlavə etmək üçün drawing obyekti
            draw = ImageDraw.Draw(overlay)
            
            # Font ölçüsünü şəklin ölçüsünə uyğun seçək
            font_size = int(min(width, height) * 0.3)  # Şəklin ölçüsünün 30%-i
            
            # Əgər Django static fayllar qovluğunda istədiyimiz font varsa onu istifadə edək,
            # yoxsa default fontu istifadə edək
            try:
                font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'arial_bold.ttf')
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                else:
                    # Default font istifadə et
                    font = ImageFont.load_default()
            except:
                # Problem olduqda default font istifadə et
                font = ImageFont.load_default()
            
            # "AS" mətni
            text = "AS"
            
            # Mətnin ölçüsünü əldə et (daha dəqiq yerləşdirmək üçün)
            try:
                # PIL 9.0.0+ versiyada
                text_size = draw.textbbox((0, 0), text, font=font)[2:4]
            except:
                # Köhnə PIL versiyalarında
                text_size = draw.textsize(text, font=font)
                
            # Mətnin mərkəzdə yerləşdirilməsi
            text_position = ((width - text_size[0]) // 2, (height - text_size[1]) // 2)
            
            # "AS" yazısını əlavə et
            draw.text(text_position, text, fill=(255, 255, 255, 128), font=font)  # Yarı şəffaf ağ
            
            # Overlay layını əsas şəkillə birləşdir
            img = Image.composite(overlay, img.convert('RGBA'), overlay)
            
            # WEBP formatına çevirmək üçün yenidən RGB-yə çevir
            img = img.convert('RGB')
            
            # Webp formatına çevirmək
            output = BytesIO()
            # Yüksək keyfiyyətli webp formatına çevirmə, 90% keyfiyyət
            img.save(output, format='WEBP', quality=90)
            output.seek(0)
            
            # Məhsul məlumatlarından yeni fayl adı yarat
            brend_adi = self.brend.adi if self.brend else ""
            marka_adi = self.marka.adi if self.marka else ""
            mehsul_adi = self.adi if self.adi else ""
            brend_kodu = self.brend_kod if self.brend_kod else ""
            oem_kodu = self.oem if self.oem else ""
            
            # Simvolları təmizlə və boşluq yerinə alt xətt qoy
            brend_adi = brend_adi.strip().replace(" ", "_")
            marka_adi = marka_adi.strip().replace(" ", "_")
            mehsul_adi = mehsul_adi.strip().replace(" ", "_")
            brend_kodu = brend_kodu.strip().replace(" ", "_")
            oem_kodu = oem_kodu.strip().replace(" ", "_")
            
            # Fayl adını yarat - qeyri-valid və problemli simvolları təmizlə
            valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            parts = [mehsul_adi, brend_adi, marka_adi, brend_kodu, oem_kodu]
            parts = ["".join(c for c in part if c in valid_chars) for part in parts]
            
            # Boş olmayan hissələri birləşdir
            parts = [p for p in parts if p]
            new_filename = "_".join(parts) + ".webp"
            
            # Fayl adı 100 simvoldan uzun olmasın
            if len(new_filename) > 100:
                new_filename = new_filename[:95] + ".webp"
            
            # Yeni InMemoryUploadedFile yaratmaq
            self.sekil = InMemoryUploadedFile(output, 'ImageField', 
                                             new_filename, 
                                             'image/webp', 
                                             sys.getsizeof(output), 
                                             None)
            
        super().save(*args, **kwargs)

class Sebet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.mehsul.adi}"
    
    class Meta:
        verbose_name = 'Səbət'
        verbose_name_plural = 'Səbət'


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
    
    class Meta:
        verbose_name = 'Sifarişlər'
        verbose_name_plural = 'Sifarişlər'


class SifarisMehsul(models.Model):
    sifaris = models.ForeignKey(Sifaris, related_name='mehsullar', on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
            verbose_name = 'Sifariş Məhsulları'
            verbose_name_plural = 'Sifariş Məhsulları'

    def __str__(self):
        return f"{self.mehsul.adi} - {self.mehsul.kateqoriya} - {self.mehsul.brend_kod} - {self.mehsul.oem} - {self.miqdar} ədəd"

    def total_price(self):
        return self.miqdar * self.qiymet

    def save(self, *args, **kwargs):
        # Sifarişin cəmini yeniləyin
        super().save(*args, **kwargs)  # İlk öncə məhsulu saxlayın
        self.sifaris.cemi_mebleg = sum(item.total_price() for item in self.sifaris.mehsullar.all())
        self.sifaris.save()  # Sifarişi yeniləyin
        
        


class OEMKod(models.Model):
    kod = models.TextField(help_text="OEM kodlarını boşluqla ayırın. Hər bir kod avtomatik olaraq ayrı-ayrı saxlanılacaq.")
    mehsul = models.ForeignKey('Mehsul', on_delete=models.CASCADE, related_name='oem_kodlar')

    def __str__(self):
        return self.kod

    def save(self, *args, **kwargs):
        import string
        # Əgər yeni yaradılırsa və ya kod dəyişdirilibsə
        if self.pk is None or self._state.adding:
            # Bütün xüsusi simvolları silək
            temiz_kod = ''.join(char for char in self.kod if char not in string.punctuation)
            # Boşluqla ayrılmış kodları ayırıb hər birini ayrı-ayrı yaradaqq
            kodlar = temiz_kod.split()
            if kodlar:
                # İlk kodu bu obyektdə saxlayaq
                self.kod = kodlar[0]
                super().save(*args, **kwargs)
                # Qalan kodlar üçün yeni OEMKod obyektləri yaradaq
                for kod in kodlar[1:]:
                    OEMKod.objects.create(
                        kod=kod,
                        mehsul=self.mehsul
                    )
            return
        else:
            # Mövcud kod yenilənərkən də xüsusi simvolları silək
            self.kod = ''.join(char for char in self.kod if char not in string.punctuation)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'OEM Kod'
        verbose_name_plural = 'OEM Kodlar'


class SebetItem(models.Model):
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.IntegerField(default=1)
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mehsul.adi} - {self.miqdar}"

    class Meta:
        verbose_name = 'Səbət elementi'
        verbose_name_plural = 'Səbət elementləri'


class MusteriReyi(models.Model):
    RATING_CHOICES = (
        (1, '1 Ulduz'),
        (2, '2 Ulduz'),
        (3, '3 Ulduz'),
        (4, '4 Ulduz'),
        (5, '5 Ulduz'),
    )
    
    musteri = models.ForeignKey(User, on_delete=models.CASCADE)
    rey = models.TextField()
    qiymetlendirme = models.IntegerField( null=True ,choices=RATING_CHOICES)
    tarix = models.DateTimeField(auto_now_add=True)
    tesdiq = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Müştəri Rəyi'
        verbose_name_plural = 'Müştəri Rəyləri'
        ordering = ['-tarix']

    def __str__(self):
        return f"{self.musteri.get_full_name()} - {self.get_qiymetlendirme_display()}"


