from django import forms
from .models import Mehsul, Kateqoriya, Firma, Avtomobil, Vitrin, Sifaris, SifarisItem, ProductReview

class MehsulForm(forms.ModelForm):
    class Meta:
        model = Mehsul
        fields = [
            'adi', 'kateqoriya', 'firma', 'avtomobil', 'vitrin',
            'brend_kod', 'olcu', 'maya_qiymet', 'qiymet', 
            'stok', 'kodlar', 'melumat', 'sekil', 'yenidir'
        ]
        widgets = {
            'adi': forms.TextInput(attrs={'class': 'form-control'}),
            'kateqoriya': forms.Select(attrs={'class': 'form-control'}),
            'firma': forms.Select(attrs={'class': 'form-control'}),
            'avtomobil': forms.Select(attrs={'class': 'form-control'}),
            'vitrin': forms.Select(attrs={'class': 'form-control'}),
            'brend_kod': forms.TextInput(attrs={'class': 'form-control'}),
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

class SifarisItemEditForm(forms.ModelForm):
    class Meta:
        model = SifarisItem
        fields = ['miqdar', 'qiymet']
        widgets = {
            'miqdar': forms.NumberInput(attrs={'class': 'form-control form-control-sm item-input', 'min': '1', 'data-field': 'quantity'}),
            'qiymet': forms.NumberInput(attrs={'class': 'form-control form-control-sm item-input', 'step': '0.01', 'data-field': 'price'}),
        } 

class ProductReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Qiymət",
        coerce=int
    )
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Şərhinizi yazın...'}), label="Şərh")

    class Meta:
        model = ProductReview
        fields = ['rating', 'comment'] 