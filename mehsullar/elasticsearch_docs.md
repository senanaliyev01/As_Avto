# Elasticsearch Axtarış Sistemi

Bu sənəd, layihədə istifadə olunan Elasticsearch axtarış sisteminin qurulması, konfiqurasiyası və istifadəsi haqqında ətraflı məlumat verir.

## Ümumi Məlumat

Elasticsearch, məhsullar üçün professional axtarış sistemi təmin edir və aşağıdakı üstünlükləri var:

1. **Daha Dəqiq Axtarış Nəticələri**:
   - Fuzzy axtarış - yazı səhvlərini düzəldir
   - Fraza axtarışı - dəqiq uyğunluqlar üçün
   - Çoxdilli dəstək - Azərbaycan dili dəstəyi

2. **Daha Sürətli Axtarış**:
   - Elasticsearch indeksləmə ilə sürətli axtarış
   - Təkrarlanan axtarışlar üçün keşləmə

3. **Daha Ağıllı Axtarış**:
   - Məhsul məlumatları, axtarış sözləri və OEM kodları üzrə axtarış
   - Ən uyğun nəticələrin qaytarılması

4. **Avtomatik Yenilənən İndekslər**:
   - Məhsullar əlavə edildikdə, dəyişdirildikdə və ya silindikdə indekslər avtomatik yenilənir
   - Axtarış sözləri və OEM kodları dəyişdikdə də yenilənir

5. **Xətalara Davamlılıq**:
   - Elasticsearch əlçatan olmadıqda standart axtarışa qayıdır
   - Xətaların qeydiyyatı və izlənməsi

## Quraşdırma

### 1. Elasticsearch Serverin Quraşdırılması

Elasticsearch serverini quraşdırmaq üçün:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install elasticsearch

# CentOS/RHEL
sudo yum install elasticsearch

# Docker ilə
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.14.0
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.14.0
```

### 2. Django Layihəsində Konfiqurasiya

`settings.py` faylında Elasticsearch konfiqurasiyasını əlavə edin:

```python
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://188.245.112.154:9200'
    },
}
```

### 3. İndekslərin Yaradılması

İndeksləri yaratmaq üçün aşağıdakı əmri işə salın:

```bash
python manage.py rebuild_elasticsearch --force
```

Bu əmr, bütün mövcud indeksləri silir və yenidən yaradır.

### 4. Bağlantını Yoxlamaq

Elasticsearch bağlantısını yoxlamaq üçün:

```bash
python manage.py check_elasticsearch
```

## İstifadə

### Axtarış Funksiyası

Elasticsearch ilə axtarış üçün `search_with_elasticsearch` funksiyası istifadə olunur:

```python
from mehsullar.views import search_with_elasticsearch

# Axtarış
results = search_with_elasticsearch(query_text="axtarış sözü")
```

### Siqnallar

Məhsullar, axtarış sözləri və OEM kodları dəyişdikdə indekslərin avtomatik yenilənməsi üçün Django siqnalları istifadə olunur. Bu siqnallar `mehsullar/signals.py` faylında təyin edilib və `mehsullar/apps.py` faylında qeydiyyatdan keçirilib.

## Xəta Həlli

### Ümumi Problemlər

1. **Bağlantı Xətaları**:
   - Elasticsearch serverin işlək olduğunu yoxlayın
   - Host və port konfiqurasiyasının düzgün olduğunu yoxlayın
   - Firewall və ya şəbəkə məhdudiyyətlərini yoxlayın

2. **İndeksləmə Xətaları**:
   - Xəta jurnallarını yoxlayın
   - İndeksləri yenidən yaratmağı sınayın: `python manage.py rebuild_elasticsearch --force`

3. **Axtarış Xətaları**:
   - Elasticsearch serverin işlək olduğunu yoxlayın
   - İndekslərin mövcud olduğunu yoxlayın: `python manage.py check_elasticsearch`

### Elasticsearch Vəziyyətini Yoxlamaq

```bash
# Serverin vəziyyətini yoxlamaq
curl -X GET "http://188.245.112.154:9200"

# İndeksləri yoxlamaq
curl -X GET "http://188.245.112.154:9200/_cat/indices"

# Klaster sağlamlığını yoxlamaq
curl -X GET "http://188.245.112.154:9200/_cluster/health"
```

## Əlavə Resurslar

- [Elasticsearch Rəsmi Sənədləri](https://www.elastic.co/guide/index.html)
- [Django Elasticsearch DSL](https://django-elasticsearch-dsl.readthedocs.io/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)

## Əlavə Qeydlər

- Elasticsearch 7.x versiyası ilə test edilib
- Böyük həcmli məlumatlar üçün indeksləmə prosesi uzun çəkə bilər
- Mürəkkəb axtarışlar üçün Elasticsearch DSL istifadə edin 