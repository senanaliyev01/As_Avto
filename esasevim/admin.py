from django.contrib import admin
from .models import Slider

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('basliq',)
    search_fields = ('basliq', 'alt_basliq')
