from django.contrib import admin
from .models import Kateqoriya, Brend, Marka, Mehsul, Sebet, Sifaris, SifarisMehsul, OEMKod, MusteriReyi, MarkaSekil, Model, Avtomodel, Motor, Il, Yanacaq
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.db import models
from django.contrib import messages
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.middleware.csrf import get_token
import pandas as pd
import re

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
            attrs={'rows': 5, 'style': 'width: 100%; font-family: monospace; resize: both;'})},
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

# Məhsul admin paaneli
admin.site.register(Model)
admin.site.register(Avtomodel)
admin.site.register(Motor)
admin.site.register(Il)
admin.site.register(Yanacaq)

class MehsulAdmin(admin.ModelAdmin):
    list_display = ('adi', 'kateqoriya', 'brend', 'marka', 'maya_qiymet', 'qiymet', 'brend_kod', 'oem', 'stok', 'yenidir', 'get_sekil')
    list_filter = ('kateqoriya', 'brend', 'marka', 'yenidir')
    search_fields = ('adi', 'kateqoriya__adi', 'brend__adi', 'marka__adi', 'brend_kod', 'oem', 'oem_kodlar__kod', 'yenidir',)
    inlines = [OEMKodInline]
    
    change_list_template = 'admin/mehsul_changelist.html'
    
    actions = ['yenilikden_sil', 'yenidir_et']
    
    # Məhsul redaktə/əlavə etmə səhifəsində sahələrin qruplaşdırılması
    fieldsets = (
        ('Şəkil', {
            'fields': ('sekil',),
            'classes': ('wide', 'extrapretty'),
            'description': 'Məhsul şəkli yükləyin. Şəkil avtomatik olaraq webp formatına çevriləcək.'
        }),
        ('Əsas Məlumatlar', {
            'fields': ('adi', 'kateqoriya', 'brend', 'marka', 'model'),
            'classes': ('wide',),
        }),
        ('Qiymət və Stok', {
            'fields': ('maya_qiymet', 'qiymet', 'stok', 'yenidir'),
            'classes': ('wide',),
        }),
        ('Kodlar', {
            'fields': ('brend_kod', 'oem'),
            'classes': ('wide',),
        }),
        ('Əlavə Məlumatlar', {
            'fields': ('haqqinda',),
            'classes': ('collapse',),
        }),
    )
    
    # Şəkil önizləməsi üçün
    readonly_fields = ('get_sekil_preview',)
    
    def get_sekil_preview(self, obj):
        if obj.sekil and hasattr(obj.sekil, 'url'):
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.sekil.url)
        return format_html('<span style="color: #999; font-style: italic;">Şəkil yüklənməyib</span>')
    get_sekil_preview.short_description = 'Cari şəkil'
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Əgər mövcud1 bir məhsul redaktə edilirsə, şəkil önizləməsini əlavə et
        if obj:
            fieldsets[0][1]['fields'] = ('get_sekil_preview', 'sekil')
        return fieldsets
    
    def get_sekil(self, obj):
        if obj.sekil:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 5px;" />', obj.sekil.url)
        return format_html('<span style="color: #999;">Şəkil yoxdur</span>')
    get_sekil.short_description = 'Şəkil'
    get_sekil.admin_order_field = 'sekil'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
        ]
        return my_urls + urls
    
    def import_excel_view(self, request):
        from django.shortcuts import render
        from django.http import HttpResponseRedirect
        import pandas as pd
        from django.contrib import messages
        from django.db import transaction
        
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                messages.error(request, 'Zəhmət olmasa Excel faylı seçin')
                return HttpResponseRedirect("../")
                
            if not excel_file.name.endswith('.xlsx'):
                messages.error(request, 'Yalnız .xlsx faylları qəbul edilir')
                return HttpResponseRedirect("../")
                
            try:
                df = pd.read_excel(excel_file)
                new_count = 0
                update_count = 0
                error_count = 0
                
                with transaction.atomic():  # Bütün əməliyyatları bir transaksiyada edirik
                    for _, row in df.iterrows():
                        try:
                            # Kateqoriya, brend və markanı tap və ya yarat
                            kateqoriya = None
                            brend = None
                            marka = None
                            
                            if 'kateqoriya' in row and pd.notna(row['kateqoriya']):
                                kateqoriya, _ = Kateqoriya.objects.get_or_create(adi=row['kateqoriya'])
                            
                            if 'brend' in row and pd.notna(row['brend']):
                                brend, _ = Brend.objects.get_or_create(adi=row['brend'])
                            
                            if 'marka' in row and pd.notna(row['marka']):
                                marka, _ = Marka.objects.get_or_create(adi=row['marka'])
                            
                            # Əlavə OEM kodlarını hazırla
                            elave_oem_kodlar = []
                            if 'elave_oem' in row and pd.notna(row['elave_oem']):
                                # Vergül, boşluq və / ilə ayrılmış OEM kodlarını ayır
                                temiz_oem = str(row['elave_oem']).replace(',', ' ').replace('/', ' ')
                                elave_oem_kodlar = [kod.strip() for kod in temiz_oem.split() if kod.strip()]
                                
                                # Birinci kodu brend_kod sütununa, ikinci kodu isə oem sütununa yerləşdir
                                if elave_oem_kodlar:
                                    # İlk olaraq sütunlardakı mövcud dəyərləri al
                                    brend_kod = row['brend_kod'] if 'brend_kod' in row and pd.notna(row['brend_kod']) else ''
                                    
                                    # Birinci kod varsa və brend_kod boşdursa
                                    if len(elave_oem_kodlar) >= 1 and (not brend_kod or brend_kod.strip() == ''):
                                        brend_kod = elave_oem_kodlar[0]
                                        row['brend_kod'] = brend_kod
                                    
                                    # İkinci kod varsa, oem sütununa yerləşdir
                                    if len(elave_oem_kodlar) >= 2:
                                        # Əgər oem sütunu dolu deyilsə
                                        if 'oem' not in row or not pd.notna(row['oem']) or not row['oem']:
                                            row['oem'] = elave_oem_kodlar[1]
                            
                            # brend_kod dəyərini təyin et (əgər hələ təyin edilməyibsə)
                            brend_kod = row['brend_kod'] if 'brend_kod' in row and pd.notna(row['brend_kod']) else ''
                            
                            # Əgər məhsulun adı varsa, boşluqları təmizlə:
                            # 1. Əvvəl və sondakı boşluqları sil (strip)
                            # 2. Sözlər arasındakı çoxlu boşluqları bir boşluğa çevir
                            if 'adi' in row and pd.notna(row['adi']):
                                # strip() əvvəl və sondakı boşluqları silir
                                temiz_ad = row['adi'].strip()
                                # \s+ bir və ya daha çox boşluq simvolu üçün regex patterndir
                                # Bu pattern ardıcıl boşluqları bir boşluğa çevirir
                                temiz_ad = re.sub(r'\s+', ' ', temiz_ad)
                                row['adi'] = temiz_ad
                            
                            # Eyni brend_kod ilə məhsul varmı yoxla (əgər brend_kod boş deyilsə)
                            existing_product = None
                            if brend_kod:
                                existing_product = Mehsul.objects.filter(brend_kod=brend_kod).first()
                            
                            if existing_product:
                                # Mövcud məhsulu yenilə
                                if 'adi' in row and pd.notna(row['adi']):
                                    # Adı təmizlə - əvvəl və sondakı boşluqları sil, çoxlu boşluqları bir boşluğa çevir
                                    temiz_ad = row['adi'].strip()
                                    temiz_ad = re.sub(r'\s+', ' ', temiz_ad)
                                    existing_product.adi = temiz_ad
                                if kateqoriya:
                                    existing_product.kateqoriya = kateqoriya
                                if brend:
                                    existing_product.brend = brend
                                if marka:
                                    existing_product.marka = marka
                                if 'stok' in row and pd.notna(row['stok']):
                                    existing_product.stok = row['stok']
                                else:
                                    existing_product.stok = 0
                                if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']):
                                    existing_product.maya_qiymet = row['maya_qiymet']
                                else:
                                    existing_product.maya_qiymet = 0
                                if 'qiymet' in row and pd.notna(row['qiymet']):
                                    existing_product.qiymet = row['qiymet']
                                else:
                                    existing_product.qiymet = 0
                                existing_product.yenidir = False
                                
                                # Haqqında məlumatını əlavə et
                                if 'haqqinda' in row and pd.notna(row['haqqinda']):
                                    existing_product.haqqinda = str(row['haqqinda'])
                                
                                if 'oem' in row and pd.notna(row['oem']):
                                    existing_product.oem = row['oem']
                                
                                existing_product.save()
                                
                                # Mövcud əlavə OEM kodlarını sil
                                existing_product.oem_kodlar.all().delete()
                                
                                # Yeni əlavə OEM kodlarını əlavə et
                                for kod in elave_oem_kodlar:
                                    OEMKod.objects.create(
                                        mehsul=existing_product,
                                        kod=kod
                                    )
                                
                                update_count += 1
                            else:
                                # Əsas sahələri hazırla
                                mehsul_data = {
                                    'adi': row['adi'].strip() if 'adi' in row and pd.notna(row['adi']) else '',
                                    'kateqoriya': kateqoriya,
                                    'brend': brend,
                                    'marka': marka,
                                    'brend_kod': brend_kod,
                                    'oem': row['oem'] if 'oem' in row and pd.notna(row['oem']) else '',
                                    'stok': row['stok'] if 'stok' in row and pd.notna(row['stok']) else 0,
                                    'maya_qiymet': row['maya_qiymet'] if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0,
                                    'qiymet': row['qiymet'] if 'qiymet' in row and pd.notna(row['qiymet']) else 0,
                                    'yenidir': False,
                                    'haqqinda': str(row['haqqinda']) if 'haqqinda' in row and pd.notna(row['haqqinda']) else None
                                }
                                
                                # Yeni məhsul yarat
                                yeni_mehsul = Mehsul.objects.create(**mehsul_data)
                                
                                # Əlavə OEM kodlarını əlavə et
                                for kod in elave_oem_kodlar:
                                    OEMKod.objects.create(
                                        mehsul=yeni_mehsul,
                                        kod=kod
                                    )
                                
                                new_count += 1
                                
                        except Exception as e:
                            error_count += 1
                            messages.error(request, f'Sətir xətası: {str(e)}')
                            continue
                
                if new_count > 0:
                    messages.success(request, f'{new_count} yeni məhsul əlavə edildi.')
                if update_count > 0:
                    messages.info(request, f'{update_count} mövcud məhsul yeniləndi.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} məhsulun əlavə/yenilənməsində xəta baş verdi.')
                    
                return HttpResponseRedirect("../")
                
            except Exception as e:
                messages.error(request, f'Excel faylını oxuyarkən xəta baş verdi: {str(e)}')
                return HttpResponseRedirect("../")
        
        return render(request, 'admin/import_excel.html')
    
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
