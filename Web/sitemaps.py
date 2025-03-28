from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote
import re
import html

# Xüsusi simvolları emal edən funksiya
def clean_url(text):
    if not text:
        return ""
    # İlk addım - slugify
    cleaned = slugify(text)
    # Əgər slugify bütün xüsusi simvolları emal etməyibsə, bunu özümüz edirik
    if not cleaned or cleaned == "-":
        # Bütün xüsusi simvolları '-' ilə əvəz edirik
        cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', text)
        # Əvvəldəki və sondakı '-' işarələrini təmizləyirik
        cleaned = cleaned.strip('-')
        # Boş sətir yaranmaması üçün yoxlayırıq
        if not cleaned:
            cleaned = "item"
    return cleaned

# Təsvir mətnləri üçün funksiya
def clean_description(text):
    if not text:
        return ""
    # HTML xüsusi simvollarını təmizləyirik (ampersand, quotes və s.)
    cleaned = html.escape(text)
    return cleaned

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
        # Təhlükəsiz URL üçün clean_url funksiyasını istifadə edirik
        slug_name = clean_url(obj.adi)
        slug_oem = clean_url(obj.oem)
        slug_brand_code = clean_url(obj.brend_kod)
        
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
            try:
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
                    # Təsvir mətnləri təmizləyirik
                    title = clean_description(item.adi)
                    caption = clean_description(f"{item.adi} - {item.brend.adi} - {item.brend_kod} - {item.oem}")
                    
                    url_info['images'] = [{
                        'loc': f"{protocol}://{domain}{item.sekil.url}",
                        'title': title,
                        'caption': caption
                    }]

                urls.append(url_info)
            except Exception as e:
                # Xəta baş verərsə, bu məhsulu keçirik və davam edirik
                continue

        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls

# Yalnız anaevim app üçün sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 