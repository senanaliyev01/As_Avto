from django.contrib import admin
from .models import Kateqoriya, Firma, Avtomobil, Mehsul, Sifaris, SifarisItem, Vitrin, PopupImage
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponse, HttpResponseRedirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from django.utils import timezone
from django.shortcuts import render
import pandas as pd
from django.contrib import messages
from django.db import transaction

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
    list_display = ['adi']
    search_fields = ['adi']

@admin.register(Avtomobil)
class AvtomobilAdmin(admin.ModelAdmin):
    list_display = ['adi']
    search_fields = ['adi']

@admin.register(Mehsul)
class MehsulAdmin(admin.ModelAdmin):
    list_display = ['adi',  'firma',  'brend_kod', 'oem', 'maya_qiymet', 'qiymet', 'stok', 'yenidir']
    list_filter = ['kateqoriya', 'firma', 'avtomobil', 'vitrin', 'yenidir']
    search_fields = ['adi', 'brend_kod', 'oem', 'kodlar']
    list_editable = ['qiymet', 'stok']
    change_list_template = 'admin/mehsul_change_list.html'
    actions = ['mark_as_new', 'remove_from_new']

    def mark_as_new(self, request, queryset):
        updated = queryset.update(yenidir=True)
        self.message_user(request, f'{updated} məhsul yeni olaraq işarələndi.')
    mark_as_new.short_description = "Seçilmiş məhsulları yeni olaraq işarələ"

    def remove_from_new(self, request, queryset):
        updated = queryset.update(yenidir=False)
        self.message_user(request, f'{updated} məhsul yenilikdən silindi.')
    remove_from_new.short_description = "Seçilmiş məhsulları yenilikdən sil"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
        ]
        return custom_urls + urls

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

                            # Əvvəlcə kodlar sütunundan brend_kod və oem-i almağa çalışaq
                            kodlar_list = []
                            if 'kodlar' in row and pd.notna(row['kodlar']):
                                kodlar_list = str(row['kodlar']).strip().split()

                            # brend_kod-u təyin et
                            brend_kod = None
                            if 'brend_kod' in row and pd.notna(row['brend_kod']):
                                brend_kod = str(row['brend_kod']).strip()
                            elif kodlar_list and len(kodlar_list) >= 1:
                                brend_kod = kodlar_list[0]

                            if not brend_kod:
                                print("XƏTA: Brend kodu və kodlar sütunu boşdur")
                                self.message_user(request, f'Sətir {index + 1}: Brend kodu və kodlar sütunu boşdur', level=messages.ERROR)
                                error_count += 1
                                continue

                            print(f"Brend kod: {brend_kod}")

                            # oem-i təyin et
                            oem = None
                            if 'oem' in row and pd.notna(row['oem']):
                                oem = str(row['oem']).strip()
                            elif kodlar_list and len(kodlar_list) >= 2:
                                oem = kodlar_list[1]
                            else:
                                oem = ''

                            existing_product = Mehsul.objects.filter(brend_kod=brend_kod).first()

                            try:
                                if existing_product:
                                    # Mövcud məhsulu yenilə
                                    existing_product.adi = temiz_ad
                                    if kateqoriya:
                                        existing_product.kateqoriya = kateqoriya
                                    if firma:
                                        existing_product.firma = firma
                                    if avtomobil:
                                        existing_product.avtomobil = avtomobil
                                    if vitrin:
                                        existing_product.vitrin = vitrin
                                    
                                    existing_product.brend_kod = brend_kod
                                    existing_product.oem = oem
                                    existing_product.olcu = str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else ''
                                    existing_product.vitrin = vitrin
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
                                        'oem': oem,
                                        'olcu': str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else '',
                                        'maya_qiymet': float(row['maya_qiymet']) if 'maya_qiymet' in row and pd.notna(row['maya_qiymet']) else 0,
                                        'qiymet': float(row['qiymet']) if 'qiymet' in row and pd.notna(row['qiymet']) else 0,
                                        'stok': int(row['stok']) if 'stok' in row and pd.notna(row['stok']) else 0,
                                        'kodlar': str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else '',
                                        'melumat': str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else '',
                                        'yenidir': False
                                    }
                                    
                                    yeni_mehsul = Mehsul.objects.create(**mehsul_data)
                                    print(f"Yeni məhsul yaradıldı: {yeni_mehsul}")
                                    new_count += 1

                            except Exception as e:
                                print(f"Məhsul yaradılarkən/yenilənərkən xəta: {str(e)}")
                                error_count += 1
                                self.message_user(request, f'Sətir {index + 1}: {str(e)}', level=messages.ERROR)
                                continue

                        except Exception as e:
                            print(f"Sətir emal edilərkən xəta: {str(e)}")
                            error_count += 1
                            self.message_user(request, f'Sətir {index + 1}: {str(e)}', level=messages.ERROR)
                            continue

                print(f"\nNəticələr:")
                print(f"Yeni məhsullar: {new_count}")
                print(f"Yenilənən məhsullar: {update_count}")
                print(f"Xətalar: {error_count}")

                if new_count > 0:
                    self.message_user(request, f'{new_count} yeni məhsul əlavə edildi.', level=messages.SUCCESS)
                if update_count > 0:
                    self.message_user(request, f'{update_count} mövcud məhsul yeniləndi.', level=messages.INFO)
                if error_count > 0:
                    self.message_user(request, f'{error_count} məhsulun əlavə/yenilənməsində xəta baş verdi.', level=messages.WARNING)
                    
                return HttpResponseRedirect("../")
                
            except Exception as e:
                print(f"Ümumi xəta: {str(e)}")
                self.message_user(request, f'Excel faylını oxuyarkən xəta baş verdi: {str(e)}', level=messages.ERROR)
                return HttpResponseRedirect("../")
        
        return HttpResponseRedirect("../")

