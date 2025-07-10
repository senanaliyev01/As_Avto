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