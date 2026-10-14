from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from .storage import PrivateAttachmentStorage


private_attachment_storage = PrivateAttachmentStorage()


def chat_attachment_upload_to(instance, filename):
    """Generate a non-guessable private path while retaining the file type."""

    from pathlib import Path
    from uuid import uuid4

    suffix = Path(filename).suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".img"
    return f"chat_attachments/{uuid4().hex}{suffix}"


def default_attachment_expiry():
    """Give each attachment a short, configurable lifetime."""

    from datetime import timedelta

    return timezone.now() + timedelta(days=settings.CHAT_ATTACHMENT_TTL_DAYS)


def default_message_expiry():
    """Store the deadline once; reading a message never extends its lifetime."""

    from datetime import timedelta

    return timezone.now() + timedelta(seconds=settings.CHAT_MESSAGE_TTL_SECONDS)


class Friendship(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friendships")
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friendships_received")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "friend"], name="unique_friendship"),
            models.CheckConstraint(condition=~Q(user=models.F("friend")), name="friendship_users_differ"),
        ]

    def __str__(self):
        return f"{self.user} and {self.friend}"


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user"],
                condition=Q(status="pending"),
                name="unique_pending_friend_request",
            ),
            models.CheckConstraint(condition=~Q(from_user=models.F("to_user")), name="friend_request_users_differ"),
        ]

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.FileField(upload_to="uploads/profile_pictures/", blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user}"

    @property
    def avatar_url(self):
        return self.profile_picture.url if self.profile_picture else ""


class Conversation(models.Model):
    is_self = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.pk}"

    def display_name_for(self, user):
        other_users = []
        for participant in self.participants.all():
            if participant.user_id == user.id:
                continue
            other_users.append(participant.user.get_full_name() or participant.user.get_username())
        return ", ".join(other_users) if other_users else f"{user.get_username()} (You)"


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_participations")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["conversation", "user"], name="unique_conversation_participant")]

    def __str__(self):
        return f"{self.user} in {self.conversation}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_message_expiry, db_index=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message {self.pk} from {self.sender}"


class MessageAttachment(models.Model):
    """A small image stored outside the database and owned by one message."""

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        storage=private_attachment_storage,
        upload_to=chat_attachment_upload_to,
    )
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_attachment_expiry, db_index=True)

    class Meta:
        ordering = ("created_at", "pk")

    def __str__(self):
        return f"Attachment {self.pk} for message {self.message_id}"

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

