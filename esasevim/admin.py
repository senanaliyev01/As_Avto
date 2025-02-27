from django.contrib import admin
from .models import slider

@admin.register(slider)
class sliderAdmin(admin.ModelAdmin):
    list_display = ('basliq',)
    search_fields = ['basliq', 'metn']
