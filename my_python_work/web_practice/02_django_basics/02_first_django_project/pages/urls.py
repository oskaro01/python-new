"""URLs owned by the pages app."""

from django.urls import path

from . import views


app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("words/new/", views.new_word, name="new_word"),
]
