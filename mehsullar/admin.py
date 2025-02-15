from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi,MarkaSekil
from django.urls import reverse
from django.utils.html import format_html

class MarkaSekilInline(admin.TabularInline):
    model = MarkaSekil
    extra = 1  # Yeni şəkil əlavə etmək üçün bir boş forma

@admin.register(Marka)
class MarkaAdmin(admin.ModelAdmin):
    inlines = [MarkaSekilInline]
    list_display = ('adi',)

# Sifarişlərdə məhsul detalını əlavə etmək üçün
class SifarisMehsulInline(admin.TabularInline):
    model = SifarisMehsul
    extra = 0

# OEMKodInline klassını əvvəldə təyin edirik
class OEMKodInline(admin.TabularInline):
    model = OEMKod
    extra = 1

# Sifariş admin paneli
@admin.register(Sifaris)
class SifarisAdmin(admin.ModelAdmin):
    inlines = [SifarisMehsulInline]
    list_display = ('id', 'user', 'tarix', 'cemi_mebleg', 'odenilen_mebleg', 'borc', 'status', 'tamamlandi', 'pdf_link')
    search_fields = ('id', 'user__username', 'status')
    list_filter = ('status', 'tamamlandi')
    fields = ('user', 'cemi_mebleg', 'odenilen_mebleg', 'status', 'tamamlandi')
    readonly_fields = ('borc',)

    def pdf_link(self, obj):
        return format_html('<a href="{}" target="_blank">PDF-yə Çevir</a>', reverse('sifaris_detallari', args=[obj.id]) + '?pdf=1')
    pdf_link.short_description = 'PDF-yə Çevir'

# Sifariş məhsulları admin paneli
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'get_mehsul_adi', 'get_brend_adi', 'get_brend_kod', 'get_oem', 'miqdar', 'qiymet', 'get_total')
    list_filter = ('sifaris', 'mehsul__brend')
    search_fields = ('mehsul__adi', 'mehsul__brend_kod', 'mehsul__oem')

    def get_mehsul_adi(self, obj):
        return obj.mehsul.adi
    get_mehsul_adi.short_description = 'Məhsul Adı'
    get_mehsul_adi.admin_order_field = 'mehsul__adi'

    def get_brend_adi(self, obj):
        return obj.mehsul.brend.adi
    get_brend_adi.short_description = 'Firma'
    get_brend_adi.admin_order_field = 'mehsul__brend__adi'

    def get_brend_kod(self, obj):
        return obj.mehsul.brend_kod
    get_brend_kod.short_description = 'Brend Kodu'
    get_brend_kod.admin_order_field = 'mehsul__brend_kod'

    def get_oem(self, obj):
        return obj.mehsul.oem
    get_oem.short_description = 'OEM'
    get_oem.admin_order_field = 'mehsul__oem'

    def get_total(self, obj):
        return f"{obj.miqdar * obj.qiymet} AZN"
    get_total.short_description = 'Cəmi'

# Məhsul admin paneli
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet', 'brend_kod', 'oem', 'stok')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    inlines = [OEMKodInline]

# Qeydiyyatları düzəltdik
admin.site.register(SifarisMehsul, SifarisMehsulAdmin)
admin.site.register(Kateqoriya)
admin.site.register(Brend)
admin.site.register(Sebet)
admin.site.register(Mehsul, MehsulAdmin)

@admin.register(MusteriReyi)
class MusteriReyiAdmin(admin.ModelAdmin):
    list_display = ['musteri', 'qiymetlendirme', 'tarix', 'tesdiq']
    list_filter = ['tesdiq', 'qiymetlendirme']
    search_fields = ['musteri__username', 'rey']
    actions = ['tesdiqle', 'tesdiq_legv_et']

    def tesdiqle(self, request, queryset):
        queryset.update(tesdiq=True)
    tesdiqle.short_description = "Seçilmiş rəyləri təsdiqlə"

    def tesdiq_legv_et(self, request, queryset):
        queryset.update(tesdiq=False)
    tesdiq_legv_et.short_description = "Seçilmiş rəylərin təsdiqini ləğv et"
