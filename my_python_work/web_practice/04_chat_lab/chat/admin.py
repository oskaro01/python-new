from django.contrib import admin

from .models import Conversation, ConversationParticipant, FriendRequest, Friendship, Message, MessageAttachment, Profile

admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(Friendship)
admin.site.register(FriendRequest)
admin.site.register(Profile)
admin.site.register(MessageAttachment)

