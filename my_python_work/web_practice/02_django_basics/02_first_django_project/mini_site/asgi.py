"""ASGI entry point for async-capable web servers."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mini_site.settings")

application = get_asgi_application()

