from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("chat/", views.chat_home, name="home"),
    path("chat/users/<int:user_id>/start/", views.start_conversation, name="start_conversation"),
    path("chat/conversations/<int:conversation_id>/", views.conversation_detail, name="conversation_detail"),
]

