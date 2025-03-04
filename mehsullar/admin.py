from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi, MarkaSekil, Model, Avtomodel, Motor, Il, Yanacaq
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION

# Admin panel üçün xüsusi CSS
class CustomAdminSite(AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context['custom_css'] = """
            <style>
                /* Ümumi stillər */
                #header {
                    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
                    color: white;
                }
                
                .module h2, .module caption, .inline-group h2 {
                    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
                    color: white;
                }
                
                /* Cədvəl stilləri */
                #result_list th {
                    background: #f5f5f5;
                    color: #1a237e;
                    font-weight: bold;
                }
                
                #result_list tr:hover {
                    background-color: #f8f9fa;
                }
                
                /* Düymə stilləri */
                .button, input[type=submit], input[type=button], .submit-row input, a.button {
                    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 15px;
                    transition: all 0.3s ease;
                }
                
                .button:hover, input[type=submit]:hover, input[type=button]:hover, .submit-row input:hover, a.button:hover {
                    background: linear-gradient(135deg, #0d47a1 0%, #1a237e 100%);
                    transform: translateY(-1px);
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                
                /* Status göstəriciləri */
                .status-badge {
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 0.85em;
                    letter-spacing: 0.5px;
                }
                
                /* Qiymət göstəriciləri */
                .price-badge {
                    background: #e8f5e9;
                    color: #2e7d32;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                /* Stok göstəricisi */
                .stock-badge {
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                .stock-low {
                    background: #ffebee;
                    color: #c62828;
                }
                
                .stock-medium {
                    background: #fff3e0;
                    color: #ef6c00;
                }
                
                .stock-high {
                    background: #e8f5e9;
                    color: #2e7d32;
                }
                
                /* Rəy ulduzları */
                .rating-stars {
                    color: #ffd700;
                    text-shadow: 0 0 2px rgba(0,0,0,0.2);
                }
                
                /* PDF düyməsi */
                .pdf-button {
                    background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
                    color: white;
                    padding: 8px 15px;
                    border-radius: 4px;
                    text-decoration: none;
                    transition: all 0.3s ease;
                }
                
                .pdf-button:hover {
                    background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
                    transform: translateY(-1px);
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                
                /* Form elementləri */
                input[type=text], input[type=password], input[type=email], input[type=number], textarea, select {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 8px;
                    transition: all 0.3s ease;
                }
                
                input[type=text]:focus, input[type=password]:focus, input[type=email]:focus, input[type=number]:focus, textarea:focus, select:focus {
                    border-color: #1a237e;
                    box-shadow: 0 0 5px rgba(26,35,126,0.2);
                }
                
                /* Pagination */
                .pagination {
                    margin: 20px 0;
                }
                
                .pagination a, .pagination span {
                    padding: 8px 12px;
                    margin: 0 4px;
                    border-radius: 4px;
                    background: #f5f5f5;
                    color: #1a237e;
                    text-decoration: none;
                    transition: all 0.3s ease;
                }
                
                .pagination a:hover {
                    background: #1a237e;
                    color: white;
                }
                
                .pagination .current {
                    background: #1a237e;
                    color: white;
                }
            </style>
        """
        return context

admin_site = CustomAdminSite(name='admin')

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
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.sekil.url)
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
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'get_qiymet', 'brend_kod', 'oem', 'get_stok', 'get_yenidir')
    list_filter = ('kateqoriya', 'brend', 'marka', 'yenidir')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem')
    inlines = [OEMKodInline]
    actions = ['yenilikden_sil', 'yenidir_et']
    list_per_page = 25

    def get_qiymet(self, obj):
        return format_html('<span class="price-badge">{} AZN</span>', obj.qiymet)
    get_qiymet.short_description = 'Qiymət'

    def get_stok(self, obj):
        if obj.stok < 10:
            return format_html('<span class="stock-badge stock-low">{} ədəd</span>', obj.stok)
        elif obj.stok < 50:
            return format_html('<span class="stock-badge stock-medium">{} ədəd</span>', obj.stok)
        else:
            return format_html('<span class="stock-badge stock-high">{} ədəd</span>', obj.stok)
    get_stok.short_description = 'Stok'

    def get_yenidir(self, obj):
        if obj.yenidir:
            return format_html('<span style="color: #2e7d32; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #c62828; font-weight: bold;">✗</span>')
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
        return format_html('<span style="color: #1a237e; font-weight: bold;">{}</span>', obj.mehsul.brend.adi)
    get_brend_adi.short_description = 'Firma'

    def get_brend_kod(self, obj):
        return format_html('<span style="font-family: monospace; background: #f5f5f5; padding: 2px 5px; border-radius: 3px;">{}</span>', obj.mehsul.brend_kod)
    get_brend_kod.short_description = 'Brend Kodu'

    def get_oem(self, obj):
        return format_html('<span style="font-family: monospace; background: #f5f5f5; padding: 2px 5px; border-radius: 3px;">{}</span>', obj.mehsul.oem)
    get_oem.short_description = 'OEM'

    def get_total(self, obj):
        if obj.id:
            return format_html('<span class="price-badge">{} AZN</span>', obj.miqdar * obj.qiymet)
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
        return format_html('<span class="price-badge">{} AZN</span>', obj.cemi_mebleg)
    get_cemi_mebleg.short_description = 'Ümumi Məbləğ'
    get_cemi_mebleg.admin_order_field = 'cemi_mebleg'

    def get_odenilen_mebleg(self, obj):
        return format_html('<span class="price-badge">{} AZN</span>', obj.odenilen_mebleg)
    get_odenilen_mebleg.short_description = 'Ödənilən'
    get_odenilen_mebleg.admin_order_field = 'odenilen_mebleg'

    def get_borc(self, obj):
        if obj.borc() > 0:
            return format_html('<span class="stock-badge stock-low">{} AZN</span>', obj.borc())
        return format_html('<span class="stock-badge stock-high">{} AZN</span>', obj.borc())
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
        return format_html('<span class="status-badge" style="{}">{}</span>', style, text)
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'status'

    def get_tamamlanma(self, obj):
        if obj.tamamlandi:
            return format_html('<span style="color: #2e7d32; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #c62828; font-weight: bold;">✗</span>')
    get_tamamlanma.short_description = 'Tamamlandı'
    get_tamamlanma.admin_order_field = 'tamamlandi'

    def pdf_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" class="pdf-button">PDF-yə Çevir</a>', 
            reverse('sifaris_detallari', args=[obj.id]) + '?pdf=1'
        )
    pdf_link.short_description = 'PDF'

