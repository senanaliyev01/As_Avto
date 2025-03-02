from django.core.management.base import BaseCommand
from mehsullar.models import Mehsul, Brend
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File
from PIL import Image
import re
import json
import io

class Command(BaseCommand):
    help = 'Məhsul və brend şəkillərini yenidən adlandırır və WebP formatına çevirir'

    def __init__(self):
        super().__init__()
        self.yaddas_fayli = 'sekil_yaddasi.json'
        self.yeniden_adlananlar = self.yaddasi_yukle()
        self.statistika = {
            'mehsul_sekilleri': 0,
            'brend_sekilleri': 0,
            'brend_yazi_sekilleri': 0,
            'webp_cevirildi': 0
        }

    def yaddasi_yukle(self):
        try:
            if os.path.exists(self.yaddas_fayli):
                with open(self.yaddas_fayli, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'mehsullar': [], 'brendler': [], 'brend_yazilar': []}
        except:
            return {'mehsullar': [], 'brendler': [], 'brend_yazilar': []}

    def yaddasi_saxla(self):
        with open(self.yaddas_fayli, 'w', encoding='utf-8') as f:
            json.dump(self.yeniden_adlananlar, f, ensure_ascii=False, indent=2)

    def temizle(self, metin):
        # Xüsusi simvolları və boşluqları təmizləyir
        temiz = re.sub(r'[^\w\s-]', '', metin)
        temiz = re.sub(r'\s+', '_', temiz.strip())
        return temiz.lower()

    def sekili_webp_cevir(self, image_path):
        """Şəkili WebP formatına çevirir və şəffaflığı qoruyur"""
        try:
            with Image.open(image_path) as img:
                # Şəklin orijinal ölçüsünü və formatını saxla
                original_format = img.format
                
                # Əgər şəkil artıq WebP formatındadırsa, çevirmə
                if original_format == 'WEBP':
                    return None
                
                # RGBA moduna keç (şəffaflıq üçün)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                
                # Şəkili yaddaşda saxla
                output = io.BytesIO()
                
                # WebP formatına çevir (şəffaflığı qoruyaraq)
                img.save(output, format='WEBP', quality=90, method=6, lossless=True)
                output.seek(0)
                
                return output
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Şəkil WebP formatına çevrilərkən xəta baş verdi: {str(e)}'
                )
            )
            return None

    def yeniden_adlandir(self, model_instance, field_name, yeni_ad_prefix, tip='mehsul'):
        if hasattr(model_instance, field_name) and getattr(model_instance, field_name):
            sekil = getattr(model_instance, field_name)
            if sekil:
                try:
                    # Əgər şəkil artıq yenidən adlandırılıbsa, keç
                    model_id = str(model_instance.id)
                    if tip == 'mehsul' and model_id in self.yeniden_adlananlar['mehsullar']:
                        return
                    elif tip == 'brend' and model_id in self.yeniden_adlananlar['brendler']:
                        return
                    elif tip == 'brend_yazi' and model_id in self.yeniden_adlananlar['brend_yazilar']:
                        return

                    # Köhnə şəklin yolunu və adını al
                    kohne_yol = sekil.path
                    kohne_ad = os.path.basename(kohne_yol)
                    
                    if os.path.exists(kohne_yol):
                        # WebP formatına çevir
                        webp_output = self.sekili_webp_cevir(kohne_yol)
                        
                        if webp_output:
                            # Yeni ad formatı (.webp uzantısı ilə)
                            yeni_ad = f"{self.temizle(yeni_ad_prefix)}.webp"
                            
                            # Şəklin saxlanacağı qovluq
                            upload_folder = 'mehsul_sekilleri' if isinstance(model_instance, Mehsul) else 'brend_sekilleri'
                            yeni_yol = os.path.join(upload_folder, yeni_ad)
                            
                            # Əgər eyni adda şəkil varsa
                            counter = 1
                            while default_storage.exists(yeni_yol):
                                yeni_ad = f"{self.temizle(yeni_ad_prefix)}_{counter}.webp"
                                yeni_yol = os.path.join(upload_folder, yeni_ad)
                                counter += 1
                            
                            # WebP şəklini yeni adla saxla
                            setattr(model_instance, field_name, File(webp_output, name=yeni_yol))
                            model_instance.save()
                            
                            # Köhnə şəkili sil
                            if os.path.exists(kohne_yol):
                                os.remove(kohne_yol)

                            # Statistikanı yenilə
                            if tip == 'mehsul':
                                self.statistika['mehsul_sekilleri'] += 1
                                self.yeniden_adlananlar['mehsullar'].append(model_id)
                            elif tip == 'brend':
                                self.statistika['brend_sekilleri'] += 1
                                self.yeniden_adlananlar['brendler'].append(model_id)
                            elif tip == 'brend_yazi':
                                self.statistika['brend_yazi_sekilleri'] += 1
                                self.yeniden_adlananlar['brend_yazilar'].append(model_id)
                            
                            self.statistika['webp_cevirildi'] += 1
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Şəkil WebP formatına çevrildi və yenidən adlandırıldı: {kohne_ad} -> {yeni_ad}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Şəkil artıq WebP formatındadır və ya çevrilə bilmədi: {kohne_ad}'
                                )
                            )
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Xəta baş verdi: {str(e)}'
                        )
                    )

    def handle(self, *args, **kwargs):
        # Məhsul şəkillərini yenidən adlandır və WebP-ə çevir
        mehsullar = Mehsul.objects.filter(sekil__isnull=False)
        for mehsul in mehsullar:
            yeni_ad = f"{mehsul.adi}_{mehsul.brend.adi}_{mehsul.brend_kod}_{mehsul.oem}"
            self.yeniden_adlandir(mehsul, 'sekil', yeni_ad, 'mehsul')
        
        # Brend şəkillərini yenidən adlandır və WebP-ə çevir
        brendler = Brend.objects.filter(sekil__isnull=False)
        for brend in brendler:
            self.yeniden_adlandir(brend, 'sekil', brend.adi, 'brend')
            if brend.sekilyazi:
                self.yeniden_adlandir(brend, 'sekilyazi', f"{brend.adi}_yazi", 'brend_yazi')
        
        # Yaddaşı saxla
        self.yaddasi_saxla()

        # Statistikanı göstər
        self.stdout.write("\nStatistika:")
        self.stdout.write(f"Məhsul şəkilləri: {self.statistika['mehsul_sekilleri']} ədəd")
        self.stdout.write(f"Brend şəkilləri: {self.statistika['brend_sekilleri']} ədəd")
        self.stdout.write(f"Brend yazı şəkilləri: {self.statistika['brend_yazi_sekilleri']} ədəd")
        self.stdout.write(f"WebP formatına çevrilən şəkillər: {self.statistika['webp_cevirildi']} ədəd")
        
        if sum(self.statistika.values()) == 0:
            self.stdout.write(
                self.style.WARNING('Heç bir şəkil yenidən adlandırılmadı və ya çevrilmədi!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Cəmi {sum(self.statistika.values())} ədəd şəkil emal edildi!")
            ) 