"""Database models for dictionary features."""

from django.conf import settings
from django.db import models


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
    category = models.CharField(max_length=60, blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["word"]

    def __str__(self):
        return self.word

