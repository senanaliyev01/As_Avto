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
    # '+' simvollarını ilk xüsusi olaraq təmizləyək ki, XML-də problem yaranmasın
    text = text.replace('+', ' plus ')
    # Digər təhlükəli simvolları təmizləyirik
    text = text.replace('&', ' and ')
    # HTML xüsusi simvollarını təmizləyirik
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
        # OEM və brend kodlarında '+' və '.' simvollarını əvəz edək
        oem_clean = obj.oem.replace('+', 'plus').replace('.', 'dot') if obj.oem else ""
        brend_kod_clean = obj.brend_kod.replace('+', 'plus').replace('.', 'dot') if obj.brend_kod else ""
        
        slug_oem = clean_url(oem_clean)
        slug_brand_code = clean_url(brend_kod_clean)
        
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
                    # Təsvir mətnləri təmizləyirik - xüsusi simvolları əvəz edirik
                    title = clean_description(item.adi)
                    
                    # OEM və brend kodlarındakı xüsusi simvolları təmizləyərək caption yaradırıq
                    brend_kod = item.brend_kod.replace('+', ' plus ').replace('.', ' dot ') if item.brend_kod else ""
                    oem = item.oem.replace('+', ' plus ').replace('.', ' dot ') if item.oem else ""
                    
                    caption = clean_description(f"{item.adi} - {item.brend.adi} - {brend_kod} - {oem}")
                    
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