from django.contrib import admin
from .models import HeroSlide

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('basliq', 'alt_basliq', 'yaradilma_tarixi')
    list_filter = ('yaradilma_tarixi',)
    search_fields = ('basliq', 'alt_basliq')
