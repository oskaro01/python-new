from django.conf import settings
from django.db import models


class Conversation(models.Model):
    is_self = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation {self.pk}"

    def display_name_for(self, user):
        other_users = [
            participant.user.get_username()
            for participant in self.participants.all()
            if participant.user_id != user.id
        ]
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
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message {self.pk} from {self.sender}"

