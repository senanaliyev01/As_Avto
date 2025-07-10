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
        # HTTPS-i məcburi et
        for url in urls:
            url['location'] = url['location'].replace('http://', 'https://')
        return urls

    def image_urls(self, obj):
        # Google image sitemap üçün
        if obj.sekil:
            return [obj.sekil.url]
        return []

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ['root', 'products', 'orders', 'cart']

    def location(self, item):
        return reverse(item) 