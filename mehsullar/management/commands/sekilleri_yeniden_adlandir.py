from django.core.management.base import BaseCommand
from mehsullar.models import Mehsul
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File

class Command(BaseCommand):
    help = 'Məhsul şəkillərini yenidən adlandırır'

    def handle(self, *args, **kwargs):
        mehsullar = Mehsul.objects.filter(sekil__isnull=False)
        
        for mehsul in mehsullar:
            if mehsul.sekil:
                # Köhnə şəklin yolunu və adını al
                kohne_yol = mehsul.sekil.path
                kohne_ad = os.path.basename(kohne_yol)
                
                if os.path.exists(kohne_yol):
                    # Yeni ad format: brend_kod.jpg/png
                    fayl_uzantisi = os.path.splitext(kohne_ad)[1]
                    yeni_ad = f"{mehsul.brend_kod}{fayl_uzantisi}"
                    yeni_yol = os.path.join('mehsul_sekilleri', yeni_ad)
                    
                    # Əgər eyni adda şəkil varsa, onda brend_kod_1.jpg kimi adlandır
                    counter = 1
                    while default_storage.exists(yeni_yol):
                        yeni_ad = f"{mehsul.brend_kod}_{counter}{fayl_uzantisi}"
                        yeni_yol = os.path.join('mehsul_sekilleri', yeni_ad)
                        counter += 1
                    
                    # Şəkili yeni adla saxla
                    with open(kohne_yol, 'rb') as f:
                        mehsul.sekil.save(yeni_ad, File(f), save=True)
                    
                    # Köhnə şəkili sil
                    if os.path.exists(kohne_yol):
                        os.remove(kohne_yol)
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Şəkil yenidən adlandırıldı: {kohne_ad} -> {yeni_ad}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Şəkil tapılmadı: {kohne_ad}'
                        )
                    )
        
        self.stdout.write(self.style.SUCCESS('Bütün şəkillər yenidən adlandırıldı!')) 