from django.contrib import admin
from .models import HeroSlider

@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('basliq',)
    search_fields = ['basliq', 'metn']
