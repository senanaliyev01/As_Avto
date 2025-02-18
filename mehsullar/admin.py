from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi, MarkaSekil
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone

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
    fields = ('mehsul', 'miqdar', 'qiymet')
    readonly_fields = ('get_brend_adi', 'get_brend_kod', 'get_oem', 'get_total')
    
    def get_brend_adi(self, obj):
        return format_html('<span style="color: #1a73e8;">{}</span>', obj.mehsul.brend.adi)
    get_brend_adi.short_description = 'Firma'

    def get_brend_kod(self, obj):
        return format_html('<span style="font-family: monospace;">{}</span>', obj.mehsul.brend_kod)
    get_brend_kod.short_description = 'Brend Kodu'

    def get_oem(self, obj):
        return format_html('<span style="font-family: monospace;">{}</span>', obj.mehsul.oem)
    get_oem.short_description = 'OEM'

    def get_total(self, obj):
        if obj.id:  # Yalnız mövcud obyektlər üçün
            return format_html('<span style="color: #008000; font-weight: bold;">{} AZN</span>', 
                             obj.miqdar * obj.qiymet)
        return '-'
    get_total.short_description = 'Cəmi'

    # Əlavə sütunları göstərmək üçün
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj:  # Mövcud sifariş üçün
            fields.extend(['get_brend_adi', 'get_brend_kod', 'get_oem', 'get_total'])
        return fields

# OEMKodInline klassını əvvəldə təyin edirik
class OEMKodInline(admin.TabularInline):
    model = OEMKod
    extra = 1
    verbose_name = 'Əlavə OEM Kodu'
    verbose_name_plural = 'Əlavə OEM Kodları'

# Sifariş admin paneli
@admin.register(Sifaris)
class SifarisAdmin(admin.ModelAdmin):
    inlines = [SifarisMehsulInline]
    list_display = (
        'id', 
        'get_musteri', 
        'get_tarix', 
        'get_cemi_mebleg', 
        'get_odenilen_mebleg', 
        'get_borc', 
        'get_status', 
        'get_tamamlanma',
        'pdf_link'
    )
    search_fields = ('id', 'user__username', 'status')
    list_filter = ('status', 'tamamlandi')
    fields = ('user', 'cemi_mebleg', 'odenilen_mebleg', 'status', 'tamamlandi')
    readonly_fields = ('borc',)

    def get_musteri(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user.first_name else obj.user.username
    get_musteri.short_description = 'Müştəri'
    get_musteri.admin_order_field = 'user__username'

    def get_tarix(self, obj):
        return obj.tarix.astimezone(timezone.get_current_timezone()).strftime('%d-%m-%Y %H:%M')
    get_tarix.short_description = 'Tarix'
    get_tarix.admin_order_field = 'tarix'

    def get_cemi_mebleg(self, obj):
        return f"{obj.cemi_mebleg} AZN"
    get_cemi_mebleg.short_description = 'Ümumi Məbləğ'
    get_cemi_mebleg.admin_order_field = 'cemi_mebleg'

    def get_odenilen_mebleg(self, obj):
        return f"{obj.odenilen_mebleg} AZN"
    get_odenilen_mebleg.short_description = 'Ödənilən'
    get_odenilen_mebleg.admin_order_field = 'odenilen_mebleg'

    def get_borc(self, obj):
        return f"{obj.borc()} AZN"
    get_borc.short_description = 'Qalıq Borc'

    def get_status(self, obj):
        status_classes = {
            'gozleyir': 'background: #FFA500;',  # Narıncı
            'hazirlanir': 'background: #FFD700;', # Sarı
            'yoldadir': 'background: #87CEEB;',   # Mavi
            'catdirildi': 'background: #90EE90;'  # Yaşıl
        }
        status_text = {
            'gozleyir': 'Gözləyir',
            'hazirlanir': 'Hazırlanır',
            'yoldadir': 'Yoldadır',
            'catdirildi': 'Çatdırıldı'
        }
        style = status_classes.get(obj.status, '')
        text = status_text.get(obj.status, obj.status)
        return format_html('<span style="padding: 5px 10px; border-radius: 4px; color: black; {}">{}</span>', style, text)
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'status'

    def get_tamamlanma(self, obj):
        if obj.tamamlandi:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    get_tamamlanma.short_description = 'Tamamlandı'
    get_tamamlanma.admin_order_field = 'tamamlandi'

    def pdf_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="background-color: #4CAF50; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px;">PDF-yə Çevir</a>', 
            reverse('sifaris_detallari', args=[obj.id]) + '?pdf=1'
        )
    pdf_link.short_description = 'PDF'

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
@admin.register(Mehsul)
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet', 'brend_kod', 'get_all_oem_codes', 'stok')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    list_filter = ('kateqoriya', 'brend', 'marka')
    inlines = [OEMKodInline]
    
    def get_all_oem_codes(self, obj):
        # Əsas OEM kodunu və əlavə OEM kodlarını birləşdiririk
        all_codes = [obj.oem] + [oem.kod for oem in obj.oem_kodlar.all()]
        return ' | '.join(all_codes)
    get_all_oem_codes.short_description = 'OEM Kodları'

    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet', 'stok')
        }),
        ('Kodlar', {
            'fields': ('brend_kod', 'oem'),
            'description': 'Əsas OEM kodunu buraya yazın. Əlavə OEM kodlarını aşağıdakı bölmədən əlavə edə bilərsiniz.'
        }),
        ('Əlavə Məlumatlar', {
            'fields': ('sekil', 'haqqinda'),
            'classes': ('collapse',)
        }),
    )

# Qeydiyyatları düzəltdik
admin.site.register(SifarisMehsul, SifarisMehsulAdmin)
admin.site.register(Kateqoriya)
admin.site.register(Brend)
admin.site.register(Sebet)

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
