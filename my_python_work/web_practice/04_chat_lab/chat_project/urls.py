from django.contrib import admin
from django.urls import include, path
from chat.views import signup

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/signup/", signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("chat.urls")),
]

