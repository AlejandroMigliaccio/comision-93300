from django import forms
from productos.models import Productos


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['titulo', 'foto', 'descripcion', 'precio', 'sku', 'categoria', 'stock']
        widgets = {
            'titulo':      forms.TextInput(attrs={'placeholder': 'Nombre del producto'}),
            'foto':        forms.URLInput(attrs={'placeholder': 'https://...'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Descripción breve'}),
            'precio':      forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'sku':         forms.TextInput(attrs={'placeholder': 'Ej: SKU-001'}),
            'stock':       forms.NumberInput(attrs={'min': '0'}),
        }
        labels = {
            'titulo':      'Título',
            'foto':        'URL de imagen',
            'descripcion': 'Descripción',
            'precio':      'Precio ($)',
            'sku':         'SKU',
            'categoria':   'Categoría',
            'stock':       'Stock',
        }
