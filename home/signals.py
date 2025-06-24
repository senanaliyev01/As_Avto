from django.db.models.signals import post_save
from django.dispatch import receiver
from home.models import Mehsul
import threading
import time

@receiver(post_save, sender=Mehsul)
def reset_yenidir_signal(sender, instance, created, **kwargs):
    if instance.yenidir:
        def reset_yenidir(pk):
            time.sleep(10)
            try:
                obj = Mehsul.objects.get(pk=pk)
                if obj.yenidir:
                    obj.yenidir = False
                    obj.save(update_fields=['yenidir'])
            except Mehsul.DoesNotExist:
                pass
        threading.Thread(target=reset_yenidir, args=(instance.pk,), daemon=True).start() 