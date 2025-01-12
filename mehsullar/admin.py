from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi

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
    list_display = ('id', 'user', 'tarix', 'cemi_mebleg', 'odenilen_mebleg', 'borc', 'status', 'tamamlandi')
    search_fields = ('id', 'user__username', 'status')
    list_filter = ('status', 'tamamlandi')
    fields = ('user', 'cemi_mebleg', 'odenilen_mebleg', 'status', 'tamamlandi')
    readonly_fields = ('borc',)

# Sifariş məhsulları admin paneli
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'mehsul', 'miqdar', 'qiymet_eur')

# Məhsul admin paneli
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet_eur', 'brend_kod', 'oem', 'stok')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    inlines = [OEMKodInline]

# Qeydiyyatları düzəltdik
admin.site.register(SifarisMehsul, SifarisMehsulAdmin)
admin.site.register(Kateqoriya)
admin.site.register(Brend)
admin.site.register(Marka)
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
