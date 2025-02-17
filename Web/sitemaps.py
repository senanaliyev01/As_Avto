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
        # Hər saniyə yenilənmə üçün cari vaxtı qaytarırıq
        return timezone.now()

class MehsulSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, mehsul):
        # Hər saniyə yenilənmə üçün cari vaxtı qaytarırıq
        return timezone.now()

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

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 