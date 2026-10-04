"""ASGI config for the mini checkout lab."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_checkout_lab.settings")

application = get_asgi_application()
