from django.core.management.base import BaseCommand
from django_elasticsearch_dsl.registries import registry
from elasticsearch.exceptions import NotFoundError
import time
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Elasticsearch indekslərini yenidən qurur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Mövcud indeksləri silir və yenidən yaradır',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        self.stdout.write(self.style.SUCCESS('Elasticsearch indekslərini yenidən qurma prosesi başladı...'))
        
        # Bütün qeydiyyatdan keçmiş sənədləri əldə edirik
        for index in registry.get_indices():
            index_name = index._name
            self.stdout.write(f"İndeks işlənir: {index_name}")
            
            if force:
                try:
                    # İndeksi silirik
                    self.stdout.write(f"İndeks silinir: {index_name}")
                    index.delete(ignore=404)
                    self.stdout.write(self.style.SUCCESS(f"İndeks silindi: {index_name}"))
                    
                    # İndeksi yenidən yaradırıq
                    self.stdout.write(f"İndeks yaradılır: {index_name}")
                    index.create()
                    self.stdout.write(self.style.SUCCESS(f"İndeks yaradıldı: {index_name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"İndeks silinərkən/yaradılarkən xəta baş verdi: {str(e)}"))
                    logger.error(f"İndeks silinərkən/yaradılarkən xəta baş verdi: {str(e)}")
            
            # Bütün sənədləri yenidən indeksləyirik
            start_time = time.time()
            self.stdout.write(f"Sənədlər indekslənir: {index_name}")
            
            try:
                # İndeksdəki bütün sənədləri əldə edirik
                document_models = registry.get_documents()
                for doc in document_models:
                    if doc()._index._name == index_name:
                        self.stdout.write(f"Model indekslənir: {doc.Django.model.__name__}")
                        doc().update()
                        self.stdout.write(self.style.SUCCESS(f"Model indeksləndi: {doc.Django.model.__name__}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Sənədlər indekslənərkən xəta baş verdi: {str(e)}"))
                logger.error(f"Sənədlər indekslənərkən xəta baş verdi: {str(e)}")
            
            end_time = time.time()
            self.stdout.write(self.style.SUCCESS(
                f"İndeks {index_name} üçün indeksləmə tamamlandı. Vaxt: {end_time - start_time:.2f} saniyə"
            ))
        
        self.stdout.write(self.style.SUCCESS('Bütün indekslər yenidən quruldu!')) 