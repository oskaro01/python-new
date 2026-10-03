"""Django email backend for Resend's HTTPS API."""

import json
import logging
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """Send Django email messages through Resend instead of SMTP."""

    api_url = "https://api.resend.com/emails"

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, "RESEND_API_KEY", "").strip()
        self.from_email = getattr(settings, "RESEND_FROM_EMAIL", "").strip()
        self.timeout = getattr(settings, "EMAIL_TIMEOUT", 10)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key or not self.from_email:
            error = ImproperlyConfigured(
                "Set RESEND_API_KEY and RESEND_FROM_EMAIL when using "
                "ResendEmailBackend."
            )
            if self.fail_silently:
                logger.error("%s", error)
                return 0
            raise error

        sent_count = 0
        for email_message in email_messages:
            if self._send(email_message):
                sent_count += 1
        return sent_count

    def _send(self, email_message):
        recipients = email_message.recipients()
        if not recipients:
            return False

        payload = {
            "from": self.from_email,
            "to": recipients,
            "subject": str(email_message.subject),
            "text": email_message.body,
        }

        for alternative in getattr(email_message, "alternatives", []):
            if alternative.mimetype == "text/html":
                payload["html"] = alternative.content
                break

        for field_name in ("cc", "bcc"):
            addresses = getattr(email_message, field_name, [])
            if addresses:
                payload[field_name] = addresses

        request = Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "personal-dictionary/1.0",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            try:
                error_message = json.loads(response_body).get("message")
            except (TypeError, ValueError):
                error_message = response_body[:200]
            error = RuntimeError(
                f"Resend rejected the email ({exc.code}): {error_message}"
            )
            if self.fail_silently:
                logger.error("%s", error)
                return False
            raise error from exc

        logger.info(
            "Resend accepted email %s for %s recipient(s).",
            response_body.get("id", "unknown"),
            len(recipients),
        )
        return True
