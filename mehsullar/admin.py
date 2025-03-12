from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi, MarkaSekil, Model, Avtomodel, Motor, Il, Yanacaq, AxtarisSozleri
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.contrib import messages
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token

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
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(
            attrs={'rows': 5, 'style': 'width: 100%; font-family: monospace;'})},
    }

# AxtarisSozleri admin paneli
@admin.register(AxtarisSozleri)
class AxtarisSozleriAdmin(admin.ModelAdmin):
    list_display = ('adi', 'sozler')
    search_fields = ('adi', 'sozler')
    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(
            attrs={'rows': 5, 'style': 'width: 100%; font-family: monospace;'})},
    }

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
admin.site.register(Model)
admin.site.register(Avtomodel)
admin.site.register(Motor)
admin.site.register(Il)
admin.site.register(Yanacaq)

class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'axtaris_sozleri', 'maya_qiymet', 'qiymet', 'brend_kod', 'oem', 'stok', 'yenidir')
    list_filter = ('kateqoriya', 'brend', 'marka', 'axtaris_sozleri')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem', 'oem_kodlar__kod', 'yenidir', 'axtaris_sozleri__adi', 'axtaris_sozleri__sozler')
    inlines = [OEMKodInline]
    filter_horizontal = ('eynidir',)
    
    actions = ['yenilikden_sil', 'yenidir_et', 'axtaris_sozleri_teyin_et', 'axtaris_sozleri_sil']
    
    def changelist_view(self, request, extra_context=None):
        # Əsas görünüşü əldə edək
        response = super().changelist_view(request, extra_context)
        
        try:
            # Bütün məhsulların ümumi dəyərini hesablayaq
            butun_mehsullar = Mehsul.objects.all()
            toplam_maya = sum(mehsul.maya_qiymet * mehsul.stok for mehsul in butun_mehsullar)
            toplam_satis = sum(mehsul.qiymet * mehsul.stok for mehsul in butun_mehsullar)
            mehsul_sayi = butun_mehsullar.count()
            
            # Əgər response-da context varsa
            if hasattr(response, 'context_data'):
                # Mesaj əlavə edək
                messages.info(request, f"Məhsul sayı: {mehsul_sayi} ədəd | Toplam Maya: {toplam_maya:.2f} AZN | Toplam Satış: {toplam_satis:.2f} AZN | Potensial Qazanc: {toplam_satis - toplam_maya:.2f} AZN")
        except:
            # Xəta baş verərsə, heç nə etmə
            pass
            
        return response
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['model'].widget.attrs.update({
            'style': 'width: 500px; height: 300px; overflow-y: auto;'  # Genişlik və hündürlük artırılır
        })
        form.base_fields['model'].widget.can_add_related = True  # Yeni model əlavə etməyə imkan verir
        return form

    def yenilikden_sil(self, request, queryset):
        queryset.update(yenidir=False)
        self.message_user(request, "Seçilmiş məhsullar yenilikdən silindi.")
    yenilikden_sil.short_description = "Seçilmiş məhsulları yenilikdən sil"

    def yenidir_et(self, request, queryset):
        queryset.update(yenidir=True)
        self.message_user(request, "Seçilmiş məhsullar yenidir olaraq işarələndi.")
    yenidir_et.short_description = "Seçilmiş məhsulları yenidir et"
    
    def axtaris_sozleri_sil(self, request, queryset):
        # Axtarış sözləri olan məhsulları sayırıq
        mehsullar_with_axtaris = queryset.exclude(axtaris_sozleri=None).count()
        
        # Axtarış sözlərini silirik (None olaraq təyin edirik)
        queryset.update(axtaris_sozleri=None)
        
        # İstifadəçiyə bildiriş göndəririk
        if mehsullar_with_axtaris > 0:
            self.message_user(request, f"{mehsullar_with_axtaris} məhsuldan axtarış sözləri silindi.")
        else:
            self.message_user(request, "Seçilmiş məhsulların heç birində axtarış sözü yox idi.", level=messages.INFO)
    
    axtaris_sozleri_sil.short_description = "Seçilmiş məhsullardan axtarış sözlərini sil"
    
    def axtaris_sozleri_teyin_et(self, request, queryset):
        # Əgər bu bir POST sorğusudursa və axtarış sözü seçilibsə
        if 'axtaris_sozleri_id' in request.POST:
            axtaris_sozleri_id = request.POST.get('axtaris_sozleri_id')
            if axtaris_sozleri_id:
                try:
                    axtaris_sozleri = AxtarisSozleri.objects.get(id=axtaris_sozleri_id)
                    # Seçilmiş məhsullara axtarış sözlərini təyin edirik
                    queryset.update(axtaris_sozleri=axtaris_sozleri)
                    self.message_user(request, f"{queryset.count()} məhsula '{axtaris_sozleri.adi}' axtarış sözlərini təyin edildi.")
                    return None
                except AxtarisSozleri.DoesNotExist:
                    self.message_user(request, "Seçilmiş axtarış sözü tapılmadı.", level=messages.ERROR)
            else:
                self.message_user(request, "Axtarış sözü seçilmədi.", level=messages.WARNING)
                
        # Bütün axtarış sözlərini əldə edirik
        axtaris_sozleri = AxtarisSozleri.objects.all()
        
        # Əgər heç bir axtarış sözü yoxdursa, xəbərdarlıq edirik
        if not axtaris_sozleri.exists():
            self.message_user(request, "Heç bir axtarış sözü tapılmadı. Əvvəlcə axtarış sözləri yaradın.", level=messages.WARNING)
            return None
        
        # Axtarış sözlərini seçmək üçün HTML formu yaradırıq
        select_options = ''.join([f'<option value="{axtaris.id}">{axtaris.adi} - {axtaris.sozler}</option>' for axtaris in axtaris_sozleri])
        
        # Seçilmiş məhsulların ID-lərini formda göndərmək üçün hidden inputlar yaradırıq
        hidden_inputs = ''.join([f'<input type="hidden" name="_selected_action" value="{obj.pk}">' for obj in queryset])
        
        # CSRF token əldə edirik
        csrf_token = get_token(request)
        
        # Formu göstəririk
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Axtarış sözlərini təyin et</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f8f8f8;
                }}
                h2 {{
                    color: #333;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }}
                select {{
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin-bottom: 15px;
                    font-size: 14px;
                }}
                .btn {{
                    background-color: #417690;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .btn:hover {{
                    background-color: #2b5070;
                }}
                .count {{
                    font-weight: bold;
                    color: #417690;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Axtarış sözlərini təyin et</h2>
                <p>Seçilmiş <span class="count">{queryset.count()}</span> məhsula axtarış sözlərini təyin edin:</p>
                <form action="" method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                    <input type="hidden" name="action" value="axtaris_sozleri_teyin_et">
                    {hidden_inputs}
                    <div>
                        <label for="axtaris_sozleri_id">Axtarış Sözləri:</label>
                        <select name="axtaris_sozleri_id" id="axtaris_sozleri_id">
                            <option value="">---------</option>
                            {select_options}
                        </select>
                    </div>
                    <input type="submit" name="apply" value="Təyin et" class="btn">
                </form>
            </div>
        </body>
        </html>
        """
        
        # Formu göstəririk
        return HttpResponse(html)
    
    axtaris_sozleri_teyin_et.short_description = "Seçilmiş məhsullara axtarış sözlərini təyin et"

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
