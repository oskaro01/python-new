"""Forms for the checkout learning workflow."""

from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=30, required=False, label="Phone")
    shipping_address = forms.CharField(max_length=200, label="Shipping address")
    shipping_city = forms.CharField(max_length=100, label="City")
    shipping_postal_code = forms.CharField(max_length=20, label="Postal code")
    shipping_country = forms.CharField(max_length=80, label="Country")
    notes = forms.CharField(
        required=False,
        label="Order notes",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
