from django.core.management.base import BaseCommand
from mehsullar.models import Mehsul, Brend
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File
import re

class Command(BaseCommand):
    help = 'Məhsul və brend şəkillərini yenidən adlandırır'

    def temizle(self, metin):
        # Xüsusi simvolları və boşluqları təmizləyir
        temiz = re.sub(r'[^\w\s-]', '', metin)
        temiz = re.sub(r'\s+', '_', temiz.strip())
        return temiz.lower()

    def yeniden_adlandir(self, model_instance, field_name, yeni_ad_prefix):
        if hasattr(model_instance, field_name) and getattr(model_instance, field_name):
            sekil = getattr(model_instance, field_name)
            if sekil:
                try:
                    # Köhnə şəklin yolunu və adını al
                    kohne_yol = sekil.path
                    kohne_ad = os.path.basename(kohne_yol)
                    
                    if os.path.exists(kohne_yol):
                        # Yeni ad formatı
                        fayl_uzantisi = os.path.splitext(kohne_ad)[1]
                        yeni_ad = f"{self.temizle(yeni_ad_prefix)}{fayl_uzantisi}"
                        
                        # Şəklin saxlanacağı qovluq
                        upload_folder = 'mehsul_sekilleri' if isinstance(model_instance, Mehsul) else 'brend_sekilleri'
                        yeni_yol = os.path.join(upload_folder, yeni_ad)
                        
                        # Əgər eyni adda şəkil varsa
                        counter = 1
                        while default_storage.exists(yeni_yol):
                            yeni_ad = f"{self.temizle(yeni_ad_prefix)}_{counter}{fayl_uzantisi}"
                            yeni_yol = os.path.join(upload_folder, yeni_ad)
                            counter += 1
                        
                        # Şəkili yeni adla saxla
                        with open(kohne_yol, 'rb') as f:
                            setattr(model_instance, field_name, File(f))
                            getattr(model_instance, field_name).name = yeni_yol
                            model_instance.save()
                        
                        # Köhnə şəkili sil
                        if os.path.exists(kohne_yol):
                            os.remove(kohne_yol)
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Şəkil yenidən adlandırıldı: {kohne_ad} -> {yeni_ad}'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Xəta baş verdi: {str(e)}'
                        )
                    )

    def handle(self, *args, **kwargs):
        # Məhsul şəkillərini yenidən adlandır
        mehsullar = Mehsul.objects.filter(sekil__isnull=False)
        for mehsul in mehsullar:
            yeni_ad = f"{mehsul.adi}_{mehsul.brend.adi}_{mehsul.brend_kod}_{mehsul.oem}"
            self.yeniden_adlandir(mehsul, 'sekil', yeni_ad)
        
        # Brend şəkillərini yenidən adlandır
        brendler = Brend.objects.filter(sekil__isnull=False)
        for brend in brendler:
            self.yeniden_adlandir(brend, 'sekil', brend.adi)
            if brend.sekilyazi:
                self.yeniden_adlandir(brend, 'sekilyazi', f"{brend.adi}_yazi")
        
        self.stdout.write(self.style.SUCCESS('Bütün şəkillər yenidən adlandırıldı!')) 