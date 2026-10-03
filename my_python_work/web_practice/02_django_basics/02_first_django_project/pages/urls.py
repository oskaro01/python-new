"""URLs owned by the pages app."""

from django.urls import path

from . import views


app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("health/", views.health_check, name="health"),
    path("staff/database/", views.database_explorer, name="database_explorer"),
    path("words/", views.word_list, name="word_list"),
    path("words/new/", views.new_word, name="new_word"),
    path("words/import/", views.import_words, name="import_words"),
    path("words/export/csv/", views.export_words_csv, name="export_words_csv"),
    path("words/export/json/", views.export_words_json, name="export_words_json"),
    path("words/<int:word_id>/", views.word_detail, name="word_detail"),
    path("words/<int:word_id>/edit/", views.edit_word, name="edit_word"),
    path("words/<int:word_id>/delete/", views.delete_word, name="delete_word"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
]
