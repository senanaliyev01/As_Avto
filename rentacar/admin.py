from django.contrib import admin
from .models import Car, CarImage

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'engine_capacity', 'car_type', 'sale_price', 'rent_price')
    search_fields = ('name',)
    list_filter = ('car_type',)

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car',)
    search_fields = ('car__name',)