class SifarisItemInline(admin.TabularInline):
    model = SifarisItem
    extra = 0
    readonly_fields = ['mehsul']
    fields = ['mehsul', 'miqdar', 'qiymet']

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

@admin.register(Sifaris)
class SifarisAdmin(admin.ModelAdmin):
    list_display = ['id', 'istifadeci', 'tarix', 'status', 'catdirilma_usulu', 'umumi_mebleg', 'odenilen_mebleg', 'qaliq_borc', 'pdf_button']
    list_filter = ['status', 'catdirilma_usulu', 'tarix', 'istifadeci']
    search_fields = ['istifadeci__username']
    readonly_fields = ['istifadeci', 'tarix', 'umumi_mebleg', 'qaliq_borc']
    fields = ['istifadeci', 'tarix', 'status', 'catdirilma_usulu', 'umumi_mebleg', 'odenilen_mebleg', 'qaliq_borc', 'qeyd']
    inlines = [SifarisItemInline]
    change_list_template = 'admin/sifaris_change_list.html'

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

        # PDF yaratmaq
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="sifaris_{sifaris_id}.pdf"'

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []

        # Universal font qeydiyyatı
        pdfmetrics.registerFont(TTFont('NotoSans', 'static/fonts/NotoSans-Regular.ttf'))

        # Stillər
        styles = getSampleStyleSheet()
        styles['Title'].fontName = 'NotoSans'
        styles['Normal'].fontName = 'NotoSans'
        
        # Başlıq
        elements.append(Paragraph(f"Sifariş №{sifaris_id}", styles['Title']))
        elements.append(Spacer(1, 20))

        # Sifariş məlumatları - Tarixi Azərbaycan formatında göstəririk
        elements.append(Paragraph(f"Müştəri: {sifaris.istifadeci.username}", styles['Normal']))
        
        # Tarixi Azərbaycan formatında göstəririk
        az_months = {
            1: 'Yanvar', 2: 'Fevral', 3: 'Mart', 4: 'Aprel',
            5: 'May', 6: 'İyun', 7: 'İyul', 8: 'Avqust',
            9: 'Sentyabr', 10: 'Oktyabr', 11: 'Noyabr', 12: 'Dekabr'
        }
        
        # Tarixi lokal vaxta çeviririk
        local_time = timezone.localtime(sifaris.tarix)
        az_date = f"{local_time.day} {az_months[local_time.month]} {local_time.year}, {local_time.strftime('%H:%M')}"
        elements.append(Paragraph(f"Tarix: {az_date}", styles['Normal']))
        
        elements.append(Paragraph(f"Çatdırılma: {sifaris.get_catdirilma_usulu_display()}", styles['Normal']))
        elements.append(Spacer(1, 20))

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
            Paragraph('Məhsul', headerStyle),
            Paragraph('Brend Kod', headerStyle),
            Paragraph('OEM', headerStyle),
            Paragraph('Vitrin', headerStyle),
            Paragraph('Qiymət', headerStyle),
            Paragraph('Miqdar', headerStyle),
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
                Paragraph(item.mehsul.adi, contentStyle),
                Paragraph(item.mehsul.brend_kod, contentStyle),
                Paragraph(item.mehsul.oem, contentStyle),
                Paragraph(item.mehsul.vitrin or '-', contentStyle),
                Paragraph(f"{item.qiymet} ₼", contentStyle),
                Paragraph(str(item.miqdar), contentStyle),
                Paragraph(f"{item.umumi_mebleg} ₼", contentStyle)
            ]
            data.append(row)
            total_amount += item.umumi_mebleg

        # Cədvəl stilləri
        table = Table(data, colWidths=[25, 120, 70, 70, 60, 60, 50, 70])
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
            [Paragraph('Qalıq Borc :', totalStyle), Paragraph(f"{sifaris.qaliq_borc} ₼", amountStyle)]
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
        
        # İmzalar
        signature_data = [[
            Paragraph("İmza: _________________", styles['Normal']),
            Paragraph("Möhür: _________________", styles['Normal'])
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
