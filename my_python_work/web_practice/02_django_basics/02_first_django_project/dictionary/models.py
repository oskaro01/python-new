"""Database models for dictionary features."""

from django.conf import settings
from django.db import models


class Category(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="word_categories",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="unique_owner_category"),
        ]

    def __str__(self):
        return self.name


class Word(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="words",
        null=True,
        blank=True,
    )
    word = models.CharField(max_length=80)
    meaning = models.TextField(blank=True)
    example = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="words",
        null=True,
        blank=True,
    )
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["word"]
        permissions = [
            ("view_all_words", "Can view all dictionary words"),
        ]
        indexes = [
            models.Index(fields=["owner", "word"], name="word_owner_word_idx"),
            models.Index(fields=["-created_at"], name="word_created_idx"),
        ]

    def __str__(self):
        return self.word
