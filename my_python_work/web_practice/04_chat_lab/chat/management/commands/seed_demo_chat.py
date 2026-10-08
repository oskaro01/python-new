from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from chat.models import Conversation, ConversationParticipant, Message


class Command(BaseCommand):
    help = "Create two local demo users and a conversation for learning."

    def handle(self, *args, **options):
        User = get_user_model()
        alice, _ = User.objects.get_or_create(username="alice")
        alice.set_password("alice-demo-password")
        alice.save()
        bob, _ = User.objects.get_or_create(username="bob")
        bob.set_password("bob-demo-password")
        bob.save()

        conversation, _ = Conversation.objects.get_or_create()
        ConversationParticipant.objects.get_or_create(conversation=conversation, user=alice)
        ConversationParticipant.objects.get_or_create(conversation=conversation, user=bob)
        if not conversation.messages.exists():
            Message.objects.create(
                conversation=conversation,
                sender=alice,
                body="Hey Bob, welcome to our chat lab!",
            )
            Message.objects.create(
                conversation=conversation,
                sender=bob,
                body="Hey Alice! It is working.",
            )

        self.stdout.write(self.style.SUCCESS("Demo chat ready."))
        self.stdout.write("alice / alice-demo-password")
        self.stdout.write("bob / bob-demo-password")
