from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from .models import Mehsul

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, obj):
        return obj.yeni_edildiyi_tarix if hasattr(obj, 'yeni_edildiyi_tarix') else None

    def location(self, obj):
        return reverse('product_detail', args=[obj.id])

    def get_urls(self, site=None, **kwargs):
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            url['location'] = url['location'].replace('http://', 'https://')
            # Şəkil üçün tam URL əlavə et
            obj = url.get('item')
            if obj and hasattr(obj, 'sekil') and obj.sekil:
                if site:
                    domain = f"https://{site.domain}" if not site.domain.startswith('http') else site.domain
                else:
                    domain = 'https://as-avto.com'
                url['image_absolute_url'] = domain + obj.sekil.url
                # Şəkil üçün ətraflı metadata
                url['image_title'] = f"{obj.adi} - {obj.brend_kod}"
                url['image_caption'] = f"{obj.adi} - {obj.brend_kod} {obj.firma.adi} {obj.avtomobil.adi}"
                url['image_license'] = "https://as-avto.com"
                url['image_geo_location'] = "Bakı, Azərbaycan"
                url['image_geo_region'] = "AZ"
                url['image_geo_placename'] = "Bakı"
                url['image_geo_position'] = "40.3777;49.8920"
                url['image_geo_title'] = f"{obj.adi} - {obj.brend_kod} - AS-AVTO"
                url['image_license_url'] = "https://as-avto.com"
                url['image_license_title'] = "AS-AVTO"
                # Məhsul məlumatları
                url['product_name'] = obj.adi
                url['product_code'] = obj.brend_kod
                url['product_brand'] = obj.firma.adi
                url['product_vehicle'] = obj.avtomobil.adi
                url['product_price'] = str(obj.qiymet)
                url['product_stock'] = obj.stok
                url['product_description'] = obj.melumat or f"{obj.adi} - {obj.brend_kod} {obj.firma.adi} {obj.avtomobil.adi}"
                url['product_category'] = obj.kateqoriya.adi if obj.kateqoriya else "Avtomobil Ehtiyat Hissələri"
                url['product_size'] = obj.olcu or ""
                # Structured Data məlumatları
                url['schema_name'] = obj.adi
                url['schema_mpn'] = obj.brend_kod
                url['schema_vehicle_model'] = obj.avtomobil.adi
                url['schema_brand_name'] = obj.firma.adi
                url['schema_price_currency'] = "AZN"
                url['schema_price'] = str(obj.qiymet)
                url['schema_availability'] = "InStock" if obj.stok > 0 else "OutOfStock"
                url['schema_sku'] = str(obj.id)
                url['schema_description'] = obj.melumat or f"{obj.adi} - {obj.brend_kod} {obj.firma.adi} {obj.avtomobil.adi}"
                # Rating məlumatları (əgər varsa)
                from django.db.models import Avg, Count
                ratings = obj.ratings.all()
                if ratings.exists():
                    avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']
                    review_count = ratings.count()
                    url['schema_rating_value'] = str(round(avg_rating, 1))
                    url['schema_review_count'] = str(review_count)
                else:
                    url['schema_rating_value'] = "0.0"
                    url['schema_review_count'] = "0"
                # Like məlumatları
                like_count = obj.likes.count()
                url['schema_like_count'] = str(like_count)
            else:
                url['image_absolute_url'] = ''
                url['image_title'] = ''
                url['image_caption'] = ''
                url['image_license'] = ''
                url['image_geo_location'] = ''
                url['image_geo_region'] = ''
                url['image_geo_placename'] = ''
                url['image_geo_position'] = ''
                url['image_geo_title'] = ''
                url['image_license_url'] = ''
                url['image_license_title'] = ''
                url['product_name'] = ''
                url['product_code'] = ''
                url['product_brand'] = ''
                url['product_vehicle'] = ''
                url['product_price'] = ''
                url['product_stock'] = ''
                url['product_description'] = ''
                url['product_category'] = ''
                url['product_size'] = ''
                url['schema_name'] = ''
                url['schema_mpn'] = ''
                url['schema_vehicle_model'] = ''
                url['schema_brand_name'] = ''
                url['schema_price_currency'] = ''
                url['schema_price'] = ''
                url['schema_availability'] = ''
                url['schema_sku'] = ''
                url['schema_description'] = ''
                url['schema_rating_value'] = ''
                url['schema_review_count'] = ''
                url['schema_like_count'] = ''
        return urls

    def image_urls(self, obj):
        if obj.sekil:
            return [obj.sekil.url]
        return []

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        # Açıq səhifələrin URL adları (orders, cart, checkout, liked_products çıxarıldı):
        return [
            'root', 'login', 'register', 'base', 'products', 'new_products', 'search_suggestions', 'product_detail'
        ]

    def location(self, item):
        if item == 'product_detail':
            # Bir nümunə məhsul üçün göstərmək üçün (əslində bütün məhsullar ProductSitemap-dadır)
            return reverse(item, args=[1])
        return reverse(item) 