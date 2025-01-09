from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from istifadeciler.models import Profile

class Command(BaseCommand):
    help = 'Profili olmayan istifadəçilər üçün profil yaradır'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'{created_count} istifadəçi üçün yeni profil yaradıldı'
            )
        ) 