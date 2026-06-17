from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category', 'product_type',
            'stock', 'reorder_level', 'warranty_months', 'installation_required',
            'delivery_time_days', 'video_url', 'image'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price must be positive")
        return price
