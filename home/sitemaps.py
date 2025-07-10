from django.contrib.sitemaps import Sitemap
from django.urls import reverse
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

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ['home', 'products', 'orders', 'cart']

    def location(self, item):
        return reverse(item) 