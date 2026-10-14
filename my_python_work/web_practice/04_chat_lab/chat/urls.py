from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("chat/", views.chat_home, name="home"),
    path("chat/profile/", views.profile_settings, name="profile"),
    path("chat/users/<int:user_id>/start/", views.start_conversation, name="start_conversation"),
    path("chat/users/search/", views.search_users, name="search_users"),
    path("chat/users/<int:user_id>/request/", views.send_friend_request, name="send_friend_request"),
    path("chat/requests/<int:request_id>/respond/", views.respond_friend_request, name="respond_friend_request"),
    path("chat/conversations/<int:conversation_id>/", views.conversation_detail, name="conversation_detail"),
]

