from pickle import FALSE
from decimal import Decimal
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
    oem = models.CharField(max_length=100)
    stok = models.IntegerField()
    qiymet_eur = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def qiymet_azn(self):
        from decimal import Decimal
        from django.core.cache import cache
        
        # Cache-dən məzənnəni al
        mezenne = cache.get('eur_mezenne')
        if not mezenne:
            # Default məzənnə
            mezenne = Decimal('2.00')
            
        # EUR qiyməti AZN-ə çevir
        return round(self.qiymet_eur * mezenne, 2)
    
    def __str__(self):
        return self.adi

    @property
    def butun_oem_kodlar(self):
        kodlar = [self.oem]
        kodlar.extend([oem.kod for oem in self.oem_kodlar.all()])
        return kodlar

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
    cemi_mebleg_eur = models.DecimalField(max_digits=10, decimal_places=2)
    odenilen_mebleg_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sifaris_mezennesi = models.DecimalField(max_digits=10, decimal_places=2)
    cari_mezenne = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tarix = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='gozleyir')
    tamamlandi = models.BooleanField(default=False)

    @property
    def cemi_mebleg_azn(self):
        return round(self.cemi_mebleg_eur * self.sifaris_mezennesi, 2)

    @property
    def odenilen_mebleg_azn(self):
        return round(self.odenilen_mebleg_eur * self.sifaris_mezennesi, 2)

    @property
    def qaliq_borc_eur(self):
        return self.cemi_mebleg_eur - self.odenilen_mebleg_eur

    @property
    def qaliq_borc_azn(self):
        return round(self.qaliq_borc_eur * self.sifaris_mezennesi, 2)

    @property
    def mezenne_deyisimi(self):
        """Məzənnə dəyişimini hesablayır"""
        if not self.cari_mezenne:
            from django.core.cache import cache
            self.cari_mezenne = cache.get('eur_mezenne', Decimal('2.00'))
        
        deyisim = ((self.cari_mezenne - self.sifaris_mezennesi) / self.sifaris_mezennesi) * 100
        return round(deyisim, 2)
    
    @property
    def mezenne_artib(self):
        """Məzənnənin artıb-azalmasını yoxlayır"""
        return self.mezenne_deyisimi > 0

    def __str__(self):
        return f"Sifariş {self.id} - {self.tarix}"


class SifarisMehsul(models.Model):
    sifaris = models.ForeignKey(Sifaris, related_name='mehsullar', on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE)
    miqdar = models.PositiveIntegerField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.mehsul.adi} - {self.mehsul.kateqoriya} - {self.mehsul.brend_kod} - {self.mehsul.oem} - {self.miqdar} ədəd"

    def total_price(self):
        return self.miqdar * self.qiymet


class OEMKod(models.Model):
    kod = models.CharField(max_length=100)
    mehsul = models.ForeignKey('Mehsul', on_delete=models.CASCADE, related_name='oem_kodlar')

    def __str__(self):
        return self.kod

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
