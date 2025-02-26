from django.core.management.base import BaseCommand
from django.utils import timezone
from mehsullar.models import Mehsul

class Command(BaseCommand):
    help = 'Yeni məhsulların statusunu yoxlayır və yeniləyir'

    def handle(self, *args, **kwargs):
        bir_hefte = timezone.timedelta(days=7)
        kohne_mehsullar = Mehsul.objects.filter(
            yenidir=True,
            elave_edilme_tarixi__lt=timezone.now() - bir_hefte
        )
        
        updated_count = kohne_mehsullar.update(yenidir=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'{updated_count} məhsulun statusu yeniləndi')
        ) 