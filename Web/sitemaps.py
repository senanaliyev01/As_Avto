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
        # İkiqat encoding problemini həll etmək üçün ilk öncə mətn parçalarındakı
        # mövcud encode edilmiş hissələri decode edirik
        name = obj.adi or ''
        oem = obj.oem or ''
        brand_code = obj.brend_kod or ''
        
        # sonra təmiz qiymətləri bir dəfə düzgün encode edirik
        encoded_name = quote(name)
        encoded_oem = quote(oem)
        encoded_brand_code = quote(brand_code)
        
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': encoded_name,
            'mehsul_oem': encoded_oem,
            'mehsul_brend_kod': encoded_brand_code,
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

            # Şəkil məlumatlarını əlavə edirik
            # Həmişə eyni "noimage.webp" əvəzinə məhsula xas bir şəkil url-i yaradaq
            # Əgər gerçək şəkil yoxdursa, məhsul ID-si ilə unikal bir şəkil adı yaradaq
            url_info['images'] = [{
                # Əgər default "noimage.webp" istifadə olunursa, bu halda məhsul ID-li versiya yaradırıq
                'loc': f"{protocol}://{domain}{item.sekil.url if item.sekil and 'noimage.webp' not in item.sekil.url else f'/media/mehsul_sekilleri/product_{item.id}.webp'}",
                'title': item.adi if item.adi else f"Məhsul {item.id}",
                'caption': f"{item.adi or 'Məhsul'} - {item.brend.adi if item.brend else ''} - {item.id} - {item.brend_kod or ''} - {item.oem or ''}"
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