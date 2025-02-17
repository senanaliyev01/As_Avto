from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote

class StaticViewSitemap(Sitemap):
    changefreq = "always"  # hər zaman yenilənə bilər
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
    changefreq = "always"  # hər zaman yenilənə bilər
    priority = 0.9

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = 'https'

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

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items = self.items()

        for item in all_items:
            loc = f"{protocol}://{domain}{self.location(item)}"
            priority = self.priority
            lastmod = self.lastmod(item) if self.lastmod is not None else None

            url_info = {
                'item': item,
                'location': loc,
                'lastmod': lastmod,
                'changefreq': self.changefreq,
                'priority': str(priority if priority is not None else ''),
            }

            if item.sekil:  # Əgər şəkil varsa
                url_info['images'] = [{
                    'loc': f"{protocol}://{domain}{item.sekil.url}",
                    'title': f"{item.adi} {item.brend_kod}",
                    'caption': f"{item.adi} - {item.brend.adi} {item.marka.adi} {item.brend_kod} {item.oem}"
                }]

            urls.append(url_info)
            if lastmod is not None:
                if latest_lastmod is None or lastmod > latest_lastmod:
                    latest_lastmod = lastmod

        if latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 