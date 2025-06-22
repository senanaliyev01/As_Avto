from django import forms
from .models import Mehsul, Kateqoriya, Firma, Avtomobil, Vitrin, Sifaris

class MehsulForm(forms.ModelForm):
    class Meta:
        model = Mehsul
        fields = [
            'adi', 'kateqoriya', 'firma', 'avtomobil', 'vitrin',
            'brend_kod', 'oem', 'olcu', 'maya_qiymet', 'qiymet', 
            'stok', 'kodlar', 'melumat', 'sekil', 'yenidir'
        ]
        widgets = {
            'adi': forms.TextInput(attrs={'class': 'form-control'}),
            'kateqoriya': forms.Select(attrs={'class': 'form-control'}),
            'firma': forms.Select(attrs={'class': 'form-control'}),
            'avtomobil': forms.Select(attrs={'class': 'form-control'}),
            'vitrin': forms.Select(attrs={'class': 'form-control'}),
            'brend_kod': forms.TextInput(attrs={'class': 'form-control'}),
            'oem': forms.TextInput(attrs={'class': 'form-control'}),
            'olcu': forms.TextInput(attrs={'class': 'form-control'}),
            'maya_qiymet': forms.NumberInput(attrs={'class': 'form-control'}),
            'qiymet': forms.NumberInput(attrs={'class': 'form-control'}),
            'stok': forms.NumberInput(attrs={'class': 'form-control'}),
            'kodlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'melumat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sekil': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'yenidir': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 

class SifarisEditForm(forms.ModelForm):
    class Meta:
        model = Sifaris
        fields = ['status', 'odenilen_mebleg', 'qeyd']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'odenilen_mebleg': forms.NumberInput(attrs={'class': 'form-control'}),
            'qeyd': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 