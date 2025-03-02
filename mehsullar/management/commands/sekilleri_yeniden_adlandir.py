from django.core.management.base import BaseCommand
from mehsullar.models import Mehsul, Brend
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files import File
import re
import json
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Məhsul və brend şəkillərini yenidən adlandırır və WebP formatına çevirir'

    def __init__(self):
        super().__init__()
        self.yaddas_fayli = os.path.join(settings.BASE_DIR, 'sekil_yaddasi.json')
        self.yeniden_adlananlar = self.yaddasi_yukle()
        self.statistika = {
            'mehsul_sekilleri': 0,
            'brend_sekilleri': 0,
            'brend_yazi_sekilleri': 0,
            'webp_cevrilen': 0
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
        temiz = re.sub(r'[^\w\s-]', '', str(metin))
        temiz = re.sub(r'\s+', '_', temiz.strip())
        return temiz.lower()

    def sekili_webp_cevir(self, image_path):
        try:
            # Şəkili aç
            with Image.open(image_path) as img:
                # RGBA formatına çevir (şəffaflığı qorumaq üçün)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')

                # BytesIO obyekti yarat
                webp_io = BytesIO()
                
                # WebP formatında saxla (şəffaflığı qoruyaraq)
                img.save(webp_io, 'WEBP', quality=90, lossless=True)
                webp_io.seek(0)
                
                return webp_io

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'WebP çevirmədə xəta: {str(e)}'
                )
            )
            return None

    def yeniden_adlandir(self, model_instance, field_name, yeni_ad_prefix, tip='mehsul'):
        if hasattr(model_instance, field_name) and getattr(model_instance, field_name):
            sekil = getattr(model_instance, field_name)
            if not sekil:
                return

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
                try:
                    kohne_yol = os.path.join(settings.MEDIA_ROOT, sekil.name)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Şəkil yolu tapılmadı: {str(e)}'))
                    return

                if not os.path.exists(kohne_yol):
                    self.stdout.write(self.style.ERROR(f'Şəkil tapılmadı: {kohne_yol}'))
                    return

                # Yeni ad formatı (WebP uzantısı ilə)
                yeni_ad = f"{self.temizle(yeni_ad_prefix)}.webp"
                
                # Şəklin saxlanacağı qovluq
                upload_folder = 'mehsul_sekilleri' if isinstance(model_instance, Mehsul) else 'brend_sekilleri'
                upload_path = os.path.join(settings.MEDIA_ROOT, upload_folder)
                
                # Qovluğu yarat əgər yoxdursa
                os.makedirs(upload_path, exist_ok=True)
                
                # Tam yol
                yeni_yol = os.path.join(upload_folder, yeni_ad)
                tam_yeni_yol = os.path.join(settings.MEDIA_ROOT, yeni_yol)
                
                # Əgər eyni adda şəkil varsa
                counter = 1
                while os.path.exists(tam_yeni_yol):
                    yeni_ad = f"{self.temizle(yeni_ad_prefix)}_{counter}.webp"
                    yeni_yol = os.path.join(upload_folder, yeni_ad)
                    tam_yeni_yol = os.path.join(settings.MEDIA_ROOT, yeni_yol)
                    counter += 1
                
                # Şəkili WebP formatına çevir
                webp_io = self.sekili_webp_cevir(kohne_yol)
                if webp_io:
                    try:
                        # Yeni WebP şəkili saxla
                        setattr(model_instance, field_name, File(webp_io, name=yeni_yol))
                        model_instance.save()
                        
                        # Köhnə şəkili sil
                        try:
                            if os.path.exists(kohne_yol) and kohne_yol != tam_yeni_yol:
                                os.remove(kohne_yol)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Köhnə şəkil silinərkən xəta: {str(e)}'))

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
                        
                        self.statistika['webp_cevrilen'] += 1
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Şəkil WebP formatına çevrildi və yenidən adlandırıldı: {os.path.basename(kohne_yol)} -> {yeni_ad}'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Şəkil saxlanarkən xəta: {str(e)}'))
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Xəta baş verdi: {str(e)}'
                    )
                )

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Şəkillərin çevrilməsi başladı...'))
        
        # Məhsul şəkillərini yenidən adlandır və WebP-ə çevir
        mehsullar = Mehsul.objects.filter(sekil__isnull=False)
        mehsul_sayi = mehsullar.count()
        self.stdout.write(f'Tapılan məhsul sayı: {mehsul_sayi}')
        
        for index, mehsul in enumerate(mehsullar, 1):
            self.stdout.write(f'Məhsul emal edilir ({index}/{mehsul_sayi}): {mehsul.adi}')
            yeni_ad = f"{mehsul.adi}_{mehsul.brend.adi}_{mehsul.brend_kod}_{mehsul.oem}"
            self.yeniden_adlandir(mehsul, 'sekil', yeni_ad, 'mehsul')
        
        # Brend şəkillərini yenidən adlandır və WebP-ə çevir
        brendler = Brend.objects.filter(sekil__isnull=False)
        brend_sayi = brendler.count()
        self.stdout.write(f'Tapılan brend sayı: {brend_sayi}')
        
        for index, brend in enumerate(brendler, 1):
            self.stdout.write(f'Brend emal edilir ({index}/{brend_sayi}): {brend.adi}')
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
        self.stdout.write(f"WebP formatına çevrilən şəkillər: {self.statistika['webp_cevrilen']} ədəd")
        
        if sum(self.statistika.values()) == 0:
            self.stdout.write(
                self.style.WARNING('Heç bir şəkil yenidən adlandırılmadı və ya çevrilmədi!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Cəmi {self.statistika['webp_cevrilen']} ədəd şəkil WebP formatına çevrildi!")
            ) 