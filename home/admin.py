from django.contrib import admin
from .models import Kateqoriya, Firma, Avtomobil, Mehsul, Sifaris, SifarisItem, Vitrin, PopupImage, Profile, Header_Message, AvtomobilLogo, ProductReview
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from django.utils import timezone
from django.shortcuts import render
import pandas as pd
from django.contrib import messages
from django.db import transaction
import math
from django.contrib.admin import SimpleListFilter

def truncate_product_name(name, max_length=20):
    """Məhsul adını qısaldır və uzun olarsa ... əlavə edir"""
    if len(name) <= max_length:
        return name
    return name[:max_length-3] + "..."

@admin.register(Header_Message)
class Header_MessageAdmin(admin.ModelAdmin):
    list_display = ['mesaj']
    search_fields = ['mesaj']

@admin.register(Kateqoriya)
class KateqoriyaAdmin(admin.ModelAdmin):
    list_display = ['adi']
    search_fields = ['adi']

@admin.register(Vitrin)
class VitrinAdmin(admin.ModelAdmin):
    list_display = ['nomre']
    search_fields = ['nomre']

@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ['adi', 'logo_tag']
    search_fields = ['adi']

    def logo_tag(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:40px;max-width:80px;object-fit:contain;" />', obj.logo.url)
        return "-"
    logo_tag.short_description = "Logo"
    logo_tag.allow_tags = True

class AvtomobilLogoInline(admin.TabularInline):
    model = AvtomobilLogo
    extra = 1

@admin.register(Avtomobil)
class AvtomobilAdmin(admin.ModelAdmin):
    list_display = ['adi', 'avtomobil_logos_preview']
    inlines = [AvtomobilLogoInline]
    search_fields = ['adi']

    def avtomobil_logos_preview(self, obj):
        logos = obj.logolar.all()
        if logos:
            return format_html(''.join([
                '<img src="{}" style="height:40px;max-width:80px;object-fit:contain;margin-right:4px;" />'.format(logo.sekil.url)
                for logo in logos if logo.sekil
            ]))
        return "-"
    avtomobil_logos_preview.short_description = "Logolar"
    avtomobil_logos_preview.allow_tags = True

@admin.register(Mehsul)
class MehsulAdmin(admin.ModelAdmin):
    list_display = ['sahib', 'brend_kod', 'firma', 'adi',  'olcu', 'vitrin', 'stok', 'maya_qiymet', 'qiymet',  'yenidir', 'qalan_vaxt', 'sekil_preview']
    list_filter = ['sahib', 'kateqoriya', 'firma', 'avtomobil', 'vitrin', 'yenidir']
    search_fields = ['adi', 'brend_kod', 'oem', 'kodlar', 'olcu', 'sahib__username']
    change_list_template = 'admin/mehsul_change_list.html'
    actions = ['mark_as_new', 'remove_from_new']

    def sekil_preview(self, obj):
        from django.utils import timezone
        if obj.sekil:
            return format_html('<img src="{}?t={}" style="max-height: 50px;"/>', obj.sekil.url, int(timezone.now().timestamp()))
        return '-'
    sekil_preview.short_description = 'Şəkil'

    def qalan_vaxt(self, obj):
        if obj.yenidir and obj.qalan_vaxt():
            return format_html('<span style="color: #17a2b8; font-weight: bold;">{}</span>', obj.qalan_vaxt())
        return '-'
    qalan_vaxt.short_description = 'Qalan Vaxt'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
            path('export-pdf/', self.export_pdf, name='export_pdf'),
        ]
        return custom_urls + urls

    def export_pdf(self, request):
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io
        from django.http import HttpResponse

        # Font qeydiyyatı
        pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))

        # PDF yaratmaq
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="mehsullar.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []

        # Başlıq
        styles = getSampleStyleSheet()
        styles['Title'].fontName = 'NotoSans'
        title = Paragraph("AS AVTO +994 77 305 95 85", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Cədvəl başlıqları
        headers = ['№', 'Kod', 'Firma', 'Məhsul', 'Vitrin', 'Stok',  'Qiymət']
        
        # Məhsul məlumatları1
        data = [headers]
        for index, mehsul in enumerate(Mehsul.objects.all(), 1):
            row = [
                str(index),
                mehsul.brend_kod,
                mehsul.firma.adi if mehsul.firma else '-',
                truncate_product_name(mehsul.adi),
                str(mehsul.vitrin.nomre) if mehsul.vitrin else '-',
                str(mehsul.stok),
                f"{mehsul.qiymet} ₼"
            ]
            data.append(row)

        # Cədvəl yaratmaq
        table = Table(data)
        table.setStyle(TableStyle([
            # Başlıq sətri
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B5173')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            
            # Məhsul sətirləri
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            
            # Cədvəl xətləri
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B5173')),
            
            # Sütun enləri
            ('COLWIDTHS', (0, 0), (-1, -1), '*'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)

        # PDF-i yarat
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def mark_as_new(self, request, queryset):
        updated = queryset.update(yenidir=True, yeni_edildiyi_tarix=timezone.now())
        
        # 3 gün sonra avtomatik olaraq yenidən çıxar
        import threading
        def auto_remove_new():
            import time
            time.sleep(259200)  # 3 gün (72 saat)
            try:
                # Yenidən yeni olan məhsulları tap və yenidən çıxar
                from django.db import transaction
                with transaction.atomic():
                    new_products = Mehsul.objects.filter(id__in=queryset.values_list('id', flat=True), yenidir=True)
                    new_products.update(yenidir=False, yeni_edildiyi_tarix=None)
            except Exception as e:
                print(f"Auto remove new status error: {e}")
        
        # Thread-i başlat
        thread = threading.Thread(target=auto_remove_new)
        thread.daemon = True
        thread.start()
        
        self.message_user(request, f'{updated} məhsul yeni olaraq işarələndi və 3 gün sonra avtomatik olaraq yenidən çıxarılacaq.')
    mark_as_new.short_description = "Seçilmiş məhsulları yeni olaraq işarələ"

    def remove_from_new(self, request, queryset):
        updated = queryset.update(yenidir=False)
        self.message_user(request, f'{updated} məhsul yenilikdən silindi.')
    remove_from_new.short_description = "Seçilmiş məhsulları yenilikdən sil"

    def import_excel_view(self, request):
        if request.method == 'POST':
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                self.message_user(request, 'Zəhmət olmasa Excel faylı seçin', level=messages.ERROR)
                return HttpResponseRedirect("../")
                
            if not excel_file.name.endswith('.xlsx'):
                self.message_user(request, 'Yalnız .xlsx faylları qəbul edilir', level=messages.ERROR)
                return HttpResponseRedirect("../")
                
            try:
                df = pd.read_excel(excel_file)
                print(f"Excel faylının sütunları: {df.columns.tolist()}")
                print(f"Excel faylında {len(df)} sətir var")
                
                new_count = 0
                update_count = 0
                error_count = 0
                
                with transaction.atomic():
                    for index, row in df.iterrows():
                        try:
                            print(f"\nSətir {index + 1} emal edilir:")
                            print(f"Məlumatlar: {dict(row)}")
                            
                            # Sətirin bütün sütun adlarını təmizləyirik
                            row = {str(k).strip().lower(): v for k, v in row.items()}
                            
                            # Kateqoriya, firma və avtomobili tap və ya yarat
                            kateqoriya = None
                            firma = None
                            avtomobil = None
                            vitrin = None
                            
                            if 'kateqoriya' in row and pd.notna(row['kateqoriya']):
                                kateqoriya, _ = Kateqoriya.objects.get_or_create(adi=str(row['kateqoriya']).strip())
                                print(f"Kateqoriya: {kateqoriya}")
                            
                            if 'firma' in row and pd.notna(row['firma']):
                                firma, _ = Firma.objects.get_or_create(adi=str(row['firma']).strip())
                                print(f"Firma: {firma}")
                            
                            if 'avtomobil' in row and pd.notna(row['avtomobil']):
                                avtomobil, _ = Avtomobil.objects.get_or_create(adi=str(row['avtomobil']).strip())
                                print(f"Avtomobil: {avtomobil}")

                            if 'vitrin' in row and pd.notna(row['vitrin']):
                                vitrin, _ = Vitrin.objects.get_or_create(nomre=str(row['vitrin']).strip())
                                print(f"Vitrin: {vitrin}")

                            # Məhsulun adını təmizlə
                            if 'adi' not in row or pd.isna(row['adi']):
                                print("XƏTA: Məhsulun adı yoxdur")
                                self.message_user(request, f'Sətir {index + 1}: Məhsulun adı boşdur', level=messages.ERROR)
                                error_count += 1
                                continue

                            temiz_ad = str(row['adi']).strip()
                            temiz_ad = ' '.join(temiz_ad.split())
                            print(f"Təmizlənmiş ad: {temiz_ad}")

                            # brend_kod-u təyin et
                            brend_kod = None
                            if 'brend_kod' in row and pd.notna(row['brend_kod']):
                                value = row['brend_kod']
                                if isinstance(value, float) and math.isnan(value):
                                    brend_kod = None
                                else:
                                    brend_kod = str(value).strip()
                                    if brend_kod.lower() == 'nan' or brend_kod == '':
                                        brend_kod = None

                            if not brend_kod:
                                print("XƏTA: Brend kodu boşdur")
                                self.message_user(request, f'Sətir {index + 1}: Brend kodu boşdur', level=messages.ERROR)
                                error_count += 1
                                continue

                            print(f"Brend kod: {brend_kod}")

                            # Mövcud məhsulu həm brend_kod, həm firma, həm də sahib ilə yoxla
                            existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma=firma, sahib=request.user).first()

                            try:
                                if existing_product:
                                    # Mövcud məhsulu yenilə, firmaya toxunma!
                                    if not existing_product.sahib:
                                        existing_product.sahib = request.user
                                    existing_product.adi = temiz_ad
                                    existing_product.kateqoriya = kateqoriya
                                    existing_product.avtomobil = avtomobil
                                    existing_product.vitrin = vitrin
                                    existing_product.brend_kod = brend_kod
                                    existing_product.olcu = str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else ''
                                    existing_product.maya_qiymet = float(row['maya_qiymet']) if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0
                                    existing_product.qiymet = float(row['qiymet']) if 'qiymet' in row and pd.notna(row['qiymet']) else 0
                                    existing_product.stok = int(row['stok']) if 'stok' in row and pd.notna(row['stok']) else 0
                                    existing_product.kodlar = str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else ''
                                    existing_product.melumat = str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else ''
                                    existing_product.save()
                                    print(f"Məhsul yeniləndi: {existing_product}")
                                    update_count += 1
                                else:
                                    # Yeni məhsul yarat
                                    mehsul_data = {
                                        'adi': temiz_ad,
                                        'kateqoriya': kateqoriya,
                                        'firma': firma,
                                        'avtomobil': avtomobil,
                                        'vitrin': vitrin,
                                        'brend_kod': brend_kod,
                                        'oem': '',  # oem-i boş saxla
                                        'olcu': str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else '',
                                        'maya_qiymet': float(row['maya_qiymet']) if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0,
                                        'qiymet': float(row['qiymet']) if 'qiymet' in row and pd.notna(row['qiymet']) else 0,
                                        'stok': int(row['stok']) if 'stok' in row and pd.notna(row['stok']) else 0,
                                        'kodlar': str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else '',
                                        'melumat': str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else '',
                                        'yenidir': False,
                                        'sahib': request.user,
                                    }
                                    
                                    yeni_mehsul = Mehsul.objects.create(**mehsul_data)
                                    print(f"Yeni məhsul yaradıldı: {yeni_mehsul}")
                                    new_count += 1

                            except Exception as e:
                                print(f"Məhsul əlavə edilərkən xəta: {e}")
                                self.message_user(request, f'Sətir {index + 1}: {str(e)}', level=messages.ERROR)
                                error_count += 1
                                continue

                        except Exception as e:
                            print(f"Sətir {index + 1} emal edilərkən xəta: {e}")
                            self.message_user(request, f'Sətir {index + 1}: {str(e)}', level=messages.ERROR)
                            error_count += 1
                            continue

                    # Nəticəni göstər
                    success_message = f"Excel faylı uğurla import edildi! "
                    if new_count > 0:
                        success_message += f"{new_count} yeni məhsul əlavə edildi. "
                    if update_count > 0:
                        success_message += f"{update_count} məhsul yeniləndi. "
                    if error_count > 0:
                        success_message += f"{error_count} xəta baş verdi."
                    
                    self.message_user(request, success_message, level=messages.SUCCESS)
                    return HttpResponseRedirect("../")

            except Exception as e:
                print(f"Excel faylı oxunarkən xəta: {e}")
                self.message_user(request, f'Excel faylı oxunarkən xəta: {str(e)}', level=messages.ERROR)
                return HttpResponseRedirect("../")

        # GET request üçün
        context = {
            'title': 'Excel faylı import et',
            'has_permission': True,
        }
        return render(request, 'admin/import_excel.html', context)

    def changelist_view(self, request, extra_context=None):
        # Statistikanı hesablayırıq
        from django.db.models import Sum, F, ExpressionWrapper, DecimalField
        
        total_stats = Mehsul.objects.aggregate(
            toplam_maya = Sum(ExpressionWrapper(
                F('stok') * F('maya_qiymet'),
                output_field=DecimalField()
            )),
            toplam_satis = Sum(ExpressionWrapper(
                F('stok') * F('qiymet'),
                output_field=DecimalField()
            ))
        )
        
        # Ümumi xeyiri hesablayırıq
        total_stats['toplam_xeyir'] = (total_stats['toplam_satis'] or 0) - (total_stats['toplam_maya'] or 0)

        extra_context = extra_context or {}
        extra_context['total_stats'] = total_stats
        
        return super().changelist_view(request, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        # Əgər məhsul yeni olaraq işarələnibsə, tarixi qeyd et
        if obj.yenidir:
            obj.yeni_edildiyi_tarix = timezone.now()
        
        # Əgər məhsul yeni olaraq işarələnibsə, 3 gün sonra avtomatik olaraq yenidən çıxar
        if obj.yenidir:  # Həm yeni yaradılan, həm də redaktə edilən məhsullar üçün
            import threading
            def auto_remove_new():
                import time
                time.sleep(259200)  # 3 gün (72 saat)
                try:
                    # Məhsulu yenidən yüklə və yenidir statusunu yoxla
                    from django.db import transaction
                    with transaction.atomic():
                        mehsul = Mehsul.objects.select_for_update().get(id=obj.id)
                        if mehsul.yenidir:  # Əgər hələ də yenidirsə
                            mehsul.yenidir = False
                            mehsul.yeni_edildiyi_tarix = None
                            mehsul.save()
                except Exception as e:
                    print(f"Auto remove new status error: {e}")
            
            # Thread-i başlat
            thread = threading.Thread(target=auto_remove_new)
            thread.daemon = True
            thread.start()
        
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if hasattr(instance, 'yenidir') and instance.yenidir:
                # Əgər məhsul yeni olaraq işarələnibsə, tarixi qeyd et
                from django.utils import timezone
                instance.yeni_edildiyi_tarix = timezone.now()
                
                # Əgər məhsul yeni olaraq işarələnibsə, 3 gün sonra avtomatik olaraq yenidən çıxar
                import threading
                def auto_remove_new():
                    import time
                    time.sleep(259200)  # 3 gün (72 saat)
                    try:
                        # Məhsulu yenidən yüklə və yenidir statusunu yoxla
                        from django.db import transaction
                        with transaction.atomic():
                            mehsul = Mehsul.objects.select_for_update().get(id=instance.id)
                            if mehsul.yenidir:  # Əgər hələ də yenidirsə
                                mehsul.yenidir = False
                                mehsul.yeni_edildiyi_tarix = None
                                mehsul.save()
                    except Exception as e:
                        print(f"Auto remove new status error: {e}")
                
                # Thread-i başlat
                thread = threading.Thread(target=auto_remove_new)
                thread.daemon = True
                thread.start()
        
        formset.save()
        super().save_formset(request, form, formset, change)

class SifarisItemInline(admin.TabularInline):
    model = SifarisItem
    extra = 0
    readonly_fields = ['mehsul', 'mehsul_sahibi']
    fields = ['mehsul', 'mehsul_sahibi', 'miqdar', 'qiymet']

    def mehsul_sahibi(self, obj):
        if obj.mehsul and obj.mehsul.sahib:
            return obj.mehsul.sahib.username
        return "AS-AVTO"
    mehsul_sahibi.short_description = 'Satıcı'

    def get_max_num(self, request, obj=None, **kwargs):
        if obj:
            return obj.sifarisitem_set.count()
        return 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mehsul":
            kwargs["queryset"] = Mehsul.objects.filter(stok__gt=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sifaris.update_total()

class SellerFilter(SimpleListFilter):
    title = 'Satıcı'
    parameter_name = 'satici'

    def lookups(self, request, model_admin):
        from django.contrib.auth.models import User
        sellers = set()
        for item in SifarisItem.objects.select_related('mehsul__sahib').all():
            if item.mehsul and item.mehsul.sahib:
                sellers.add((item.mehsul.sahib.id, item.mehsul.sahib.username))
            else:
                sellers.add((0, 'AS-AVTO'))
        return sorted(sellers, key=lambda x: (x[0] != 0, x[1]))

    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            if value == '0':
                # Only orders with at least one item with no seller
                return queryset.filter(sifarisitem__mehsul__sahib__isnull=True).distinct()
            else:
                return queryset.filter(sifarisitem__mehsul__sahib__id=value).distinct()
        return queryset

@admin.register(Sifaris)
class SifarisAdmin(admin.ModelAdmin):
    list_display = ['id', 'istifadeci', 'saticilar', 'tarix', 'status', 'catdirilma_usulu', 'umumi_mebleg', 'odenilen_mebleg', 'qaliq_borc', 'pdf_button']
    list_filter = ['status', 'catdirilma_usulu', 'tarix', 'istifadeci', SellerFilter]
    search_fields = ['istifadeci__username']
    readonly_fields = ['istifadeci', 'tarix', 'umumi_mebleg', 'qaliq_borc']
    fields = ['istifadeci', 'tarix', 'status', 'catdirilma_usulu', 'umumi_mebleg', 'odenilen_mebleg', 'qaliq_borc', 'qeyd']
    inlines = [SifarisItemInline]
    change_list_template = 'admin/sifaris_change_list.html'

    def saticilar(self, obj):
        # Sifarişdə olan bütün məhsulların sahiblərini tapırıq
        satici_set = set()
        for item in obj.sifarisitem_set.all():
            if item.mehsul and item.mehsul.sahib:
                satici_set.add(item.mehsul.sahib.username)
            else:
                satici_set.add('AS-AVTO')
        return ', '.join(satici_set)
    saticilar.short_description = 'Satıcı(lar)'

    def pdf_button(self, obj):
        return format_html(
            '<a class="button" href="export-pdf/{}" style="background-color: #417690; color: white; '
            'padding: 5px 10px; border-radius: 4px; text-decoration: none;">PDF</a>',
            obj.id
        )
    pdf_button.short_description = 'PDF'
    pdf_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-pdf/<int:sifaris_id>/', self.export_pdf, name='export-pdf'),
        ]
        return custom_urls + urls

    def export_pdf(self, request, sifaris_id):
        sifaris = Sifaris.objects.get(id=sifaris_id)
        sifaris_items = sifaris.sifarisitem_set.all()
        statistics = Sifaris.get_order_statistics(sifaris.istifadeci)

        # PDF yaratmaq
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sifaris_{sifaris_id}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=0, bottomMargin=20)
        elements = []

        # Universal font qeydiyyatı
        pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))

        # Logo və sifariş məlumatları üçün cədvəl yaradırıq
        logo_path = 'static/images/Header_Logo.png'
        try:
            logo = Image(logo_path, width=150, height=100)
            
            # Sifariş məlumatlarını hazırlayırıq
            styles = getSampleStyleSheet()
            styles['Title'].fontName = 'NotoSans'
            styles['Normal'].fontName = 'NotoSans'
            styles['Normal'].spaceBefore = 0
            styles['Normal'].spaceAfter = 0
            
            # Tarixi Azərbaycan formatında göstəririk
            az_months = {
                1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
                5: 'May', 6: 'İyun', 7: 'İyul', 8: 'Avqust',
                9: 'Sentyabr', 10: 'Oktyabr', 11: 'Noyabr', 12: 'Dekabr'
            }
            
            local_time = timezone.localtime(sifaris.tarix)
            az_date = f"{local_time.day} {az_months[local_time.month]} {local_time.year}, {local_time.strftime('%H:%M')}"
            
            # Sifariş məlumatlarını sağ tərəfə yerləşdiririk
            order_info_table = Table([
                [Paragraph(f"Müştəri: {sifaris.istifadeci.username}", styles['Normal'])],
                [Paragraph(f"Tarix: {az_date}", styles['Normal'])],
                [Paragraph(f"Çatdırılma: {sifaris.get_catdirilma_usulu_display()}", styles['Normal'])],
                [Paragraph(f"Sifariş №{sifaris_id}", styles['Normal'])]
            ], colWidths=[200])  # Sabit genişlik təyin edirik
            
            order_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            # İki sütunlu cədvəl yaradırıq
            header_table = Table([
                [logo, order_info_table]
            ], colWidths=[doc.width-220, 220])  # Sağ tərəfə daha çox yer ayırırıq
            
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
        except Exception as e:
            print(f"Logo əlavə edilərkən xəta: {e}")

        # Məhsullar cədvəli - başlıqları mərkəzləşdirmək üçün Paragraph istifadə edirik
        headerStyle = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='NotoSans',
            fontSize=9,
            textColor=colors.whitesmoke,
            alignment=1,  # Mərkəz
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )

        headers = [
            Paragraph('№', headerStyle),
            Paragraph('Kod', headerStyle),
            Paragraph('Firma', headerStyle),
            Paragraph('Məhsul', headerStyle),
            Paragraph('Vitrin', headerStyle),
            Paragraph('Miqdar', headerStyle),
            Paragraph('Qiymət', headerStyle),
            Paragraph('Cəmi', headerStyle)
        ]

        # Məhsullar cədvəli
        data = [headers]
        total_amount = 0
        
        # Məhsul məlumatları üçün stil
        contentStyle = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontName='NotoSans',
            fontSize=8,
            alignment=1,  # Mərkəz
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )

        for index, item in enumerate(sifaris_items, 1):
            row = [
                Paragraph(str(index), contentStyle),
                Paragraph(item.mehsul.brend_kod, contentStyle),
                Paragraph(item.mehsul.firma.adi, contentStyle),
                Paragraph(truncate_product_name(item.mehsul.adi), contentStyle),
                Paragraph(str(item.mehsul.vitrin.nomre) if item.mehsul.vitrin else '-', contentStyle),
                Paragraph(str(item.miqdar), contentStyle),
                Paragraph(f"{item.qiymet} ₼", contentStyle),
                Paragraph(f"{item.umumi_mebleg} ₼", contentStyle)
            ]
            data.append(row)
            total_amount += item.umumi_mebleg

        # Cədvəl stilləri
        table = Table(data)
        table.setStyle(TableStyle([
            # Başlıq sətri
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B5173')),  # Tünd mavi
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'NotoSans'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            
            # Məhsul sətirləri
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'NotoSans'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            
            # Cədvəl xətləri
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#2B5173')),
            
            # Sütun enləri
            ('COLWIDTHS', (0, 0), (-1, -1), '*'),  # Bütün sütunlar üçün avtomatik en
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Bütün sütunlar üçün mərkəz düzləndirmə
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Şaquli mərkəz düzləndirmə
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 15))  # Boşluq azaldıldı

        # Ümumi məbləğ və Qalıq borc cədvəli
        totalStyle = ParagraphStyle(
            'TotalStyle',
            parent=styles['Normal'],
            fontName='NotoSans',
            fontSize=10,
            alignment=0,  # Sol tərəf
            spaceAfter=0,
            spaceBefore=0,
            leading=12
        )

        amountStyle = ParagraphStyle(
            'AmountStyle',
            parent=styles['Normal'],
            fontName='NotoSans',
            fontSize=10,
            alignment=2,  # Sağ tərəf
            spaceAfter=0,
            spaceBefore=0,
            leading=12,
            textColor=colors.HexColor('#2B5173')  # Tünd mavi
        )

        total_data = [
            [Paragraph('Ümumi Cəmi :', totalStyle), Paragraph(f"{total_amount} ₼", amountStyle)],
            [Paragraph('Ümumi Borc :', totalStyle), Paragraph(f"{statistics['umumi_borc']} ₼", amountStyle)]
        ]

        total_table = Table(total_data, colWidths=[100, 100])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (0, -1), 20),  # Mətn və rəqəm arasında məsafə
        ]))

        # Cədvəli sağa tərəfə yerləşdirmək üçün
        align_table = Table([[total_table]], colWidths=[525])  # A4 səhifəsinin eni
        align_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ]))
        
        elements.append(align_table)
        elements.append(Spacer(1, 30))

        # Ödəniş bölməsi
        payment_text = f"Ödənilən Məbləğ: ___________________________ ₼"
        elements.append(Paragraph(payment_text, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # İmzalarr
        signature_data = [[
            Paragraph("Təhvil Verdi: _________________", styles['Normal']),
            Paragraph(f"Təhvil Aldı: {sifaris.istifadeci.username} _________________", styles['Normal'])
        ]]
        signature_table = Table(signature_data, colWidths=[250, 250])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(signature_table)

        # PDF-i yarat
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def has_add_permission(self, request):
        return False  # Sifarişlər yalnız saytdan əlavə edilə bilər

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        form.instance.update_total()

    def changelist_view(self, request, extra_context=None):
        # İstifadəçilər üzrə statistikanı hesablayırıq
        from django.db.models import Count, Sum, F
        from django.contrib.auth.models import User
        
        user_stats = User.objects.annotate(
            sifaris_sayi=Count('sifaris'),
            umumi_mebleg=Sum('sifaris__umumi_mebleg'),
            umumi_odenilen=Sum('sifaris__odenilen_mebleg'),
            umumi_borc=Sum(F('sifaris__umumi_mebleg') - F('sifaris__odenilen_mebleg'))
        ).values('username', 'sifaris_sayi', 'umumi_mebleg', 'umumi_odenilen', 'umumi_borc')

        # Ümumi statistika
        total_stats = {
            'total_orders': sum(stat['sifaris_sayi'] for stat in user_stats),
            'total_amount': sum(stat['umumi_mebleg'] or 0 for stat in user_stats),
            'total_paid': sum(stat['umumi_odenilen'] or 0 for stat in user_stats),
            'total_debt': sum(stat['umumi_borc'] or 0 for stat in user_stats),
        }

        extra_context = extra_context or {}
        extra_context['user_statistics'] = user_stats
        extra_context['total_statistics'] = total_stats
        
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(PopupImage)
class PopupImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'basliq', 'aktiv', 'sira', 'yaradilma_tarixi', 'sekil_preview']
    list_editable = ['aktiv', 'sira']
    ordering = ['sira', '-yaradilma_tarixi']
    
    def sekil_preview(self, obj):
        if obj.sekil:
            return format_html('<img src="{}" style="max-height: 50px;"/>', obj.sekil.url)
        return '-'
    sekil_preview.short_description = 'Şəkil'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'address', 'is_verified', 'verification_button']
    list_filter = ['is_verified']
    search_fields = ['user__username', 'phone', 'address']
    actions = ['verify_profiles', 'unverify_profiles']

    def verification_button(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="color: green;">✓ Təsdiqlənib</span>'
            )
        return format_html(
            '<span style="color: red;">✗ Təsdiqlənməyib</span>'
        )
    verification_button.short_description = 'Status'

    def verify_profiles(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f'{queryset.count()} profil təsdiqləndi.')
    verify_profiles.short_description = "Seçilmiş profilləri təsdiqlə"

    def unverify_profiles(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f'{queryset.count()} profilin təsdiqi ləğv edildi.')
    unverify_profiles.short_description = "Seçilmiş profillərin təsdiqini ləğv et"

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('mehsul', 'user', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'mehsul', 'rating')
    search_fields = ('mehsul__adi', 'user__username', 'comment')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Seçilmiş şərhləri təsdiqlə'