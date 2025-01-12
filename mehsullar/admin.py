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
    list_display = ('id', 'user', 'tarix', 'cemi_mebleg_eur_display', 'cemi_mebleg_azn_display', 
                   'odenilen_mebleg_eur_display', 'odenilen_mebleg_azn_display', 
                   'qaliq_borc_eur_display', 'qaliq_borc_azn_display', 'status', 'tamamlandi')
    search_fields = ('id', 'user__username', 'status')
    list_filter = ('status', 'tamamlandi')
    fields = ('user', 'cemi_mebleg_eur', 'odenilen_mebleg_eur', 'status', 'tamamlandi')

    def cemi_mebleg_eur_display(self, obj):
        return f"{obj.cemi_mebleg_eur} EUR"
    cemi_mebleg_eur_display.short_description = 'Cəmi Məbləğ (EUR)'

    def cemi_mebleg_azn_display(self, obj):
        return f"{obj.cemi_mebleg_azn} AZN"
    cemi_mebleg_azn_display.short_description = 'Cəmi Məbləğ (AZN)'

    def odenilen_mebleg_eur_display(self, obj):
        return f"{obj.odenilen_mebleg_eur} EUR"
    odenilen_mebleg_eur_display.short_description = 'Ödənilən Məbləğ (EUR)'

    def odenilen_mebleg_azn_display(self, obj):
        return f"{obj.odenilen_mebleg_azn} AZN"
    odenilen_mebleg_azn_display.short_description = 'Ödənilən Məbləğ (AZN)'

    def qaliq_borc_eur_display(self, obj):
        return f"{obj.qaliq_borc_eur} EUR"
    qaliq_borc_eur_display.short_description = 'Qalıq Borc (EUR)'

    def qaliq_borc_azn_display(self, obj):
        return f"{obj.qaliq_borc_azn} AZN"
    qaliq_borc_azn_display.short_description = 'Qalıq Borc (AZN)'

# Sifariş məhsulları admin paneli
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'mehsul', 'miqdar', 'qiymet_display')
    
    def qiymet_display(self, obj):
        return f"{obj.qiymet} EUR"
    qiymet_display.short_description = 'Qiymət (EUR)'

# Məhsul admin paneli
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet_eur_display', 'qiymet_azn_display', 'brend_kod', 'oem', 'stok')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    list_filter = ('kateqoriya', 'brend', 'marka')
    inlines = [OEMKodInline]

    def qiymet_eur_display(self, obj):
        return f"{obj.qiymet_eur} EUR"
    qiymet_eur_display.short_description = 'Qiymət (EUR)'

    def qiymet_azn_display(self, obj):
        return f"{obj.qiymet_azn} AZN"
    qiymet_azn_display.short_description = 'Qiymət (AZN)'

# Digər admin qeydiyyatları
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
