import logging

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


class RegisterForm(UserCreationForm):
    """Django's secure registration form with clearer help text."""

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = "Letters, numbers, and @/./+/-/_ only."


class LoggedPasswordResetForm(PasswordResetForm):
    """Log safe password-reset checkpoints for production debugging."""

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        users = list(self.get_users(email))
        email_domain = email.rsplit("@", 1)[-1] if "@" in email else "unknown"

        logger.info(
            "Password reset requested for email domain %s: %s eligible user(s).",
            email_domain,
            len(users),
        )

        result = super().save(*args, **kwargs)

        if users:
            logger.info("Password reset email send call finished without SMTP error.")

        return result
