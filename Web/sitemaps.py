from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote
from datetime import datetime
import pytz

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
    last_modified = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_modified = timezone.now()
        
    def items(self):
        # Son yenilənmə vaxtını yenilə
        self.last_modified = timezone.now()
        return Mehsul.objects.all()

    def lastmod(self, mehsul):
        return self.last_modified

    def location(self, mehsul):
        # URL-dəki xüsusi simvolları düzgün kodlaşdırırıq
        encoded_name = quote(mehsul.adi)
        encoded_oem = quote(mehsul.oem)
        encoded_brand_code = quote(mehsul.brend_kod)
        
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': encoded_name,
            'mehsul_oem': encoded_oem,
            'mehsul_brend_kod': encoded_brand_code,
            'mehsul_id': mehsul.id
        })
        
    def image_location(self, mehsul):
        if mehsul.sekil:
            return f"https://as-avto.com{mehsul.sekil.url}"
        return None

    def image_caption(self, mehsul):
        return f"{mehsul.adi} - {mehsul.brend.adi} - {mehsul.oem} - {mehsul.brend_kod}"

    def image_title(self, mehsul):
        return mehsul.adi

    @classmethod
    def get_last_modified(cls):
        return cls.last_modified.strftime("%Y-%m-%d %H:%M:%S") if cls.last_modified else "Hələ yenilənməyib"

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 