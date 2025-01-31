from django.contrib import admin
from .models import Car, CarImage

class CarImageInline(admin.TabularInline):  # Inline sinifi
    model = Car.images.through  # ManyToManyField üçün əlaqə modeli
    extra = 1  # Yeni şəkil əlavə etmək üçün boş forma

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'engine_capacity', 'car_type', 'sale_price', 'rent_price')
    search_fields = ('name',)
    list_filter = ('car_type',)
    inlines = [CarImageInline]  # Inline əlavə edildi

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('image',)
