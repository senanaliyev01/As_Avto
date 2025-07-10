from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return reverse('product_detail', args=[obj.id])

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ['home', 'products', 'orders', 'cart']

    def location(self, item):
        return reverse(item) 