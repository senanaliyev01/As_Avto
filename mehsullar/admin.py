from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi, MarkaSekil, Model, Avtomodel, Motor, Il, Yanacaq
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.db import models

class MarkaSekilInline(admin.TabularInline):
    model = MarkaSekil
    extra = 1

@admin.register(Marka)
class MarkaAdmin(admin.ModelAdmin):
    inlines = [MarkaSekilInline]
    list_display = ('adi',)
    search_fields = ('adi',)
    ordering = ('adi',)

@admin.register(Kateqoriya)
class KateqoriyaAdmin(admin.ModelAdmin):
    list_display = ('adi',)
    search_fields = ('adi',)
    ordering = ('adi',)

@admin.register(Brend)
class BrendAdmin(admin.ModelAdmin):
    list_display = ('adi', 'get_sekil')
    search_fields = ('adi',)
    ordering = ('adi',)

    def get_sekil(self, obj):
        if obj.sekil:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.sekil.url)
        return "-"
    get_sekil.short_description = 'Logo'

@admin.register(Avtomodel)
class AvtomodelAdmin(admin.ModelAdmin):
    list_display = ('adi',)
    search_fields = ('adi',)
    ordering = ('adi',)

@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    list_display = ('motor',)
    search_fields = ('motor',)
    ordering = ('motor',)

@admin.register(Il)
class IlAdmin(admin.ModelAdmin):
    list_display = ('il',)
    search_fields = ('il',)
    ordering = ('il',)

@admin.register(Yanacaq)
class YanacaqAdmin(admin.ModelAdmin):
    list_display = ('yanacaq',)
    search_fields = ('yanacaq',)
    ordering = ('yanacaq',)

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('avtomobil', 'model', 'motor', 'yanacaq', 'il')
    list_filter = ('avtomobil', 'model', 'motor', 'yanacaq', 'il')
    search_fields = ('avtomobil__adi', 'model__adi', 'motor__motor', 'yanacaq__yanacaq', 'il__il')
    ordering = ('avtomobil', 'model', 'motor', 'yanacaq', 'il')

class OEMKodInline(admin.TabularInline):
    model = OEMKod
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(
            attrs={'rows': 5, 'style': 'width: 100%; font-family: monospace;'})},
    }

@admin.register(Mehsul)
class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'qiymet', 'brend_kod', 'oem', 'stok', 'get_yenidir')
    list_filter = ('kateqoriya', 'brend', 'marka', 'yenidir')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    inlines = [OEMKodInline]
    actions = ['yenilikden_sil', 'yenidir_et']
    list_per_page = 25

    def get_yenidir(self, obj):
        if obj.yenidir:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    get_yenidir.short_description = 'Yenidir'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.attrs.update({
            'style': 'width: 500px; height: 300px; overflow-y: auto;'
        })
        form.base_fields['model'].widget.can_add_related = True
        return form

    def yenilikden_sil(self, request, queryset):
        queryset.update(yenidir=False)
        self.message_user(request, "Seçilmiş məhsullar yenilikdən silindi.")
    yenilikden_sil.short_description = "Seçilmiş məhsulları yenilikdən sil"

    def yenidir_et(self, request, queryset):
        queryset.update(yenidir=True)
        self.message_user(request, "Seçilmiş məhsullar yenidir olaraq işarələndi.")
    yenidir_et.short_description = "Seçilmiş məhsulları yenidir et"

@admin.register(Sebet)
class SebetAdmin(admin.ModelAdmin):
    list_display = ('user', 'mehsul', 'miqdar')
    list_filter = ('user', 'mehsul__kateqoriya', 'mehsul__brend')
    search_fields = ('user__username', 'mehsul__adi', 'mehsul__brend_kod')
    ordering = ('-id',)

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
        if obj.id:
            return format_html('<span style="color: #008000; font-weight: bold;">{} AZN</span>', 
                             obj.miqdar * obj.qiymet)
        return '-'
    get_total.short_description = 'Cəmi'

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if obj:
            fields.extend(['get_brend_adi', 'get_brend_kod', 'get_oem', 'get_total'])
        return fields

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
    list_per_page = 25

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
            'gozleyir': 'background: #FFA500;',
            'hazirlanir': 'background: #FFD700;',
            'yoldadir': 'background: #87CEEB;',
            'catdirildi': 'background: #90EE90;'
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

@admin.register(SifarisMehsul)
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'get_mehsul_adi', 'get_brend_adi', 'get_brend_kod', 'get_oem', 'miqdar', 'qiymet', 'get_total')
    list_filter = ('sifaris', 'mehsul__brend')
    search_fields = ('mehsul__adi', 'mehsul__brend_kod', 'mehsul__oem')
    ordering = ('-id',)
    list_per_page = 25

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

@admin.register(MusteriReyi)
class MusteriReyiAdmin(admin.ModelAdmin):
    list_display = ['musteri', 'get_qiymetlendirme', 'get_tarix', 'get_tesdiq']
    list_filter = ['tesdiq', 'qiymetlendirme']
    search_fields = ['musteri__username', 'rey']
    actions = ['tesdiqle', 'tesdiq_legv_et']
    ordering = ('-tarix',)
    list_per_page = 25

    def get_qiymetlendirme(self, obj):
        stars = '★' * obj.qiymetlendirme + '☆' * (5 - obj.qiymetlendirme)
        return format_html('<span style="color: gold;">{}</span>', stars)
    get_qiymetlendirme.short_description = 'Qiymətləndirmə'

    def get_tarix(self, obj):
        return obj.tarix.astimezone(timezone.get_current_timezone()).strftime('%d-%m-%Y %H:%M')
    get_tarix.short_description = 'Tarix'

    def get_tesdiq(self, obj):
        if obj.tesdiq:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    get_tesdiq.short_description = 'Təsdiq'

    def tesdiqle(self, request, queryset):
        queryset.update(tesdiq=True)
        self.message_user(request, "Seçilmiş rəylər təsdiqləndi.")
    tesdiqle.short_description = "Seçilmiş rəyləri təsdiqlə"

    def tesdiq_legv_et(self, request, queryset):
        queryset.update(tesdiq=False)
        self.message_user(request, "Seçilmiş rəylərin təsdiqi ləğv edildi.")
    tesdiq_legv_et.short_description = "Seçilmiş rəylərin təsdiqini ləğv et"
