from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from mehsullar.models import Mehsul, Marka, Kateqoriya, Brend, Sifaris, MusteriReyi
from rentacar.models import Car
from django.contrib.auth.models import User
from django.utils import timezone

class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return [
            'anaevim',  # Ana səhifə
            'esasevim:main',  # Əsas səhifə
            'about',  # Haqqımızda
            'login',  # Giriş
            'register',  # Qeydiyyat
            'profile',  # Profil
            'products_list',  # Məhsullar
            'view_cart',  # Səbət
            'sifaris_izle',  # Sifarişlər
            'hesabatlar',  # Hesabatlar
            'umumi_baxis',  # Ümumi baxış
            'car_list',  # Avtomobillər
        ]

    def location(self, item):
        return reverse(item)

class MehsulSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Mehsul.objects.all()

    def lastmod(self, obj):
        return obj.yaradilma_tarixi if hasattr(obj, 'yaradilma_tarixi') else timezone.now()

    def location(self, obj):
        return reverse('mehsul_haqqinda', kwargs={
            'mehsul_adi': obj.adi,
            'mehsul_oem': obj.oem,
            'mehsul_brend_kod': obj.brend_kod,
            'mehsul_id': obj.id
        })

class MarkaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Marka.objects.all()

    def location(self, obj):
        return f'/marka/{obj.adi}/'

class KateqoriyaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Kateqoriya.objects.all()

    def location(self, obj):
        return f'/kateqoriya/{obj.adi}/'

class BrendSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Brend.objects.all()

    def location(self, obj):
        return f'/brend/{obj.adi}/'

class CarSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Car.objects.all()

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('car_detail', kwargs={'pk': obj.id})

class SifarisSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Sifaris.objects.all()

    def lastmod(self, obj):
        return obj.tarix

    def location(self, obj):
        return reverse('sifaris_detallari', kwargs={'sifaris_id': obj.id})

class MusteriReyiSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return MusteriReyi.objects.filter(tesdiq=True)

    def lastmod(self, obj):
        return obj.tarix

    def location(self, obj):
        return reverse('esasevim:main') + '#reyler'

class UserProfileSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return User.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.date_joined

    def location(self, obj):
        return reverse('profile')

class SearchSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return [
            'products_list',  # Məhsul axtarışı
            'car_list',      # Avtomobil axtarışı
        ]

    def location(self, item):
        return reverse(item)

class ListingSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return [
            'products_list',      # Məhsul siyahısı
            'umumi_baxis',        # Ümumi baxış
            'sifaris_izle',       # Sifariş siyahısı
            'hesabatlar',         # Hesabatlar
            'view_cart',          # Səbət
        ]

    def location(self, item):
        return reverse(item)

# Bütün sitemapləri bir dictionary-də birləşdiririk
sitemaps = {
    'static': StaticViewSitemap,
    'mehsullar': MehsulSitemap,
    'markalar': MarkaSitemap,
    'kateqoriyalar': KateqoriyaSitemap,
    'brendler': BrendSitemap,
    'cars': CarSitemap,
    'sifarisler': SifarisSitemap,
    'reyler': MusteriReyiSitemap,
    'profiller': UserProfileSitemap,
    'search': SearchSitemap,
    'listings': ListingSitemap,
} 