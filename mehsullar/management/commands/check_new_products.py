from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from mehsullar.models import Mehsul

class Command(BaseCommand):
    help = 'Yeni məhsulların statusunu yoxlayır və yeniləyir'

    def handle(self, *args, **kwargs):
        # 1 həftədən çox vaxt keçmiş məhsulları tap
        one_week_ago = timezone.now() - timedelta(days=7)
        old_products = Mehsul.objects.filter(
            yenidir=True,
            elave_edilme_tarixi__lt=one_week_ago
        )

        # Statusları yenilə
        updated_count = old_products.update(yenidir=False)

        self.stdout.write(
            self.style.SUCCESS(
                f'{updated_count} məhsulun statusu "köhnə" olaraq yeniləndi'
            )
        ) 