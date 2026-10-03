import logging

from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template import loader


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

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject,
            body,
            from_email,
            [to_email],
        )
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        recipient_domain = to_email.rsplit("@", 1)[-1] if "@" in to_email else "unknown"
        try:
            sent_count = email_message.send()
        except Exception as exc:
            logger.error(
                "Password reset SMTP send failed for %s (%s).",
                recipient_domain,
                type(exc).__name__,
                exc_info=True,
            )
            return

        logger.info(
            "Password reset SMTP send returned %s message(s) for %s.",
            sent_count,
            recipient_domain,
        )

    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        users = list(self.get_users(email))
        email_domain = email.rsplit("@", 1)[-1] if "@" in email else "unknown"

        logger.info(
            "Password reset requested for email domain %s: %s eligible user(s).",
            email_domain,
            len(users),
        )

        return super().save(*args, **kwargs)
