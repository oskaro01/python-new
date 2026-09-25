"""Admin setup for dictionary models."""

from django.contrib import admin

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "owner", "category", "is_favorite", "created_at")
    list_filter = ("owner", "category", "is_favorite")
    search_fields = ("word", "meaning", "example", "category", "owner__username")
    ordering = ("word",)

