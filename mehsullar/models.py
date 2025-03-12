from pickle import FALSE

from django.db import models
from django.contrib.auth.models import User

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

class AxtarisSozleri(models.Model):
    adi = models.CharField(max_length=100, unique=True)
    sozler = models.TextField(help_text="Axtarış sözlərini boşluqla ayırın. Məsələn: 'sirga sirgalar'")

    def __str__(self):
        return self.adi

    class Meta:
        verbose_name = 'Axtarış Sözləri'
        verbose_name_plural = 'Axtarış Sözləri'

class Mehsul(models.Model):
    adi = models.CharField(max_length=255)
    kateqoriya = models.ForeignKey(Kateqoriya, on_delete=models.CASCADE)
    brend = models.ForeignKey(Brend, on_delete=models.CASCADE)
    marka = models.ForeignKey(Marka, on_delete=models.CASCADE)
    model = models.ManyToManyField(Model,blank=True)  
    axtaris_sozleri = models.ForeignKey(AxtarisSozleri, on_delete=models.SET_NULL, null=True, blank=True, related_name='mehsullar')
    brend_kod = models.CharField(max_length=50, unique=True)
    oem = models.CharField(max_length=100)
    stok = models.IntegerField()
    maya_qiymet = models.DecimalField(max_digits=10, decimal_places=2)
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)
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
        # Əgər yeni yaradılırsa və ya kod dəyişdirilibsə
        if self.pk is None or self._state.adding:
            # Əvvəlcə "-" işarələrini silək
            temiz_kod = self.kod.replace('-', '')
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
            # Mövcud kod yenilənərkən də "-" işarələrini silək
            self.kod = self.kod.replace('-', '')
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


