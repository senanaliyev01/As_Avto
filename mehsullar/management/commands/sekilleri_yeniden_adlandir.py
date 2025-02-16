from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files import File
from mehsullar.models import Mehsul, Brend, MarkaSekil
import os
from django.conf import settings
import shutil
import hashlib
from datetime import datetime

class Command(BaseCommand):
    help = 'Mövcud şəkillərin adlarını yenidən təyin edir'

    def generate_unique_name(self, original_name, identifier, category):
        # Şəklin hash-ini yaradırıq
        hash_object = hashlib.md5(original_name.encode())
        file_hash = hash_object.hexdigest()[:8]
        
        # Faylın uzantısını alırıq
        ext = os.path.splitext(original_name)[1].lower()
        
        # Tarixi əlavə edirik
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Təmiz ad yaradırıq
        clean_identifier = ''.join(e for e in identifier if e.isalnum() or e == '_').lower()
        
        # Yeni adı formalaşdırırıq
        new_name = f"{category}/{clean_identifier}_{timestamp}_{file_hash}{ext}"
        
        return new_name

    def handle(self, *args, **options):
        # Məhsul şəkillərini yenidən adlandır
        for mehsul in Mehsul.objects.all():
            if mehsul.sekil:
                try:
                    old_path = mehsul.sekil.path
                    if os.path.exists(old_path):
                        # Unikal identifikator yaradırıq
                        identifier = f"{mehsul.brend.adi}_{mehsul.brend_kod}_{mehsul.id}"
                        new_name = self.generate_unique_name(
                            mehsul.sekil.name,
                            identifier,
                            "mehsul_sekilleri"
                        )
                        
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        mehsul.sekil.name = new_name
                        mehsul.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Məhsul şəkli yenidən adlandırıldı: {new_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Xəta: {str(e)} - Məhsul ID: {mehsul.id}'))

        # Brend şəkillərini yenidən adlandır
        for brend in Brend.objects.all():
            if brend.sekil:
                try:
                    old_path = brend.sekil.path
                    if os.path.exists(old_path):
                        identifier = f"brend_{brend.adi}_{brend.id}"
                        new_name = self.generate_unique_name(
                            brend.sekil.name,
                            identifier,
                            "brend_sekilleri"
                        )
                        
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        brend.sekil.name = new_name
                        brend.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Brend şəkli yenidən adlandırıldı: {new_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Xəta: {str(e)} - Brend ID: {brend.id}'))

            if brend.sekilyazi:
                try:
                    old_path = brend.sekilyazi.path
                    if os.path.exists(old_path):
                        identifier = f"brend_yazi_{brend.adi}_{brend.id}"
                        new_name = self.generate_unique_name(
                            brend.sekilyazi.name,
                            identifier,
                            "brend_yazilari"
                        )
                        
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        brend.sekilyazi.name = new_name
                        brend.save(update_fields=['sekilyazi'])
                        self.stdout.write(self.style.SUCCESS(f'Brend yazı şəkli yenidən adlandırıldı: {new_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Xəta: {str(e)} - Brend ID: {brend.id}'))

        # Marka şəkillərini yenidən adlandır
        for marka_sekil in MarkaSekil.objects.all():
            if marka_sekil.sekil:
                try:
                    old_path = marka_sekil.sekil.path
                    if os.path.exists(old_path):
                        identifier = f"marka_{marka_sekil.marka.adi}_{marka_sekil.id}"
                        new_name = self.generate_unique_name(
                            marka_sekil.sekil.name,
                            identifier,
                            "marka_sekilleri"
                        )
                        
                        new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                        os.makedirs(os.path.dirname(new_path), exist_ok=True)
                        
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        marka_sekil.sekil.name = new_name
                        marka_sekil.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Marka şəkli yenidən adlandırıldı: {new_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Xəta: {str(e)} - Marka Şəkil ID: {marka_sekil.id}'))

        self.stdout.write(self.style.SUCCESS('Bütün şəkillər uğurla yenidən adlandırıldı')) 