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
        # Bütün xüsusi simvolları və boşluqları təmizləyirik
        
        # Adi sahəsi üçün - boşluqlar qalsın, digər simvollar təmizlənsin
        clean_name = re.sub(r'[^\w\s]', '-', str(obj.adi))
        # Sonra boşluqları birbaşa - simvoluna çeviririk 
        clean_name = clean_name.replace(' ', '-')
        
        # OEM və brend_kod üçün bütün xüsusi simvollar və boşluqlar təmizlənsin
        clean_oem = re.sub(r'[^\w]', '-', str(obj.oem))
        clean_brand_code = re.sub(r'[^\w]', '-', str(obj.brend_kod))
        
        # Bütün ardıcıl - simvollarını bir - simvoluna çeviririk
        clean_name = re.sub(r'-+', '-', clean_name).strip('-')
        clean_oem = re.sub(r'-+', '-', clean_oem).strip('-')
        clean_brand_code = re.sub(r'-+', '-', clean_brand_code).strip('-')
        
        # URL-ni manual olaraq yaradırıq (view name əvəzinə path istifadə etdiyimiz üçün)
        return f"/product-detail/{clean_name}-{clean_oem}-{clean_brand_code}/{obj.id}/"

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

            # Şəkil məlumatlarını əlavə edirik
            if hasattr(item, 'sekil') and item.sekil:
                # Xüsusi simvolları təmizləyək
                clean_title = re.sub(r'[^\w\s]', ' ', str(item.adi)).strip()
                clean_caption = f"{clean_title} - {item.brend.adi} - {item.id} - {re.sub(r'[^\w\s-]', '-', str(item.oem))}"
                
                url_info['images'] = [{
                    'loc': f"{protocol}://{domain}{item.sekil.url}",
                    'title': clean_title,
                    'caption': clean_caption
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