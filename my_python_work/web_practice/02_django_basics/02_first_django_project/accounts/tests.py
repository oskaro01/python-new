import json
from unittest.mock import Mock, patch

from django.core import mail
from django.test import SimpleTestCase, override_settings

from .email_backend import ResendEmailBackend


class ResendEmailBackendTests(SimpleTestCase):
    @override_settings(
        RESEND_API_KEY="re_test_key",
        RESEND_FROM_EMAIL="onboarding@resend.dev",
        EMAIL_TIMEOUT=3,
    )
    @patch("accounts.email_backend.urlopen")
    def test_sends_email_as_resend_json(self, mocked_urlopen):
        response = Mock()
        response.read.return_value = b'{"id":"email_123"}'
        mocked_urlopen.return_value.__enter__.return_value = response
        mocked_urlopen.return_value.__exit__.return_value = None

        message = mail.EmailMessage(
            "Password reset",
            "Open this link.",
            "ignored@example.com",
            ["recipient@example.com"],
        )

        sent_count = ResendEmailBackend().send_messages([message])

        self.assertEqual(sent_count, 1)
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["from"], "onboarding@resend.dev")
        self.assertEqual(payload["to"], ["recipient@example.com"])
        self.assertEqual(payload["subject"], "Password reset")
        self.assertEqual(payload["text"], "Open this link.")
        self.assertEqual(
            request.headers["Authorization"],
            "Bearer re_test_key",
        )
