from django import forms
from products.models import Product, QuoteRequest


class QuoteForm(forms.ModelForm):

    class Meta:
        model = QuoteRequest
        fields = [
            "product",
            "institution_name",
            "location",
            "quantity",
            "phone",
            "email",
            "message",
            "attachment",
        ]

        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "institution_name": forms.TextInput(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "attachment": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")
        self.fields["product"].empty_label = "Select a product"

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1.")
        return quantity