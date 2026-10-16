from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import Q
from django.utils import timezone

from .models import Conversation, Message, UserBlock
from .realtime import message_payload


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    """Broadcast short text messages to the authorized conversation group."""

    async def connect(self):
        self.conversation_id = int(self.scope["url_route"]["kwargs"]["conversation_id"])
        self.group_name = f"chat_conversation_{self.conversation_id}"

        if not await self.can_access_conversation():
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        self.user_group_name = f"user_notifications_{self.scope['user'].pk}"
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "ready"})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        body = str(content.get("body", "")).strip()
        if not body:
            await self.send_json({"type": "error", "error": "Message cannot be empty."})
            return
        if len(body) > 5000:
            await self.send_json({"type": "error", "error": "Message is too long."})
            return

        result = await self.create_message(body)
        if result is None:
            await self.close(code=4403)
            return
        payload, recipient_ids = result

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "payload": payload},
        )
        for recipient_id in recipient_ids:
            await self.channel_layer.group_send(
                f"user_notifications_{recipient_id}",
                {
                    "type": "chat.notification",
                    "payload": {**payload, "type": "notification"},
                },
            )

    async def chat_message(self, event):
        await self.send_json(event["payload"])

    async def chat_notification(self, event):
        await self.send_json(event["payload"])

    @database_sync_to_async
    def can_access_conversation(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return False
        conversation = Conversation.objects.filter(
            pk=self.conversation_id,
            participants__user=user,
        ).first()
        if conversation is None:
            return False
        other_ids = conversation.participants.exclude(user=user).values_list("user_id", flat=True)
        return not UserBlock.objects.filter(
            Q(blocker=user, blocked_id__in=other_ids)
            | Q(blocked=user, blocker_id__in=other_ids)
        ).exists()

    @database_sync_to_async
    def create_message(self, body):
        user = self.scope["user"]
        conversation = Conversation.objects.filter(
            pk=self.conversation_id,
            participants__user=user,
        ).first()
        if conversation is None:
            return None

        other_ids = conversation.participants.exclude(user=user).values_list("user_id", flat=True)
        if UserBlock.objects.filter(
            Q(blocker=user, blocked_id__in=other_ids)
            | Q(blocked=user, blocker_id__in=other_ids)
        ).exists():
            return None

        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            body=body,
        )
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=["updated_at"])
        recipient_ids = list(
            conversation.participants.exclude(user=user).values_list("user_id", flat=True)
        )
        return message_payload(message), recipient_ids


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Deliver a user's incoming chat notifications on every authenticated page."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        self.user_group_name = f"user_notifications_{user.pk}"
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "ready"})

    async def disconnect(self, close_code):
        if hasattr(self, "user_group_name"):
            await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def chat_notification(self, event):
        await self.send_json(event["payload"])
