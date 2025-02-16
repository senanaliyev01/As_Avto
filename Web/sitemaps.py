from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return [
            'anaevim',  # Ana səhifə
        ]

    def location(self, item):
        return reverse(item)

class MehsulSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, obj):
        return obj.yaradilma_tarixi if hasattr(obj, 'yaradilma_tarixi') else timezone.now()

    def location(self, obj):
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': obj.adi,
            'mehsul_oem': obj.oem,
            'mehsul_brend_kod': obj.brend_kod,
            'mehsul_id': obj.id
        })

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 