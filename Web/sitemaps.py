from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul
from django.utils import timezone
from django.utils.text import slugify
from urllib.parse import quote

class StaticViewSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return ['anaevim']

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return timezone.now()

class MehsulSitemap(Sitemap):
    changefreq = "always"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, mehsul):
        return timezone.now()

    def location(self, mehsul):
        return reverse('mehsul_etrafli', kwargs={
            'mehsul_adi': slugify(mehsul.adi),
            'mehsul_oem': slugify(mehsul.oem),
            'mehsul_brend_kod': slugify(mehsul.brend_kod),
            'mehsul_id': mehsul.id
        })

    def _urls(self, page, protocol, domain):
        urls = []
        for item in self.paginator.page(page).object_list:
            loc = f"{protocol}://{domain}{self.location(item)}"
            priority = self.priority
            changefreq = self.changefreq
            lastmod = self.lastmod(item) if self.lastmod is not None else None

            url_info = {
                'item': item,
                'location': loc,
                'lastmod': lastmod,
                'changefreq': changefreq,
                'priority': priority,
            }

            if item.sekil:
                url_info['images'] = [{
                    'loc': f"{protocol}://{domain}{item.sekil.url}",
                    'title': item.adi,
                    'caption': f"{item.adi} - {item.brend.adi} - {item.oem} - {item.brend_kod}"
                }]

            urls.append(url_info)
        return urls

sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
} 