"""Forms for the checkout learning workflow."""

from django import forms

from .shipping import shipping_choices


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=30, required=False, label="Phone")
    shipping_address = forms.CharField(max_length=200, label="Shipping address")
    shipping_city = forms.CharField(max_length=100, label="City")
    shipping_postal_code = forms.CharField(max_length=20, label="Postal code")
    shipping_country = forms.CharField(max_length=80, label="Country")
    shipping_method = forms.ChoiceField(
        choices=(),
        label="Shipping method",
        required=False,
    )
    notes = forms.CharField(
        required=False,
        label="Order notes",
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def __init__(self, *args, requires_shipping=True, **kwargs):
        super().__init__(*args, **kwargs)
        if requires_shipping:
            self.fields["shipping_method"].choices = [
                ("", "Choose a shipping method")
            ] + shipping_choices()
            self.fields["shipping_method"].required = True
        else:
            self.fields["shipping_method"].choices = [
                ("", "No shipping required")
            ]
        if not requires_shipping:
            for field_name in (
                "shipping_address",
                "shipping_city",
                "shipping_postal_code",
                "shipping_country",
            ):
                self.fields[field_name].required = False
                self.fields[field_name].label += " (optional for digital items)"
