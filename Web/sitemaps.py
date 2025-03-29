from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote

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

            # XML-safe clean strings for location and other attrs
            loc = str(loc).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')

            url_info = {
                'item': item,
                'location': loc,
                'lastmod': lastmod,
                'changefreq': self._get('changefreq', item),
                'priority': str(priority if priority is not None else ''),
                'is_sitemap_item': True  # sitemap öğesi olduğunu belirtmek için
            }

            # Şəkil məlumatlarını əlavə edirik - güvenli string formatlamalarla
            if hasattr(item, 'sekil') and item.sekil:
                img_loc = f"{protocol}://{domain}{item.sekil.url}"
                img_loc = str(img_loc).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                
                title = str(item.adi).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                caption = f"{title} - {item.brend.adi} - {item.brend_kod} - {item.oem}"
                caption = caption.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                
                url_info['images'] = [{
                    'loc': img_loc,
                    'title': title,
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