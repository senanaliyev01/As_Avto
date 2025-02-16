from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files import File
from mehsullar.models import Mehsul, Brend, MarkaSekil
import os
from django.conf import settings
import shutil

class Command(BaseCommand):
    help = 'Mövcud şəkillərin adlarını yenidən təyin edir'

    def handle(self, *args, **options):
        # Məhsul şəkillərini yenidən adlandır
        for mehsul in Mehsul.objects.all():
            if mehsul.sekil:
                # Köhnə fayl yolunu al
                old_path = mehsul.sekil.path
                if os.path.exists(old_path):
                    # Yeni ad yarat
                    ext = os.path.splitext(old_path)[1]  # Faylın uzantısını al
                    new_name = f"mehsul_sekilleri/{mehsul.brend_kod}{ext}"
                    new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                    
                    # Əmin ol ki, hədəf qovluq mövcuddur
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    try:
                        # Faylı yeni ada kopyala
                        shutil.copy2(old_path, new_path)
                        # Köhnə faylı sil
                        os.remove(old_path)
                        # Məhsulun şəkil sahəsini yenilə
                        mehsul.sekil.name = new_name
                        mehsul.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Məhsul şəkli yenidən adlandırıldı: {new_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Xəta: {str(e)}'))

        # Brend şəkillərini yenidən adlandır
        for brend in Brend.objects.all():
            if brend.sekil:
                old_path = brend.sekil.path
                if os.path.exists(old_path):
                    ext = os.path.splitext(old_path)[1]
                    new_name = f"brend_sekilleri/brend_{brend.id}{ext}"
                    new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    try:
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        brend.sekil.name = new_name
                        brend.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Brend şəkli yenidən adlandırıldı: {new_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Xəta: {str(e)}'))

        # Marka şəkillərini yenidən adlandır
        for marka_sekil in MarkaSekil.objects.all():
            if marka_sekil.sekil:
                old_path = marka_sekil.sekil.path
                if os.path.exists(old_path):
                    ext = os.path.splitext(old_path)[1]
                    new_name = f"marka_sekilleri/marka_{marka_sekil.marka.id}{ext}"
                    new_path = os.path.join(settings.MEDIA_ROOT, new_name)
                    
                    os.makedirs(os.path.dirname(new_path), exist_ok=True)
                    
                    try:
                        shutil.copy2(old_path, new_path)
                        os.remove(old_path)
                        marka_sekil.sekil.name = new_name
                        marka_sekil.save(update_fields=['sekil'])
                        self.stdout.write(self.style.SUCCESS(f'Marka şəkli yenidən adlandırıldı: {new_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Xəta: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Bütün şəkillər uğurla yenidən adlandırıldı')) 