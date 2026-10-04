"""WSGI config for the mini checkout lab."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_checkout_lab.settings")

application = get_wsgi_application()
