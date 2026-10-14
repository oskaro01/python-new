from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import Conversation, FriendRequest, Friendship, Profile


class FriendRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.sender = User.objects.create_user(username="sender", first_name="Alice")
        cls.recipient = User.objects.create_user(username="recipient", first_name="Bob")
        cls.outsider = User.objects.create_user(username="outsider")
        cls.request = FriendRequest.objects.create(from_user=cls.sender, to_user=cls.recipient)

    def respond(self, action):
        return self.client.post(
            reverse("chat:respond_friend_request", args=[self.request.pk]),
            {"action": action}, HTTP_ACCEPT="application/json",
        )

    def test_search_distinguishes_sender_and_recipient(self):
        self.client.force_login(self.sender)
        result = self.client.get(reverse("chat:search_users"), {"q": "Bob"}).json()["users"][0]
        self.assertEqual(result["status"], "pending")
        self.client.force_login(self.recipient)
        result = self.client.get(reverse("chat:search_users"), {"q": "Alice"}).json()["users"][0]
        self.assertEqual(result["status"], "incoming")
        self.assertEqual(result["request_id"], self.request.pk)

    def test_accept_creates_one_friendship_and_can_start_chat(self):
        self.client.force_login(self.recipient)
        self.assertEqual(self.respond("accept").json()["status"], "friends")
        self.assertEqual(self.respond("accept").status_code, 200)
        self.assertEqual(Friendship.objects.count(), 1)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, FriendRequest.Status.ACCEPTED)
        self.assertIsNotNone(self.request.responded_at)
        url = reverse("chat:start_conversation", args=[self.sender.pk])
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first.url, second.url)
        self.assertEqual(Conversation.objects.count(), 1)

    def test_decline_does_not_create_friendship(self):
        self.client.force_login(self.recipient)
        self.assertEqual(self.respond("decline").status_code, 200)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, FriendRequest.Status.DECLINED)
        self.assertFalse(Friendship.objects.exists())
        self.respond("accept")
        self.assertFalse(Friendship.objects.exists())

    def test_only_recipient_can_respond(self):
        for user in [self.sender, self.outsider]:
            self.client.force_login(user)
            self.assertEqual(self.respond("accept").status_code, 404)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, FriendRequest.Status.PENDING)

    def test_response_requires_post_csrf_and_valid_action(self):
        url = reverse("chat:respond_friend_request", args=[self.request.pk])
        self.client.force_login(self.recipient)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.respond("unexpected").status_code, 400)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.recipient)
        self.assertEqual(csrf_client.post(url, {"action": "accept"}).status_code, 403)

    def test_add_does_not_create_reverse_pending_request(self):
        self.client.force_login(self.recipient)
        response = self.client.post(
            reverse("chat:send_friend_request", args=[self.sender.pk]),
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.json()["status"], "incoming")
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_incoming_controls_render_with_and_without_search(self):
        self.client.force_login(self.recipient)
        for params in [{}, {"q": "Alice"}]:
            response = self.client.get(reverse("chat:home"), params)
            self.assertContains(response, 'value="accept"')
            self.assertContains(response, 'value="decline"')

    def test_chat_search_filters_existing_conversations_and_friends(self):
        self.client.force_login(self.recipient)
        self.respond("accept")
        thread = Conversation.objects.create()
        thread.participants.create(user=self.sender)
        thread.participants.create(user=self.recipient)
        unrelated = Conversation.objects.create()
        unrelated.participants.create(user=self.outsider)
        unrelated.participants.create(user=self.recipient)
        response = self.client.get(reverse("chat:home"), {"chat_q": "ali"})
        self.assertEqual([c.pk for c in response.context["conversations"]], [thread.pk])
        self.assertEqual(list(response.context["friends"]), [self.sender])
        response = self.client.get(reverse("chat:conversation_detail", args=[thread.pk]))
        self.assertContains(response, 'id="conversation-search"')
        self.assertContains(response, 'id="topbar-user-search"')

    def test_normal_forms_redirect_instead_of_showing_json(self):
        self.client.force_login(self.recipient)
        response = self.client.post(
            reverse("chat:respond_friend_request", args=[self.request.pk]), {"action": "accept"},
        )
        self.assertRedirects(response, reverse("chat:home"))
        response = self.client.get(reverse("chat:home"), {"q": "Alice"})
        self.assertContains(response, reverse("chat:start_conversation", args=[self.sender.pk]))

    def test_profile_menu_and_settings_update_picture(self):
        self.client.force_login(self.sender)
        response = self.client.get(reverse("chat:profile"))
        self.assertContains(response, "Profile settings")
        picture = SimpleUploadedFile("alice.png", b"fake image bytes", content_type="image/png")
        response = self.client.post(
            reverse("chat:profile"),
            {"profile_picture": picture},
        )
        self.assertRedirects(response, reverse("chat:home"))
        profile = Profile.objects.get(user=self.sender)
        self.assertTrue(profile.profile_picture.name.endswith("alice.png"))
        response = self.client.get(reverse("chat:home"))
        self.assertContains(response, "sender")
        profile.profile_picture.delete(save=False)

    def test_profile_rejects_non_image_uploads(self):
        self.client.force_login(self.sender)
        picture = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")
        response = self.client.post(
            reverse("chat:profile"),
            {"profile_picture": picture},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Choose an image file.")
