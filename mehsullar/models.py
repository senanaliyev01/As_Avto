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
    terminal_adi = models.CharField(max_length=100, verbose_name="Terminal adı")
    ip_adres = models.GenericIPAddressField(verbose_name="IP Ünvanı")
    port = models.IntegerField(default=8080, verbose_name="Port")
    aktiv = models.BooleanField(default=True, verbose_name="Aktivdir")
    yaradilma_tarixi = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.terminal_adi} ({self.ip_adres}:{self.port})"
    
    class Meta:
        verbose_name = 'POS Terminal'
        verbose_name_plural = 'POS Terminallar'
    
    def baglanti_yoxla(self):
        """Terminalla bağlantı olub olmadığını yoxlayır"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((self.ip_adres, self.port))
            s.close()
            return True
        except:
            return False
    
    def odenis_et(self, mebleg, kart_nomresi=None):
        """POS terminalı üzərindən ödəniş etmək üçün funksiya"""
        import socket
        import json
        
        if not self.baglanti_yoxla():
            return False, "Terminalla bağlantı qurula bilmədi"
            
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(60)  # Ödəniş 1 dəqiqə ərzində tamamlanmalıdır
            s.connect((self.ip_adres, self.port))
            
            # Ödəniş məlumatlarını hazırlayırıq
            data = {
                "method": "payment",
                "amount": float(mebleg),
                "card_number": kart_nomresi
            }
            
            # Məlumatları JSON formatında göndəririk
            s.sendall(json.dumps(data).encode())
            
            # Cavabı gözləyirik
            response = s.recv(1024).decode()
            s.close()
            
            # Cavabı təhlil edirik
            response_data = json.loads(response)
            if response_data.get("success"):
                return True, response_data.get("transaction_id", "")
            else:
                return False, response_data.get("error", "Bilinməyən xəta")
        except Exception as e:
            return False, str(e)

class Satis(models.Model):
    STATUS_CHOICES = [
        ('gozleyir', 'Ödəniş gözləyir'),
        ('tamamlandi', 'Tamamlandı'),
        ('legv_edildi', 'Ləğv edildi'),
    ]
    
    ODENIS_TIPI_CHOICES = [
        ('nagd', 'Nağd'),
        ('kart', 'Kart'),
        ('terminal', 'POS Terminal'),
        ('hisse', 'Hissəli ödəniş'),
    ]
    
    satis_nomresi = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Satış nömrəsi")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="İstifadəçi")
    cemi_mebleg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cəmi məbləğ")
    odenilen_mebleg = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Ödənilən məbləğ")
    endirim = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Endirim")
    tarix = models.DateTimeField(auto_now_add=True, verbose_name="Satış tarixi")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='gozleyir', verbose_name="Status")
    odenis_tipi = models.CharField(max_length=50, choices=ODENIS_TIPI_CHOICES, default='nagd', verbose_name="Ödəniş tipi")
    terminal = models.ForeignKey(POSTerminal, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="POS Terminal")
    transaction_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="Əməliyyat ID")
    musteri_adi = models.CharField(max_length=255, null=True, blank=True, verbose_name="Müştəri adı")
    musteri_telefon = models.CharField(max_length=20, null=True, blank=True, verbose_name="Müştəri telefonu")
    qeyd = models.TextField(null=True, blank=True, verbose_name="Qeyd")
    
    def save(self, *args, **kwargs):
        # Satis nömrəsini yaratmaq
        if not self.satis_nomresi:
            import datetime
            current_date = datetime.datetime.now()
            # Tarix və vaxt əsasında satış nömrəsi yaratmaq
            self.satis_nomresi = f"S-{current_date.strftime('%Y%m%d')}-{current_date.strftime('%H%M%S')}"
        super(Satis, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Satış #{self.satis_nomresi} - {self.tarix.strftime('%d.%m.%Y %H:%M')}"
    
    class Meta:
        verbose_name = 'Satış'
        verbose_name_plural = 'Satışlar'
        ordering = ['-tarix']
    
    def borc(self):
        return self.cemi_mebleg - self.odenilen_mebleg - self.endirim
    
    def terminal_odenis_et(self):
        """POS terminal vasitəsilə ödəniş etmək üçün metod"""
        if not self.terminal:
            return False, "Terminal seçilməyib"
        
        # Qalan məbləği hesablayırıq
        odenilecek_mebleg = self.borc()
        if odenilecek_mebleg <= 0:
            return False, "Bütün məbləğ artıq ödənilib"
        
        # Terminal vasitəsilə ödəniş edirik
        success, message = self.terminal.odenis_et(odenilecek_mebleg)
        
        if success:
            # Ödənişi qeyd edirik
            self.odenilen_mebleg += odenilecek_mebleg
            self.transaction_id = message  # transaction ID
            
            # Əgər bütün məbləğ ödənilibsə, statusu dəyişdiririk
            if self.borc() <= 0:
                self.status = 'tamamlandi'
                
            self.save()
            return True, "Ödəniş uğurla tamamlandı"
        else:
            return False, f"Ödəniş xətası: {message}"

class SatisMehsul(models.Model):
    satis = models.ForeignKey(Satis, related_name='mehsullar', on_delete=models.CASCADE, verbose_name="Satış")
    mehsul = models.ForeignKey(Mehsul, on_delete=models.CASCADE, verbose_name="Məhsul")
    miqdar = models.PositiveIntegerField(verbose_name="Miqdar")
    qiymet = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Qiymət")
    
    class Meta:
        verbose_name = 'Satış Məhsulu'
        verbose_name_plural = 'Satış Məhsulları'

    def __str__(self):
        return f"{self.mehsul.adi} - {self.miqdar} ədəd"

    def total_price(self):
        return self.miqdar * self.qiymet

    def save(self, *args, **kwargs):
        # Məhsulun stokunu yeniləmək
        if not self.pk:  # Yeni əlavə olunmuş məhsul
            mehsul = self.mehsul
            if mehsul.stok is not None and mehsul.stok >= self.miqdar:
                mehsul.stok -= self.miqdar
                mehsul.save()
        
        super(SatisMehsul, self).save(*args, **kwargs)
        
        # Satışın cəmini yeniləyin
        self.satis.cemi_mebleg = sum(item.total_price() for item in self.satis.mehsullar.all())
        self.satis.save()


