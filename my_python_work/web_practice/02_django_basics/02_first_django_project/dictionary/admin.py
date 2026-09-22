"""Admin setup for dictionary models."""

from django.contrib import admin

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "category", "is_favorite", "created_at")
    list_filter = ("category", "is_favorite")
    search_fields = ("word", "meaning", "example", "category")
    ordering = ("word",)

