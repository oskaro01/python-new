from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("chat/", views.chat_home, name="home"),
]

