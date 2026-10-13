from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Write a message..."}
            )
        }

    def clean_body(self):
        body = self.cleaned_data["body"].strip()
        if not body:
            raise forms.ValidationError("Message cannot be empty.")
        return body


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
