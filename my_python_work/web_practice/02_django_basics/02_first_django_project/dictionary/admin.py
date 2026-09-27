"""Admin setup for dictionary models."""

from django.contrib import admin

from .models import Category, Word


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")
    list_filter = ("owner",)
    search_fields = ("name", "owner__username")
    ordering = ("name",)


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "owner", "category", "is_favorite", "created_at")
    list_filter = ("owner", "category", "is_favorite")
    search_fields = ("word", "meaning", "example", "category__name", "owner__username")
    ordering = ("word",)

