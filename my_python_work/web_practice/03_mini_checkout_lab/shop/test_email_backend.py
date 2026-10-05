import json
from unittest.mock import Mock, patch

from django.core.mail import EmailMessage
from django.test import SimpleTestCase, override_settings

from .email_backend import ResendEmailBackend


class ResendEmailBackendTests(SimpleTestCase):
    @override_settings(
        RESEND_API_KEY="re_test_key",
        RESEND_FROM_EMAIL="receipts@example.com",
        EMAIL_TIMEOUT=3,
    )
    @patch("shop.email_backend.urlopen")
    def test_sends_expected_resend_payload(self, mocked_urlopen):
        response = Mock()
        response.read.return_value = b'{"id":"email_123"}'
        mocked_urlopen.return_value.__enter__.return_value = response
        mocked_urlopen.return_value.__exit__.return_value = None

        sent_count = ResendEmailBackend().send_messages(
            [
                EmailMessage(
                    subject="Receipt for Order #7",
                    body="Total: $12.50",
                    from_email="ignored@example.com",
                    to=["customer@example.com"],
                )
            ]
        )

        self.assertEqual(sent_count, 1)
        request = mocked_urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.headers["Authorization"], "Bearer re_test_key")
        self.assertEqual(payload["from"], "receipts@example.com")
        self.assertEqual(payload["to"], ["customer@example.com"])
        self.assertEqual(payload["subject"], "Receipt for Order #7")
        self.assertEqual(payload["text"], "Total: $12.50")
