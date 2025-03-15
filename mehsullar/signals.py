from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Mehsul, AxtarisSozleri, OEMKod
from django_elasticsearch_dsl.registries import registry
import logging

logger = logging.getLogger(__name__)

# Mehsul modelində dəyişiklik olduqda
@receiver(post_save, sender=Mehsul)
def update_mehsul_document(sender, instance, **kwargs):
    """
    Mehsul obyekti yeniləndikdə Elasticsearch indeksini yeniləyir
    """
    try:
        registry.update(instance)
        logger.info(f"Mehsul {instance.id} Elasticsearch-də yeniləndi")
    except Exception as e:
        logger.error(f"Mehsul {instance.id} Elasticsearch-də yenilənərkən xəta: {str(e)}")

# Mehsul silinəndə
@receiver(post_delete, sender=Mehsul)
def delete_mehsul_document(sender, instance, **kwargs):
    """
    Mehsul obyekti silindikdə Elasticsearch indeksindən silir
    """
    try:
        registry.delete(instance)
        logger.info(f"Mehsul {instance.id} Elasticsearch-dən silindi")
    except Exception as e:
        logger.error(f"Mehsul {instance.id} Elasticsearch-dən silinərkən xəta: {str(e)}")

# AxtarisSozleri modelində dəyişiklik olduqda
@receiver(post_save, sender=AxtarisSozleri)
def update_axtaris_sozleri_documents(sender, instance, **kwargs):
    """
    AxtarisSozleri obyekti yeniləndikdə əlaqəli Mehsul obyektlərinin Elasticsearch indeksini yeniləyir
    """
    try:
        for mehsul in instance.mehsullar.all():
            registry.update(mehsul)
        logger.info(f"AxtarisSozleri {instance.id} ilə əlaqəli məhsullar Elasticsearch-də yeniləndi")
    except Exception as e:
        logger.error(f"AxtarisSozleri {instance.id} ilə əlaqəli məhsullar Elasticsearch-də yenilənərkən xəta: {str(e)}")

# OEMKod modelində dəyişiklik olduqda
@receiver(post_save, sender=OEMKod)
def update_oem_kod_document(sender, instance, **kwargs):
    """
    OEMKod obyekti yeniləndikdə əlaqəli Mehsul obyektinin Elasticsearch indeksini yeniləyir
    """
    try:
        registry.update(instance.mehsul)
        logger.info(f"OEMKod {instance.id} ilə əlaqəli məhsul Elasticsearch-də yeniləndi")
    except Exception as e:
        logger.error(f"OEMKod {instance.id} ilə əlaqəli məhsul Elasticsearch-də yenilənərkən xəta: {str(e)}")

# OEMKod silinəndə
@receiver(post_delete, sender=OEMKod)
def delete_oem_kod_document(sender, instance, **kwargs):
    """
    OEMKod obyekti silindikdə əlaqəli Mehsul obyektinin Elasticsearch indeksini yeniləyir
    """
    try:
        registry.update(instance.mehsul)
        logger.info(f"OEMKod silindikdən sonra əlaqəli məhsul Elasticsearch-də yeniləndi")
    except Exception as e:
        logger.error(f"OEMKod silindikdən sonra əlaqəli məhsul Elasticsearch-də yenilənərkən xəta: {str(e)}") 