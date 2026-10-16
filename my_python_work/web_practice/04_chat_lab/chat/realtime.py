"""Small, user-independent payloads shared by HTTP and WebSocket delivery."""

from django.urls import reverse


def message_payload(message):
    """Build the metadata needed to render one live message safely."""

    attachments = []
    for attachment in message.attachments.all():
        url = reverse("chat:attachment_file", args=[attachment.pk])
        attachments.append(
            {
                "url": url,
                "download_url": f"{url}?download=1",
                "original_name": attachment.original_name,
                "content_type": attachment.content_type,
            }
        )
    return {
        "type": "message",
        "message_id": message.pk,
        "conversation_id": message.conversation_id,
        "sender_id": message.sender_id,
        "sender_name": message.sender.get_username(),
        "body": message.body,
        "attachments": attachments,
        "created_at": message.created_at.isoformat(),
        "expires_at": int(message.expires_at.timestamp()),
    }
