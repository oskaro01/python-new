"""Forms for the checkout learning workflow."""

from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=30, required=False, label="Phone")
    notes = forms.CharField(
        required=False,
        label="Order notes",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
