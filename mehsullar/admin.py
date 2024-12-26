from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul

# Sifarişlərdə məhsul detalını əlavə etmək üçün
class SifarisMehsulInline(admin.TabularInline):
    model = SifarisMehsul
    extra = 0

# Sifariş admin paneli
@admin.register(Sifaris)
class SifarisAdmin(admin.ModelAdmin):
    inlines = [SifarisMehsulInline]
    list_display = ('id', 'user', 'tarix', 'cemi_mebleg', 'odenilen_mebleg', 'borc', 'status', 'tamamlandi')
    search_fields = ('id', 'user__username', 'status')  # Axtarış sahələri
    list_filter = ('status', 'tamamlandi')
    fields = ('user', 'cemi_mebleg', 'odenilen_mebleg', 'status', 'tamamlandi')  # Redaktə edilə bilən sahələr
    readonly_fields = ('borc',)  # Borc avtomatik hesablanır, redaktə edilə bilməz

# Sifariş məhsulları admin paneli
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'mehsul', 'miqdar', 'qiymet')

# Məhsul admin paneli
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet', 'brend_kod', 'oem_kod')  # Siyahıya brend və OEM kodları əlavə etdik
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem_kod')  # Axtarış üçün uyğun sahələr

# Qeydiyyatları düzəltdik
admin.site.register(SifarisMehsul, SifarisMehsulAdmin)
admin.site.register(Kateqoriya)
admin.site.register(Brend)
admin.site.register(Marka)
admin.site.register(Sebet)
admin.site.register(Mehsul, MehsulAdmin)
