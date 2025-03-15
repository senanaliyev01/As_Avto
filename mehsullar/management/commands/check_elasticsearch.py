from django.core.management.base import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Elasticsearch bağlantısını və konfiqurasiyasını yoxlayır'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Elasticsearch bağlantısı yoxlanılır...'))
        
        # Elasticsearch konfiqurasiyasını əldə edirik
        es_hosts = settings.ELASTICSEARCH_DSL.get('default', {}).get('hosts', '')
        self.stdout.write(f"Elasticsearch host: {es_hosts}")
        
        try:
            # Elasticsearch ilə bağlantı qururuq
            es = Elasticsearch(es_hosts)
            
            # Bağlantını yoxlayırıq
            if es.ping():
                self.stdout.write(self.style.SUCCESS('Elasticsearch bağlantısı uğurludur!'))
                
                # Elasticsearch haqqında məlumat əldə edirik
                info = es.info()
                self.stdout.write(f"Elasticsearch versiyası: {info['version']['number']}")
                self.stdout.write(f"Cluster adı: {info['cluster_name']}")
                
                # İndeksləri əldə edirik
                indices = es.indices.get_alias(index="*")
                self.stdout.write(f"Mövcud indekslər: {', '.join(indices.keys())}")
                
                # Mehsullar indeksini yoxlayırıq
                if 'mehsullar' in indices:
                    self.stdout.write(self.style.SUCCESS('Mehsullar indeksi mövcuddur!'))
                    
                    # İndeks haqqında məlumat əldə edirik
                    index_stats = es.indices.stats(index="mehsullar")
                    doc_count = index_stats['_all']['primaries']['docs']['count']
                    self.stdout.write(f"Mehsullar indeksində {doc_count} sənəd var")
                    
                    # Mapping əldə edirik
                    mapping = es.indices.get_mapping(index="mehsullar")
                    self.stdout.write(f"Mehsullar indeksi mapping: {json.dumps(mapping, indent=2)}")
                else:
                    self.stdout.write(self.style.WARNING('Mehsullar indeksi mövcud deyil!'))
                    self.stdout.write('İndeksi yaratmaq üçün "python manage.py rebuild_elasticsearch --force" əmrini işə salın')
            else:
                self.stdout.write(self.style.ERROR('Elasticsearch bağlantısı uğursuz oldu!'))
                self.stdout.write('Elasticsearch serverin işlək olduğunu və konfiqurasiyaların düzgün olduğunu yoxlayın')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Elasticsearch bağlantısı zamanı xəta: {str(e)}'))
            self.stdout.write('Xəta detalları:')
            import traceback
            self.stdout.write(traceback.format_exc())
            
            # Konfiqurasiya məsləhətləri
            self.stdout.write(self.style.WARNING('Konfiqurasiya məsləhətləri:'))
            self.stdout.write('1. Elasticsearch serverin işlək olduğunu yoxlayın')
            self.stdout.write('2. Host və port konfiqurasiyasının düzgün olduğunu yoxlayın')
            self.stdout.write('3. Firewall və ya şəbəkə məhdudiyyətlərini yoxlayın')
            self.stdout.write('4. Elasticsearch serverin SSL/TLS konfiqurasiyasını yoxlayın')
            self.stdout.write('5. Elasticsearch serverin autentifikasiya tələblərini yoxlayın')
            
            # Düzgün konfiqurasiya nümunəsi
            self.stdout.write(self.style.SUCCESS('Düzgün konfigurasiya nümunəsi:'))
            self.stdout.write("""
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://host:port'
    },
}
            """)
            
            # Əlavə məlumat
            self.stdout.write(self.style.SUCCESS('Əlavə məlumat:'))
            self.stdout.write('Elasticsearch serverin vəziyyətini yoxlamaq üçün: curl -X GET "http://host:port"')
            self.stdout.write('Elasticsearch indekslərini yoxlamaq üçün: curl -X GET "http://host:port/_cat/indices"')
            self.stdout.write('Elasticsearch sağlamlığını yoxlamaq üçün: curl -X GET "http://host:port/_cluster/health"') 