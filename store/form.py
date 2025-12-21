from django import forms
from store.models import Category

SORTING_CHOICES = [
        ("price_asc", "Price (Low to High)"),
        ("price_desc", "Price (High to Low)"),
        ("latest", "Latest"),
        ("oldest", "Oldest"),
        
        
    ]
class ProductFiltereForm(forms.Form):

    name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Product Name"}
        ),
        required=False,
    )
    min_price = forms.DecimalField(
        max_digits=10,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Min Price"}
        ),
    )
    max_price = forms.DecimalField(
        max_digits=10,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max Price"}
        ),
    )
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple( attrs={"class": "select2"} ),
    )

    
    sorting_key = forms.ChoiceField(
        choices=SORTING_CHOICES,
        required=False,
        initial=SORTING_CHOICES[0],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


   