"""URL routes for the tiny Django project."""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def home(request):
    return HttpResponse("Hello from Django. Your first Django route works.")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
]

