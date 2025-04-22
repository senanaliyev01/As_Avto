from pickle import FALSE
import random
import string
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


def generate_as_code():
    """6 rəqəmli təsadüfi kod generasiyası"""
    return ''.join(random.choices(string.digits, k=6))


class Mehsul(models.Model):
    adi = models.CharField(max_length=255, null=True, blank=True)
    kateqoriya = models.ForeignKey(Kateqoriya, on_delete=models.CASCADE, null=True, blank=True)
    brend = models.ForeignKey(Brend, on_delete=models.CASCADE, null=True, blank=True)
    marka = models.ForeignKey(Marka, on_delete=models.CASCADE, null=True, blank=True)
    model = models.ManyToManyField(Model,blank=True)  
    brend_kod = models.CharField(max_length=50, null=True, blank=True)
    oem = models.CharField(max_length=255, null=True, blank=True)
    as_kodu = models.CharField(max_length=15, null=True, blank=True, editable=False)
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
            
        is_new_as_code = False
        # OEM kodu əsasında AS kodunu təyin edin
        if self.oem and not self.as_kodu:
            # Eyni OEM kodu olan məhsulu tapın
            existing_product = Mehsul.objects.filter(oem=self.oem).exclude(id=self.id).first()
            
            if existing_product and existing_product.as_kodu:
                # Eyni OEM koduna malik məhsul varsa, onun AS kodunu istifadə edin
                self.as_kodu = existing_product.as_kodu
            else:
                # Yeni bir təkrarsız AS kodu yaradın
                while True:
                    new_code = "AS-" + generate_as_code()
                    if not Mehsul.objects.filter(as_kodu=new_code).exists():
                        self.as_kodu = new_code
                        is_new_as_code = True
                        break
                        
        super().save(*args, **kwargs)
        
        # Yeni AS kodu yaradıldıqda və ya dəyişdikdə, bütün OEM kodlarına bu AS kodunu təyin et
        if self.as_kodu and (is_new_as_code or 'as_kodu' in kwargs.get('update_fields', [])):
            # Eyni OEM kodlu məhsulları tapıb onların AS kodlarını yenilə
            if self.oem:
                similar_products = Mehsul.objects.filter(oem=self.oem).exclude(id=self.id)
                for product in similar_products:
                    if product.as_kodu != self.as_kodu:
                        product.as_kodu = self.as_kodu
                        product.save(update_fields=['as_kodu'])
            
            # Məhsulun əlavə OEM kodları varsa, onlar üçün də eyni AS kodunu təyin et
            for oem_kod in self.oem_kodlar.all():
                # Eyni əlavə OEM koduna malik məhsulları tap
                similar_oem_products = OEMKod.objects.filter(kod=oem_kod.kod).exclude(mehsul=self)
                for oem_product in similar_oem_products:
                    if oem_product.mehsul.as_kodu != self.as_kodu:
                        oem_product.mehsul.as_kodu = self.as_kodu
                        oem_product.mehsul.save(update_fields=['as_kodu'])
                        
                # Eyni əlavə OEM kodu əsas OEM kodu kimi istifadə edən məhsulları tap
                main_oem_products = Mehsul.objects.filter(oem=oem_kod.kod).exclude(id=self.id)
                for main_product in main_oem_products:
                    if main_product.as_kodu != self.as_kodu:
                        main_product.as_kodu = self.as_kodu
                        main_product.save(update_fields=['as_kodu'])

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
        was_new = self.pk is None or self._state.adding
        
        # Əgər yeni yaradılırsa və ya kod dəyişdirilibsə
        if was_new:
            # Bütün xüsusi simvolları silək
            temiz_kod = ''.join(char for char in self.kod if char not in string.punctuation)
            # Boşluqla ayrılmış kodları ayırıb hər birini ayrı-ayrı yaradaqq
            kodlar = temiz_kod.split()
            if kodlar:
                # İlk kodu bu obyektdə saxlayaq
                self.kod = kodlar[0]
                
                super().save(*args, **kwargs)
                
                # AS kodunu məhsulla sinxronlaşdır
                if self.mehsul and self.mehsul.as_kodu:
                    # Eyni OEM koduna malik məhsulları tapıb onlara da eyni AS kodunu təyin et
                    similar_products = Mehsul.objects.filter(oem=self.kod).exclude(id=self.mehsul.id)
                    for product in similar_products:
                        if product.as_kodu != self.mehsul.as_kodu:
                            product.as_kodu = self.mehsul.as_kodu
                            product.save(update_fields=['as_kodu'])
                
                # Əgər məhsulun AS kodu yoxdursa və digər məhsullarda eyni OEM kodu ilə AS kodu varsa
                if self.mehsul and not self.mehsul.as_kodu:
                    # Eyni OEM koduna malik məhsulu tap
                    similar_product = Mehsul.objects.filter(oem=self.kod).exclude(id=self.mehsul.id).first()
                    if similar_product and similar_product.as_kodu:
                        self.mehsul.as_kodu = similar_product.as_kodu
                        self.mehsul.save(update_fields=['as_kodu'])
                    else:
                        # Digər əlavə OEM kodlarında bu kodu axtaraq
                        similar_oem = OEMKod.objects.filter(kod=self.kod).exclude(mehsul=self.mehsul).first()
                        if similar_oem and similar_oem.mehsul.as_kodu:
                            self.mehsul.as_kodu = similar_oem.mehsul.as_kodu
                            self.mehsul.save(update_fields=['as_kodu'])
                        else:
                            # Heç bir yerdə bu OEM kodu ilə məhsul yoxdursa, yeni AS kodu yarat
                            if not self.mehsul.as_kodu:
                                while True:
                                    new_code = "AS-" + generate_as_code()
                                    if not Mehsul.objects.filter(as_kodu=new_code).exists():
                                        self.mehsul.as_kodu = new_code
                                        self.mehsul.save(update_fields=['as_kodu'])
                                        break
                
                # Qalan kodlar üçün yeni OEMKod obyektləri yaradaq
                for kod in kodlar[1:]:
                    new_oem = OEMKod.objects.create(
                        kod=kod,
                        mehsul=self.mehsul
                    )
            return
        else:
            # Mövcud kod yenilənərkən də xüsusi simvolları silək
            self.kod = ''.join(char for char in self.kod if char not in string.punctuation)
            
            super().save(*args, **kwargs)
            
            # AS kodunu məhsulla sinxronlaşdır
            if self.mehsul and self.mehsul.as_kodu:
                # Eyni OEM koduna malik məhsulları tapıb onlara da eyni AS kodunu təyin et
                similar_products = Mehsul.objects.filter(oem=self.kod).exclude(id=self.mehsul.id)
                for product in similar_products:
                    if product.as_kodu != self.mehsul.as_kodu:
                        product.as_kodu = self.mehsul.as_kodu
                        product.save(update_fields=['as_kodu'])

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


