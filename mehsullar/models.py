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

class POSTerminal(models.Model):
    ad = models.CharField(max_length=100, verbose_name="Terminal adı")
    ip_adres = models.CharField(max_length=50, verbose_name="IP Adresi")
    port = models.IntegerField(default=8080, verbose_name="Port")
    aktiv = models.BooleanField(default=True, verbose_name="Aktivdir")
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.ad} ({self.ip_adres}:{self.port})"
        
    class Meta:
        verbose_name = 'POS Terminal'
        verbose_name_plural = 'POS Terminallar'
        
class Satis(models.Model):
    ODENIS_USULLARI = [
        ('nagd', 'Nağd'),
        ('kart', 'Kart'),
        ('terminal', 'POS Terminal')
    ]
    
    STATUS_CHOICES = [
        ('gozleyen', 'Gözləyən'),
        ('tamamlandi', 'Tamamlandı'),
        ('legv_edildi', 'Ləğv edildi')
    ]
    
    tarix = models.DateTimeField(auto_now_add=True, verbose_name="Satış tarixi")
    umumi_mebleg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ümumi məbləğ")
    odenis_usulu = models.CharField(max_length=20, choices=ODENIS_USULLARI, default='nagd', verbose_name="Ödəniş üsulu")
    pos_terminal = models.ForeignKey(POSTerminal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="POS Terminal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='gozleyen', verbose_name="Status")
    qeyd = models.TextField(blank=True, null=True, verbose_name="Qeyd")
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Operator")
    emeliyyat_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Əməliyyat ID")
    
    def __str__(self):
        return f"Satış #{self.id} - {self.tarix.strftime('%d-%m-%Y %H:%M')}"
    
    def pos_terminal_odeme(self):
        """POS Terminal vasitəsilə ödəmə edir"""
        from .pos_terminal import get_terminal
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"POS Terminal ödəməsi başladılır. Terminal: {self.pos_terminal}")
        
        if not self.pos_terminal:
            logger.error("POS Terminal seçilməyib")
            return False, "POS Terminal seçilməyib"
        
        # IP localhost-sa dummy terminal istifadə et (test və debug üçün)
        use_dummy = self.pos_terminal.ip_adres in ["localhost", "127.0.0.1"]
        
        # Terminal servisi yarat
        terminal = get_terminal(
            self.pos_terminal.ip_adres, 
            self.pos_terminal.port,
            debug=True,  # Debug rejimini aktiv edirik
            dummy=use_dummy  # Test rejimi
        )
        
        # Əvvəlcə terminal ilə bağlantı qurmağı sınayaq
        if not terminal.connect():
            logger.error(f"Terminal ilə bağlantı qurula bilmədi: {self.pos_terminal.ip_adres}:{self.pos_terminal.port}")
            return False, f"Terminal ilə bağlantı qurula bilmədi. Lütfən IP adresini ({self.pos_terminal.ip_adres}) və portu ({self.pos_terminal.port}) yoxlayın."
        
        # Terminalın statusunu yoxlayaq
        status, status_message = terminal.check_status()
        if not status:
            logger.warning(f"Terminal hazır deyil: {status_message}")
            terminal.disconnect()
            return False, f"Terminal hazır deyil: {status_message}"
        
        logger.info(f"Terminal ilə bağlantı quruldu və hazırdır: {status_message}")
        
        # Əlavə məlumatları hazırlayaq (çekdə göstəriləcək)
        mehsul_sayi = self.mehsullar.count()
        
        # Satış detallarını hazırla
        mehsul_detallari = []
        for item in self.mehsullar.all():
            mehsul_detallari.append({
                'ad': item.mehsul.adi,
                'kod': item.mehsul.brend_kod or '',
                'miqdar': item.miqdar,
                'qiymet': float(item.qiymet),
                'cem': float(item.miqdar * item.qiymet)
            })
        
        # Ödəməni həyata keçir
        reference_no = f"TR{self.id}-{int(self.tarix.timestamp())}"
        logger.info(f"Ödəmə prosesi başladılır, məbləğ: {self.umumi_mebleg}, istinad: {reference_no}")
        
        success, transaction_id, message = terminal.process_payment(
            self.umumi_mebleg, 
            reference_no,
            {
                'operator': self.operator.get_full_name() or self.operator.username,
                'satis_id': self.id,
                'tarix': self.tarix.strftime('%d-%m-%Y %H:%M'),
                'mehsul_sayi': mehsul_sayi,
                'mehsullar': mehsul_detallari
            }
        )
        
        # Bağlantını kəsək
        terminal.disconnect()
        
        # Əməliyyat nəticəsini qeyd et
        if success:
            logger.info(f"Ödəmə uğurla tamamlandı: {transaction_id}")
            self.emeliyyat_id = transaction_id
            self.status = 'tamamlandi'
            self.save()
        else:
            logger.error(f"Ödəmə xətası: {message}")
        
        return success, message
    
    def pos_legv_et(self):
        """POS Terminal vasitəsilə edilmiş ödəməni ləğv edir"""
        from .pos_terminal import get_terminal
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"POS Terminal ləğv əməliyyatı başladılır. Terminal: {self.pos_terminal}, Əməliyyat ID: {self.emeliyyat_id}")
        
        if not self.pos_terminal or not self.emeliyyat_id:
            logger.error("Ləğv ediləcək əməliyyat tapılmadı")
            return False, "Ləğv ediləcək əməliyyat tapılmadı"
        
        # IP localhost-sa dummy terminal istifadə et (test və debug üçün)
        use_dummy = self.pos_terminal.ip_adres in ["localhost", "127.0.0.1"]
        
        # Terminal servisi yarat
        terminal = get_terminal(
            self.pos_terminal.ip_adres, 
            self.pos_terminal.port,
            debug=True,
            dummy=use_dummy
        )
        
        # Əvvəlcə terminal ilə bağlantı qurmağı sınayaq
        if not terminal.connect():
            logger.error(f"Terminal ilə bağlantı qurula bilmədi: {self.pos_terminal.ip_adres}:{self.pos_terminal.port}")
            return False, f"Terminal ilə bağlantı qurula bilmədi. Lütfən IP adresini yoxlayın."
        
        # Ləğv et
        success, message = terminal.cancel_transaction(self.emeliyyat_id)
        
        # Bağlantını kəsək
        terminal.disconnect()
        
        # Əməliyyat nəticəsini qeyd et
        if success:
            logger.info(f"Ödəmə uğurla ləğv edildi: {self.emeliyyat_id}")
            self.status = 'legv_edildi'
            self.save()
        else:
            logger.error(f"Ləğv xətası: {message}")
        
        return success, message
        
    class Meta:
        verbose_name = 'Satış'
        verbose_name_plural = 'Satışlar'
        ordering = ['-tarix']

class SatisMehsul(models.Model):
    satis = models.ForeignKey(Satis, related_name='mehsullar', on_delete=models.CASCADE)
    mehsul = models.ForeignKey(Mehsul, on_delete=models.PROTECT)
    miqdar = models.PositiveIntegerField(default=1, verbose_name="Miqdar")
    qiymet = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Qiymət")
    
    def __str__(self):
        return f"{self.mehsul.adi} - {self.miqdar} ədəd"
    
    def total_qiymet(self):
        return self.miqdar * self.qiymet
        
    class Meta:
        verbose_name = 'Satış Məhsulu'
        verbose_name_plural = 'Satış Məhsulları'


