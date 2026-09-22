"""URLs owned by the pages app."""

from django.urls import path

from . import views


app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("words/", views.word_list, name="word_list"),
    path("words/new/", views.new_word, name="new_word"),
    path("words/<int:word_id>/", views.word_detail, name="word_detail"),
    path("words/<int:word_id>/edit/", views.edit_word, name="edit_word"),
]
