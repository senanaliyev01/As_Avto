from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Mehsul, AxtarisSozleri, OEMKod

@registry.register_document
class MehsulDocument(Document):
    # Əsas məlumatlar
    id = fields.IntegerField()
    adi = fields.TextField(
        attr='adi',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    
    # Əlaqəli məlumatlar
    kateqoriya = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'adi': fields.TextField(fields={'raw': fields.KeywordField()}),
    })
    
    brend = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'adi': fields.TextField(fields={'raw': fields.KeywordField()}),
    })
    
    marka = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'adi': fields.TextField(fields={'raw': fields.KeywordField()}),
    })
    
    # Axtarış sözləri
    axtaris_sozleri_text = fields.TextField()
    
    # OEM kodları
    oem = fields.TextField(
        attr='oem',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    
    oem_kodlar = fields.TextField(multi=True)
    
    # Digər məlumatlar
    brend_kod = fields.TextField(
        attr='brend_kod',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    
    haqqinda = fields.TextField()
    
    qiymet = fields.FloatField()
    stok = fields.IntegerField()
    
    class Index:
        name = 'mehsullar'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'az_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'az_stop', 'az_stemmer']
                    }
                },
                'filter': {
                    'az_stop': {
                        'type': 'stop',
                        'stopwords': '_english_'  # Azərbaycan dili üçün stop sözlər əlavə edilə bilər
                    },
                    'az_stemmer': {
                        'type': 'stemmer',
                        'language': 'english'  # Azərbaycan dili üçün stemmer əlavə edilə bilər
                    }
                }
            }
        }
    
    class Django:
        model = Mehsul
        fields = [
            'yenidir',
        ]
        
        # Əlaqəli obyektləri əlavə et
        related_models = [AxtarisSozleri, OEMKod]
    
    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, AxtarisSozleri):
            return related_instance.mehsullar.all()
        elif isinstance(related_instance, OEMKod):
            return [related_instance.mehsul]
    
    def prepare_kateqoriya(self, instance):
        return {
            'id': instance.kateqoriya.id,
            'adi': instance.kateqoriya.adi
        } if instance.kateqoriya else None
    
    def prepare_brend(self, instance):
        return {
            'id': instance.brend.id,
            'adi': instance.brend.adi
        } if instance.brend else None
    
    def prepare_marka(self, instance):
        return {
            'id': instance.marka.id,
            'adi': instance.marka.adi
        } if instance.marka else None
    
    def prepare_axtaris_sozleri_text(self, instance):
        if instance.axtaris_sozleri:
            return instance.axtaris_sozleri.sozler
        return ""
    
    def prepare_oem_kodlar(self, instance):
        return [oem.kod for oem in instance.oem_kodlar.all()] 