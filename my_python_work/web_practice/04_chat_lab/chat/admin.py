from django.contrib import admin

from .models import Conversation, ConversationParticipant, FriendRequest, Friendship, Message, MessageAttachment, Profile

admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(Friendship)
admin.site.register(FriendRequest)
admin.site.register(Profile)
@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "original_name", "created_at", "expires_at")
    list_filter = ("content_type",)
    search_fields = ("original_name",)