@admin.register(SifarisMehsul)
class SifarisMehsulAdmin(admin.ModelAdmin):
    list_display = ('sifaris', 'get_mehsul_adi', 'get_brend_adi', 'get_brend_kod', 'get_oem', 'miqdar', 'get_qiymet', 'get_total')
    list_filter = ('sifaris', 'mehsul__brend')
    search_fields = ('mehsul__adi', 'mehsul__brend_kod', 'mehsul__oem')
    ordering = ('-id',)
    list_per_page = 25

    def get_mehsul_adi(self, obj):
        return obj.mehsul.adi
    get_mehsul_adi.short_description = 'Məhsul Adı'
    get_mehsul_adi.admin_order_field = 'mehsul__adi'

    def get_brend_adi(self, obj):
        return format_html('<span style="color: #1a237e; font-weight: bold;">{}</span>', obj.mehsul.brend.adi)
    get_brend_adi.short_description = 'Firma'
    get_brend_adi.admin_order_field = 'mehsul__brend__adi'

    def get_brend_kod(self, obj):
        return format_html('<span style="font-family: monospace; background: #f5f5f5; padding: 2px 5px; border-radius: 3px;">{}</span>', obj.mehsul.brend_kod)
    get_brend_kod.short_description = 'Brend Kodu'
    get_brend_kod.admin_order_field = 'mehsul__brend_kod'

    def get_oem(self, obj):
        return format_html('<span style="font-family: monospace; background: #f5f5f5; padding: 2px 5px; border-radius: 3px;">{}</span>', obj.mehsul.oem)
    get_oem.short_description = 'OEM'
    get_oem.admin_order_field = 'mehsul__oem'

    def get_qiymet(self, obj):
        return format_html('<span class="price-badge">{} AZN</span>', obj.qiymet)
    get_qiymet.short_description = 'Qiymət'

    def get_total(self, obj):
        return format_html('<span class="price-badge">{} AZN</span>', obj.miqdar * obj.qiymet)
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
        return format_html('<span class="rating-stars">{}</span>', stars)
    get_qiymetlendirme.short_description = 'Qiymətləndirmə'

    def get_tarix(self, obj):
        return obj.tarix.astimezone(timezone.get_current_timezone()).strftime('%d-%m-%Y %H:%M')
    get_tarix.short_description = 'Tarix'

    def get_tesdiq(self, obj):
        if obj.tesdiq:
            return format_html('<span style="color: #2e7d32; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #c62828; font-weight: bold;">✗</span>')
    get_tesdiq.short_description = 'Təsdiq'

    def tesdiqle(self, request, queryset):
        queryset.update(tesdiq=True)
        self.message_user(request, "Seçilmiş rəylər təsdiqləndi.")
    tesdiqle.short_description = "Seçilmiş rəyləri təsdiqlə"

    def tesdiq_legv_et(self, request, queryset):
        queryset.update(tesdiq=False)
        self.message_user(request, "Seçilmiş rəylərin təsdiqi ləğv edildi.")
    tesdiq_legv_et.short_description = "Seçilmiş rəylərin təsdiqini ləğv et"
