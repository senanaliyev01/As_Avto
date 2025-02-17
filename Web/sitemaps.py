from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote

class StaticViewSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9

    def items(self):
        return [
            'anaevim',  # Ana səhifə
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return timezone.now()

class MehsulSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, obj):
        return timezone.now()

    def location(self, obj):
        # URL-dəki xüsusi simvolları düzgün kodlaşdırırıq
        encoded_name = quote(obj.adi)
        encoded_oem = quote(obj.oem)
        encoded_brand_code = quote(obj.brend_kod)
        
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': encoded_name,
            'mehsul_oem': encoded_oem,
            'mehsul_brend_kod': encoded_brand_code,
            'mehsul_id': obj.id
        })

    def image_location(self, item):
        if item.sekil:
            return f"https://as-avto.com{item.sekil.url}"
        return None

    def image_title(self, item):
        return f"{item.adi} {item.brend_kod}"

    def image_caption(self, item):
        return f"{item.adi} - {item.brend.adi} {item.marka.adi} {item.brend_kod} {item.oem}"

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 