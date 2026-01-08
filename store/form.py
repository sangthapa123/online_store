from django import forms
from store.models import Category, Order,Review
from accounts.models import DeliveryPerson


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

class OrderChangeForm(forms.ModelForm):

    delivery_person = forms.ModelChoiceField(
        queryset=DeliveryPerson.objects.filter(is_verified=True,is_active=True),
        required=False,
    )

    class Meta:
        model = Order
        fields = ["delivery_person"]


    def save(self, commit=True):
            if self.cleaned_data["delivery_person"]:
                self.instance.status = Order.Status.ON_THE_WAY
            return super().save(commit)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text", "rating"]

        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-control", "placeholder": "Write your review here"}
            ),
            "rating": forms.HiddenInput(),
        }

    def save(self, commit=True, context=None):
        if not context:
            raise ValueError("Context with user and product is required")

        user = context.get("user")
        product = context.get("product")

        if commit:
            # Check if we're updating an existing review (form has instance)
            if self.instance and self.instance.pk:
                # Update existing review
                self.instance.text = self.cleaned_data.get("text")
                self.instance.rating = self.cleaned_data.get("rating")
                self.instance.save()
                return self.instance
            else:
                # Create new review (allows multiple reviews per user/product)
                review = Review.objects.create(
                    user=user,
                    product=product,
                    text=self.cleaned_data.get("text"),
                    rating=self.cleaned_data.get("rating"),
                )
                return review
        else:
            # For commit=False, return unsaved instance
            review = super().save(commit=False)
            review.user = user
            review.product = product
            return review