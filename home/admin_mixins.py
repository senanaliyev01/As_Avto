from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Count, Sum, F, Avg
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import datetime

class StockStatusFilter(SimpleListFilter):
    """Stok vəziyyətini süzgəcləmək üçün xüsusi filter"""
    title = 'Stok vəziyyəti'
    parameter_name = 'stok_veziyyeti'

    def lookups(self, request, model_admin):
        return (
            ('kritik', 'Kritik (0)'),
            ('az', 'Az (1-5)'),
            ('orta', 'Orta (6-10)'),
            ('kifayet', 'Kifayət (11-20)'),
            ('bol', 'Bol (20+)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'kritik':
            return queryset.filter(stok=0)
        if self.value() == 'az':
            return queryset.filter(stok__gt=0, stok__lte=5)
        if self.value() == 'orta':
            return queryset.filter(stok__gt=5, stok__lte=10)
        if self.value() == 'kifayet':
            return queryset.filter(stok__gt=10, stok__lte=20)
        if self.value() == 'bol':
            return queryset.filter(stok__gt=20)
        return queryset

class ProfitMarginFilter(SimpleListFilter):
    """Qazanc marjasını süzgəcləmək üçün xüsusi filter"""
    title = 'Qazanc marjası'
    parameter_name = 'qazanc_marjasi'

    def lookups(self, request, model_admin):
        return (
            ('zeif', 'Zəif (10% altı)'),
            ('normal', 'Normal (10-25%)'),
            ('yaxsi', 'Yaxşı (25-50%)'),
            ('yuksel', 'Yüksək (50%+)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zeif':
            return queryset.filter(qiymet__lte=F('maya_qiymet') * 1.1)
        if self.value() == 'normal':
            return queryset.filter(qiymet__gt=F('maya_qiymet') * 1.1, qiymet__lte=F('maya_qiymet') * 1.25)
        if self.value() == 'yaxsi':
            return queryset.filter(qiymet__gt=F('maya_qiymet') * 1.25, qiymet__lte=F('maya_qiymet') * 1.5)
        if self.value() == 'yuksel':
            return queryset.filter(qiymet__gt=F('maya_qiymet') * 1.5)
        return queryset

class EnhancedButtonsAdminMixin:
    """Admin paneldə düymələr əlavə etmək üçün xüsusi mixin"""
    
    def get_buttons(self, obj):
        """İdarə panelində məhsul üçün xüsusi düymələr"""
        buttons = []
        
        # Redaktə düyməsi
        buttons.append(
            format_html('<a href="{}" class="button" style="background-color: #007bff; color: white; '
                      'padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px;">'
                      '<i class="fas fa-edit"></i></a>',
                      reverse(f'admin:home_mehsul_change', args=[obj.id]))
        )
        
        # Avtomobillər siyahısını göstərmək üçün düymə
        buttons.append(
            format_html('<a href="{}" class="button" style="background-color: #28a745; color: white; '
                      'padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px;">'
                      '<i class="fas fa-car"></i></a>',
                      reverse(f'admin:home_mehsul_changelist') + f'?avtomobil__id__exact={obj.avtomobil.id}')
        )
        
        # Firma məhsullarını göstərmək üçün düymə
        buttons.append(
            format_html('<a href="{}" class="button" style="background-color: #6c757d; color: white; '
                      'padding: 5px 10px; border-radius: 4px; text-decoration: none;">'
                      '<i class="fas fa-industry"></i></a>',
                      reverse(f'admin:home_mehsul_changelist') + f'?firma__id__exact={obj.firma.id}')
        )
        
        return format_html('<div class="admin-actions">{}</div>', mark_safe(''.join(buttons)))
    
    get_buttons.short_description = 'Əməliyyatlar'
    get_buttons.allow_tags = True
    
class EnhancedProductListMixin:
    """Məhsul siyahısını təkmilləşdirmək üçün mixin"""
    
    def get_profit_margin(self, obj):
        """Qazanc marjasını hesablamaq və göstərmək"""
        if obj.maya_qiymet and obj.maya_qiymet > 0:
            margin = ((obj.qiymet - obj.maya_qiymet) / obj.maya_qiymet) * 100
            if margin < 10:
                return format_html('<span style="color: #dc3545; font-weight: bold;">{:.1f}%</span>', margin)
            elif margin < 25:
                return format_html('<span style="color: #fd7e14; font-weight: bold;">{:.1f}%</span>', margin)
            elif margin < 50:
                return format_html('<span style="color: #28a745; font-weight: bold;">{:.1f}%</span>', margin)
            else:
                return format_html('<span style="color: #007bff; font-weight: bold;">{:.1f}%</span>', margin)
        return '-'
    get_profit_margin.short_description = 'Qazanc %'
    get_profit_margin.admin_order_field = 'qiymet'
    
    def get_status_badge(self, obj):
        """Məhsul vəziyyəti nişanını göstər"""
        if obj.stok == 0:
            return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                             'border-radius: 12px; font-size: 11px;">Bitib</span>')
        elif obj.stok <= 5:
            return format_html('<span style="background-color: #fd7e14; color: white; padding: 3px 8px; '
                             'border-radius: 12px; font-size: 11px;">Az qalıb</span>')
        elif obj.yenidir:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                             'border-radius: 12px; font-size: 11px;">Yeni</span>')
        
        return ''
    get_status_badge.short_description = 'Status'
    
    def get_list_display(self, request):
        """Administrator üçün kontekstə uyğun siyahı göstər"""
        if request.user.is_superuser:
            return ['adi', 'get_firma', 'get_brend_kod', 'get_oem', 'get_qiymet', 'get_maya_qiymet', 
                   'get_profit_margin', 'get_stok', 'get_status_badge', 'get_buttons', 'sekil_preview']
        else:
            return ['adi', 'get_firma', 'get_brend_kod', 'get_oem', 'get_qiymet', 'get_stok', 
                   'get_status_badge', 'sekil_preview']
    
    def get_list_filter(self, request):
        """Administrator üçün kontekstə uyğun filterlər göstər"""
        if request.user.is_superuser:
            return ['kateqoriya', 'firma', 'avtomobil', 'vitrin', 'yenidir', StockStatusFilter, ProfitMarginFilter]
        else:
            return ['kateqoriya', 'firma', 'avtomobil', 'vitrin', 'yenidir', StockStatusFilter] 