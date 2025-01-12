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
    list_display = ('sifaris', 'mehsul', 'miqdar', 'qiymet')
    
    def qiymet(self, obj):
        return f"{obj.qiymet} EUR"
    qiymet.short_description = 'Qiymət (EUR)'

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

# Kateqoriya admin paneli
class KateqoriyaAdmin(admin.ModelAdmin):
    list_display = ('adi',)
    search_fields = ('adi',)

# Brend admin paneli
class BrendAdmin(admin.ModelAdmin):
    list_display = ('adi',)
    search_fields = ('adi',)

# Marka admin paneli
class MarkaAdmin(admin.ModelAdmin):
    list_display = ('adi',)
    search_fields = ('adi',)

# Səbət admin paneli
class SebetAdmin(admin.ModelAdmin):
    list_display = ('user', 'mehsul', 'miqdar')
    list_filter = ('user',)
    search_fields = ('user__username', 'mehsul__adi')

# Qeydiyyatları yeniləyirik
admin.site.register(SifarisMehsul, SifarisMehsulAdmin)
admin.site.register(Kateqoriya, KateqoriyaAdmin)
admin.site.register(Brend, BrendAdmin)
admin.site.register(Marka, MarkaAdmin)
admin.site.register(Sebet, SebetAdmin)
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