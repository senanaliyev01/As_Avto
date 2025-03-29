from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote
import re

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
        # məhsul adında və kodlarda olan xüsusi simvollar düzgün işləməyə bilər
        # əvvəlcə slugify və sonra URL encoding tətbiq edək
        
        # Xüsusi simvolları temizləyək
        clean_name = re.sub(r'[^\w\s-]', '', str(obj.adi)) if obj.adi else ''
        clean_oem = re.sub(r'[^\w\s-]', '', str(obj.oem)) if obj.oem else ''
        clean_brand_code = re.sub(r'[^\w\s-]', '', str(obj.brend_kod)) if obj.brend_kod else ''
        
        # Slugify edək
        slug_name = slugify(clean_name)
        slug_oem = slugify(clean_oem)
        slug_brand_code = slugify(clean_brand_code)
        
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': slug_name,
            'mehsul_oem': slug_oem,
            'mehsul_brend_kod': slug_brand_code,
            'mehsul_id': obj.id
        })

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod

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

            # Şəkil məlumatlarını əlavə edirik, xüsusi simvolları təmizləyərək
            if hasattr(item, 'sekil') and item.sekil:
                # Xüsusi simvolları təmizləyirik ki JSON formatlaşdırma xətası olmasın
                safe_title = re.sub(r'[^\w\s-]', '', str(item.adi)) if item.adi else ''
                safe_brend = re.sub(r'[^\w\s-]', '', str(item.brend.adi)) if item.brend and item.brend.adi else ''
                safe_brend_kod = re.sub(r'[^\w\s-]', '', str(item.brend_kod)) if item.brend_kod else ''
                safe_oem = re.sub(r'[^\w\s-]', '', str(item.oem)) if item.oem else ''
                
                caption = f"{safe_title} - {safe_brend} - {safe_brend_kod} - {safe_oem}"
                
                url_info['images'] = [{
                    'loc': f"{protocol}://{domain}{item.sekil.url}",
                    'title': safe_title,
                    'caption': caption
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