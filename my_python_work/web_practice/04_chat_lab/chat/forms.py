from django import forms
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Message, MessageReport, Profile


class MessageForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": "image/jpeg,image/png,image/webp"}
        ),
        help_text="JPEG, PNG, or WebP up to 3 MB.",
    )

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
        return body

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if not attachment:
            return None
        if attachment.size > 3 * 1024 * 1024:
            raise forms.ValidationError("Images must be 3 MB or smaller.")

        allowed_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        suffix = Path(attachment.name).suffix.lower()
        expected_type = allowed_types.get(suffix)
        if expected_type is None or attachment.content_type != expected_type:
            raise forms.ValidationError("Choose a JPEG, PNG, or WebP image.")

        header = attachment.read(12)
        attachment.seek(0)
        signatures = {
            ".jpg": header.startswith(b"\xff\xd8\xff"),
            ".jpeg": header.startswith(b"\xff\xd8\xff"),
            ".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
            ".webp": header.startswith(b"RIFF") and header[8:12] == b"WEBP",
        }
        if not signatures[suffix]:
            raise forms.ValidationError("The uploaded file is not a valid image.")
        return attachment

    def clean(self):
        cleaned_data = super().clean()
        body = (cleaned_data.get("body") or "").strip()
        attachment = cleaned_data.get("attachment")
        if not body and not attachment:
            raise forms.ValidationError("Write a message or attach an image.")
        cleaned_data["body"] = body
        return cleaned_data


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["profile_picture"]

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture and picture.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile pictures must be 5 MB or smaller.")
        content_type = getattr(picture, "content_type", "") or ""
        if picture and not content_type.startswith("image/"):
            raise forms.ValidationError("Choose an image file.")
        return picture


class AccountDeletionForm(forms.Form):
    password = forms.CharField(
        label="Current password",
        strip=False,
        widget=forms.PasswordInput,
    )
    confirm = forms.BooleanField(
        label="I understand that this permanently deletes my account.",
    )

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError("The password is incorrect.")
        return password


class MessageReportForm(forms.ModelForm):
    class Meta:
        model = MessageReport
        fields = ["reason"]
