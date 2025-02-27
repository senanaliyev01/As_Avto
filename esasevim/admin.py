from django.contrib import admin
from .models import HeroSlider

@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('basliq', 'aktiv', 'sira')
    list_editable = ('aktiv', 'sira')
    list_filter = ('aktiv',)
