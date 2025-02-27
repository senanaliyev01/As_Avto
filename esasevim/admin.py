from django.contrib import admin
from .models import MainSlider

@admin.register(MainSlider)
class MainSliderAdmin(admin.ModelAdmin):
    list_display = ('basliq', 'alt_basliq', 'aktiv', 'sira')
    list_editable = ('aktiv', 'sira')
    list_filter = ('aktiv',)
    search_fields = ('basliq', 'alt_basliq')
