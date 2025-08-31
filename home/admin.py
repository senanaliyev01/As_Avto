from django.contrib import admin
from .models import Kateqoriya, Firma, Avtomobil, Mehsul, Sifaris, SifarisItem, Vitrin, PopupImage, Profile, Header_Message
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
import os
import uuid
import json
from django.http import JsonResponse
from django.conf import settings

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
    list_display = ['adi']
    search_fields = ['adi']

@admin.register(Avtomobil)
class AvtomobilAdmin(admin.ModelAdmin):
    list_display = ['adi']
    search_fields = ['adi']

@admin.register(Mehsul)
class MehsulAdmin(admin.ModelAdmin):
    list_display = ['brend_kod', 'firma', 'adi',  'olcu', 'vitrin', 'stok', 'maya_qiymet', 'qiymet',  'yenidir', 'sekil_preview', 'change_image_button']
    list_filter = ['kateqoriya', 'firma', 'avtomobil', 'vitrin', 'yenidir']
    search_fields = ['adi', 'brend_kod', 'oem', 'kodlar', 'olcu']
    change_list_template = 'admin/mehsul_change_list.html'
    actions = ['mark_as_new', 'remove_from_new']

    def sekil_preview(self, obj):
        if obj.sekil:
            return format_html('<img src="{}" id="product-image-{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;"/>', obj.sekil.url, obj.id)
        return '-'
    sekil_preview.short_description = 'Şəkil'

    def change_image_button(self, obj):
        if obj.sekil:
            return format_html(
                '<button type="button" class="change-image-btn" data-product-id="{}" title="Şəkil Dəyiş"><i class="fas fa-image"></i></button>',
                obj.id
            )
        else:
            return format_html(
                '<button type="button" class="change-image-btn" data-product-id="{}" title="Şəkil Əlavə Et"><i class="fas fa-plus"></i></button>',
                obj.id
            )
    change_image_button.short_description = '🖼️'
    change_image_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.import_excel_view, name='import_excel'),
            path('export-pdf/', self.export_pdf, name='export_pdf'),
            path('import-excel-init/', self.import_excel_init, name='import_excel_init'),
            path('import-excel-batch/', self.import_excel_batch, name='import_excel_batch'),
            path('import-excel-finalize/', self.import_excel_finalize, name='import_excel_finalize'),
            path('change-image/', self.change_image, name='change_image'),
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
                mehsul.adi,
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
        updated = queryset.update(yenidir=True)
        self.message_user(request, f'{updated} məhsul yeni olaraq işarələndi.')
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
                deleted_count = 0
                # Excel faylındakı məhsulların açarları: (brend_kod, firma_id)
                excel_product_keys = set()
                
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

                            # Bu sətirdəki məhsulun açarını yadda saxla
                            excel_product_keys.add((brend_kod, firma.id if firma else None))

                            # Mövcud məhsulu həm brend_kod, həm firma ilə yoxla
                            if firma:
                                existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma=firma).first()
                            else:
                                existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma__isnull=True).first()

                            try:
                                if existing_product:
                                    # Mövcud məhsulu yenilə
                                    existing_product.adi = temiz_ad
                                    
                                    # Excel-də olan məlumatları yenilə, olmayanları None et
                                    existing_product.kateqoriya = kateqoriya
                                    existing_product.firma = firma
                                    existing_product.avtomobil = avtomobil
                                    existing_product.vitrin = vitrin
                                    
                                    # Digər məlumatları yenilə
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
                                        'yenidir': False
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

                    # Excel-də olmayan məhsulları sil
                    if excel_product_keys:
                        all_products_qs = Mehsul.objects.all()
                        to_delete_ids = [
                            p.id for p in all_products_qs.only('id', 'brend_kod', 'firma_id')
                            if (p.brend_kod, p.firma_id) not in excel_product_keys
                        ]
                        if to_delete_ids:
                            deleted_count, _ = Mehsul.objects.filter(id__in=to_delete_ids).delete()

                    # Nəticəni göstər
                    success_message = f"Excel faylı uğurla import edildi! "
                    if new_count > 0:
                        success_message += f"{new_count} yeni məhsul əlavə edildi. "
                    if update_count > 0:
                        success_message += f"{update_count} məhsul yeniləndi. "
                    if deleted_count > 0:
                        success_message += f"{deleted_count} məhsul Excel-də olmadığı üçün silindi. "
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

    def import_excel_init(self, request):
        """Excel faylını qəbul edir, sətirləri təmizləyib job faylına yazır, job_id qaytarır"""
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

        excel_file = request.FILES.get("excel_file")
        if not excel_file:
            return JsonResponse({'status': 'error', 'message': 'Excel faylı seçin.'}, status=400)
        if not excel_file.name.endswith('.xlsx'):
            return JsonResponse({'status': 'error', 'message': 'Yalnız .xlsx faylı qəbul edilir.'}, status=400)

        # Faylı media/imports altına yaz
        imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
        os.makedirs(imports_dir, exist_ok=True)
        job_id = str(uuid.uuid4())
        saved_path = os.path.join(imports_dir, f'admin_{job_id}.xlsx')
        with open(saved_path, 'wb+') as dest:
            for chunk in excel_file.chunks():
                dest.write(chunk)

        # Exceli oxu və sətirləri təmizlə
        try:
            df = pd.read_excel(saved_path)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Excel oxunmadı: {e}'}, status=400)

        cleaned_rows = []
        columns_display = [str(c) for c in df.columns]
        columns_lower = [str(c).strip().lower() for c in df.columns]
        for index, row in df.iterrows():
            row = {str(k).strip().lower(): v for k, v in row.items()}
            cleaned_rows.append(row)

        total_rows = len(cleaned_rows)

        # Job state faylı
        jobs_dir = os.path.join(imports_dir, 'jobs')
        os.makedirs(jobs_dir, exist_ok=True)
        job_state_path = os.path.join(jobs_dir, f'{job_id}.json')
        job_state = {
            'file_path': saved_path,
            'total_rows': total_rows,
            'processed_rows': 0,
            'new_count': 0,
            'update_count': 0,
            'error_count': 0,
            'deleted_count': 0,
            'excel_product_keys': [],  # (brend_kod, firma_id)
            'error_details': [],  # ['5-ci sətir: ...', ...]
            'rows': cleaned_rows,
            'columns': columns_lower,
            'columns_display': columns_display,
        }
        with open(job_state_path, 'w', encoding='utf-8') as f:
            json.dump(job_state, f, ensure_ascii=False)

        return JsonResponse({'status': 'ok', 'job_id': job_id, 'total_rows': total_rows})

    def import_excel_batch(self, request):
        """Verilən interval üzrə (start, size) sətirləri emal edir"""
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

        job_id = request.POST.get('job_id')
        try:
            start = int(request.POST.get('start', 0))
            size = int(request.POST.get('size', 100))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'start/size yanlışdır.'}, status=400)

        imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
        job_state_path = os.path.join(imports_dir, 'jobs', f'{job_id}.json')
        if not os.path.exists(job_state_path):
            return JsonResponse({'status': 'error', 'message': 'Job tapılmadı.'}, status=404)

        with open(job_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        rows = state.get('rows', [])
        subset = rows[start:start+size]
        if not subset:
            return JsonResponse({'status': 'ok', 'message': 'Heç nə yoxdur', 'processed_rows': state['processed_rows'], 'new_count': state['new_count'], 'update_count': state['update_count'], 'error_count': state['error_count']})

        new_count = state['new_count']
        update_count = state['update_count']
        error_count = state['error_count']
        excel_keys = set(tuple(k) for k in state.get('excel_product_keys', []))
        error_details = state.get('error_details', [])
        batch_errors = []

        # Emal məntiqi
        for idx, row in enumerate(subset, start=start):
            try:
                excel_line_no = idx + 2  # Başlıq 1-ci sətir, data 2-dən başlayır
                # Model referansları
                kateqoriya = None
                firma = None
                avtomobil = None
                vitrin = None

                if 'kateqoriya' in row and pd.notna(row['kateqoriya']):
                    kateqoriya, _ = Kateqoriya.objects.get_or_create(adi=str(row['kateqoriya']).strip())
                if 'firma' in row and pd.notna(row['firma']):
                    firma, _ = Firma.objects.get_or_create(adi=str(row['firma']).strip())
                if 'avtomobil' in row and pd.notna(row['avtomobil']):
                    avtomobil, _ = Avtomobil.objects.get_or_create(adi=str(row['avtomobil']).strip())
                if 'vitrin' in row and pd.notna(row['vitrin']):
                    vitrin, _ = Vitrin.objects.get_or_create(nomre=str(row['vitrin']).strip())

                # Hazırla: sətirin bütün dəyərləri və xəta yığımı
                full_row = {str(k): ('' if (k not in row or pd.isna(row.get(k))) else str(row.get(k))) for k in row.keys()}
                row_errors = []
                def add_err(field_name, message):
                    row_errors.append({
                        'line': excel_line_no,
                        'message': message,
                        'field': field_name,
                        'row': full_row,
                    })

                # Tələb olunan sahələr: adi , brend_kod , firma , avtomobil, maya_qiymet, qiymet, stok
                # adi
                if ('adi' not in row) or pd.isna(row.get('adi')) or str(row.get('adi')).strip() == '':
                    add_err('adi', 'Məhsulun adı boşdur')

                temiz_ad = str(row['adi']).strip()
                temiz_ad = ' '.join(temiz_ad.split())

                # brend_kod
                brend_kod = None
                if 'brend_kod' in row and pd.notna(row['brend_kod']):
                    value = row['brend_kod']
                    if not (isinstance(value, float) and math.isnan(value)):
                        candidate = str(value).strip()
                        if candidate.lower() != 'nan' and candidate != '':
                            brend_kod = candidate
                if not brend_kod:
                    add_err('brend_kod', 'Brend kodu boşdur')

                # firma (required)
                firma_name = row.get('firma') if 'firma' in row else ''
                if (firma_name is None) or (str(firma_name).strip() == '') or pd.isna(firma_name):
                    add_err('firma', 'Firma boşdur')
                else:
                    firma, _ = Firma.objects.get_or_create(adi=str(firma_name).strip())

                # avtomobil (required)
                avtomobil_name = row.get('avtomobil') if 'avtomobil' in row else ''
                if (avtomobil_name is None) or (str(avtomobil_name).strip() == '') or pd.isna(avtomobil_name):
                    add_err('avtomobil', 'Avtomobil boşdur')
                else:
                    avtomobil, _ = Avtomobil.objects.get_or_create(adi=str(avtomobil_name).strip())

                # maya_qiymet (required float)
                maya_qiymet_value = row.get('maya_qiymet')
                if maya_qiymet_value is None or (str(maya_qiymet_value).strip() == '') or pd.isna(maya_qiymet_value):
                    add_err('maya_qiymet', 'maya_qiymet boşdur')
                    maya_qiymet_parsed = None
                else:
                    try:
                        maya_qiymet_parsed = float(str(maya_qiymet_value).replace(',', '.'))
                    except Exception:
                        maya_qiymet_parsed = None
                        add_err('maya_qiymet', 'maya_qiymet rəqəm olmalıdır')

                # qiymet (required float)
                qiymet_value = row.get('qiymet')
                if qiymet_value is None or (str(qiymet_value).strip() == '') or pd.isna(qiymet_value):
                    add_err('qiymet', 'qiymet boşdur')
                    qiymet_parsed = None
                else:
                    try:
                        qiymet_parsed = float(str(qiymet_value).replace(',', '.'))
                    except Exception:
                        qiymet_parsed = None
                        add_err('qiymet', 'qiymet rəqəm olmalıdır')

                # stok (required int)
                stok_value = row.get('stok')
                if stok_value is None or (str(stok_value).strip() == '') or pd.isna(stok_value):
                    add_err('stok', 'stok boşdur')
                    stok_parsed = None
                else:
                    try:
                        stok_parsed = int(float(str(stok_value).replace(',', '.')))
                    except Exception:
                        stok_parsed = None
                        add_err('stok', 'stok tam ədəd olmalıdır')

                # Yığılmış xəta varsa bu sətiri keç
                if row_errors:
                    error_count += len(row_errors)
                    batch_errors.extend(row_errors)
                    continue

                excel_keys.add((brend_kod, firma.id if firma else None))

                # Bu nöqtədə tələb olunanlar var, firmada var
                existing_product = Mehsul.objects.filter(brend_kod=brend_kod, firma=firma).first()

                if existing_product:
                    existing_product.adi = temiz_ad
                    existing_product.kateqoriya = kateqoriya
                    existing_product.avtomobil = avtomobil
                    existing_product.vitrin = vitrin
                    existing_product.olcu = str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else ''
                    existing_product.maya_qiymet = maya_qiymet_parsed or 0
                    existing_product.qiymet = qiymet_parsed or 0
                    existing_product.stok = stok_parsed or 0
                    existing_product.kodlar = str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else ''
                    existing_product.melumat = str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else ''
                    existing_product.save()
                    update_count += 1
                else:
                    mehsul_data = {
                        'adi': temiz_ad,
                        'kateqoriya': kateqoriya,
                        'firma': firma,
                        'avtomobil': avtomobil,
                        'vitrin': vitrin,
                        'brend_kod': brend_kod,
                        'oem': '',
                        'olcu': str(row['olcu']).strip() if 'olcu' in row and pd.notna(row['olcu']) else '',
                        'maya_qiymet': maya_qiymet_parsed or 0,
                        'qiymet': qiymet_parsed or 0,
                        'stok': stok_parsed or 0,
                        'kodlar': str(row['kodlar']) if 'kodlar' in row and pd.notna(row['kodlar']) else '',
                        'melumat': str(row['melumat']) if 'melumat' in row and pd.notna(row['melumat']) else '',
                        'yenidir': False
                    }
                    Mehsul.objects.create(**mehsul_data)
                    new_count += 1
            except Exception as e:
                error_count += 1
                full_row = {str(k): ('' if (k not in row or pd.isna(row.get(k))) else str(row.get(k))) for k in row.keys()}
                batch_errors.append({
                    'line': excel_line_no,
                    'message': str(e),
                    'field': None,
                    'row': full_row,
                })
                continue

        # State-i yenilə
        state['new_count'] = new_count
        state['update_count'] = update_count
        state['error_count'] = error_count
        state['processed_rows'] = min(state['total_rows'], start + len(subset))
        state['excel_product_keys'] = list(excel_keys)
        # Toplam error detallarını yığ
        if batch_errors:
            error_details.extend(batch_errors)
            state['error_details'] = error_details
        with open(job_state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)

        return JsonResponse({
            'status': 'ok',
            'processed_rows': state['processed_rows'],
            'total_rows': state['total_rows'],
            'new_count': new_count,
            'update_count': update_count,
            'error_count': error_count,
            'errors': batch_errors,
            'columns': state.get('columns_display') or [],
        })

    def import_excel_finalize(self, request):
        """Excel-də olmayan məhsulları silir və job fayllarını təmizləyir"""
        if request.method != 'POST':
            return JsonResponse({'status': 'error', 'message': 'Yalnız POST.'}, status=405)

        job_id = request.POST.get('job_id')
        imports_dir = os.path.join(settings.MEDIA_ROOT, 'imports')
        job_state_path = os.path.join(imports_dir, 'jobs', f'{job_id}.json')
        if not os.path.exists(job_state_path):
            return JsonResponse({'status': 'error', 'message': 'Job tapılmadı.'}, status=404)

        with open(job_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        excel_keys = set(tuple(k) for k in state.get('excel_product_keys', []))
        deleted_count = 0
        if excel_keys:
            all_products_qs = Mehsul.objects.all()
            to_delete_ids = [
                p.id for p in all_products_qs.only('id', 'brend_kod', 'firma_id')
                if (p.brend_kod, p.firma_id) not in excel_keys
            ]
            if to_delete_ids:
                deleted_count, _ = Mehsul.objects.filter(id__in=to_delete_ids).delete()

        # Faylları təmizlə
        try:
            if os.path.exists(state.get('file_path', '')):
                os.remove(state['file_path'])
        except Exception:
            pass
        try:
            os.remove(job_state_path)
        except Exception:
            pass

        return JsonResponse({
            'status': 'ok',
            'deleted_count': deleted_count,
            'total_errors': len(state.get('error_details', [])),
            'error_details': state.get('error_details', []),
            'columns': state.get('columns_display') or []
        })

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

    def change_image(self, request):
        if request.method != 'POST':
            return JsonResponse({
                'status': 'error',
                'message': 'Yalnız POST metodu qəbul edilir.'
            })
        
        try:
            product_id = request.POST.get('product_id')
            image_file = request.FILES.get('image')
            
            if not product_id or not image_file:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Məhsul ID və ya şəkil faylı tapılmadı.'
                })
            
            # Quick validation
            if not image_file.content_type.startswith('image/'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Yalnız şəkil faylları qəbul edilir.'
                })
            
            # Check file size (max 5MB)
            if image_file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Şəkil faylı çox böyükdür. Maksimum 5MB olmalıdır.'
                })
            
            # Get product
            try:
                product = Mehsul.objects.select_for_update().get(id=product_id)
            except Mehsul.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Məhsul tapılmadı.'
                })
            
            # Delete old image if exists (async)
            if product.sekil:
                old_image_path = product.sekil.path
                if os.path.exists(old_image_path):
                    try:
                        os.remove(old_image_path)
                    except OSError:
                        pass  # Ignore file deletion errors
            
            # Save new image
            product.sekil = image_file
            product.save(update_fields=['sekil'])
            
            return JsonResponse({
                'status': 'success',
                'message': 'Şəkil uğurla yeniləndi!',
                'new_image_url': product.sekil.url,
                'product_id': product_id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Xəta baş verdi: {str(e)}'
            })

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
                Paragraph(item.mehsul.adi, contentStyle),
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
            return format_html('<img src="{}" id="popup-image-{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;"/>', obj.sekil.url, obj.id)
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