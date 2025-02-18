from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote, unquote

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
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
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, obj):
        return timezone.now()

    def location(self, obj):
        # URL-dəki xüsusi simvolları düzgün kodlaşdırırıq
        temiz_adi = slugify(obj.adi.replace('%', ''))
        temiz_oem = obj.oem.replace('%', '')
        temiz_brend_kod = obj.brend_kod.replace('%', '')
        
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': temiz_adi,
            'mehsul_oem': temiz_oem,
            'mehsul_brend_kod': temiz_brend_kod,
            'mehsul_id': obj.id
        })

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True

        for item in self.paginator.page(page).object_list:
            loc = f"{protocol}://{domain}{self._location(item)}"
            priority = self._get('priority', item)
            lastmod = self._get('lastmod', item)

            if all_items_lastmod and lastmod is None:
                all_items_lastmod = False
            elif all_items_lastmod:
                if latest_lastmod is None:
                    latest_lastmod = lastmod
                else:
                    latest_lastmod = max(latest_lastmod, lastmod)

            url_info = {
                'item': item,
                'location': loc,
                'lastmod': lastmod,
                'changefreq': self._get('changefreq', item),
                'priority': str(priority if priority is not None else ''),
            }

            # Şəkil məlumatlarını əlavə edirik
            if hasattr(item, 'sekil') and item.sekil:
                # Şəkil URL-ni olduğu kimi saxlayırıq
                sekil_path = item.sekil.url
                # Yalnız % işarələrini təmizləyirik
                sekil_path = sekil_path.replace('%25', '%').replace('%20', ' ')
                
                url_info['images'] = [{
                    'loc': f"{protocol}://{domain}{sekil_path}",
                    'title': item.adi,
                    'caption': f"{item.adi} - {item.brend.adi} - {item.brend_kod} - {item.oem}"
                }]

            urls.append(url_info)

        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 