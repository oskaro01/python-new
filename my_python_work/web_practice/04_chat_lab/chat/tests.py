import base64
import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Conversation, FriendRequest, Friendship, Message, MessageAttachment, Profile, UserBlock


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

    def test_authenticated_users_can_view_profile_picture(self):
        self.client.force_login(self.sender)
        profile = Profile.objects.get(user=self.sender)
        picture = SimpleUploadedFile("alice.png", b"fake image bytes", content_type="image/png")
        profile.profile_picture.save("alice.png", picture, save=True)
        response = self.client.get(profile.profile_picture.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
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

    def test_profile_storage_error_is_shown_as_form_error(self):
        self.client.force_login(self.sender)
        picture = SimpleUploadedFile("alice.png", b"fake image bytes", content_type="image/png")
        with patch("django.core.files.storage.FileSystemStorage._save", side_effect=OSError):
            response = self.client.post(reverse("chat:profile"), {"profile_picture": picture})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Profile picture storage is unavailable right now.")

    def test_unexpected_profile_save_error_is_shown_as_form_error(self):
        self.client.force_login(self.sender)
        picture = SimpleUploadedFile("alice.png", b"fake image bytes", content_type="image/png")
        with patch("django.core.files.storage.FileSystemStorage._save", side_effect=RuntimeError):
            response = self.client.post(reverse("chat:profile"), {"profile_picture": picture})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "We could not save this profile picture right now.")

    def test_delete_account_requires_password_and_confirmation(self):
        user = get_user_model().objects.create_user(username="deletable", password="correct-password")
        self.client.force_login(user)
        url = reverse("chat:delete_account")

        response = self.client.post(url, {"password": "wrong-password", "confirm": "on"})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())

        response = self.client.post(url, {"password": "correct-password"})
        self.assertEqual(response.status_code, 400)
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())

        response = self.client.post(url, {"password": "correct-password", "confirm": "on"})
        self.assertRedirects(response, reverse("chat:landing"))
        self.assertFalse(get_user_model().objects.filter(pk=user.pk).exists())

    def test_blocked_person_can_be_unblocked_from_profile_settings(self):
        UserBlock.objects.create(blocker=self.sender, blocked=self.outsider)
        self.client.force_login(self.sender)
        page = self.client.get(reverse("chat:profile"))
        self.assertContains(page, "outsider")

        response = self.client.post(reverse("chat:unblock_user", args=[self.outsider.pk]))
        self.assertRedirects(response, reverse("chat:profile"))
        self.assertFalse(UserBlock.objects.filter(blocker=self.sender, blocked=self.outsider).exists())


class MessageAttachmentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_media_root = tempfile.mkdtemp(prefix="chat-private-media-")
        cls.media_override = override_settings(PRIVATE_MEDIA_ROOT=cls.private_media_root)
        cls.media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.media_override.disable()
        shutil.rmtree(cls.private_media_root, ignore_errors=True)

    @staticmethod
    def image_upload(name="photo.png"):
        image_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        return SimpleUploadedFile(name, image_bytes, content_type="image/png")

    def setUp(self):
        self.sender = get_user_model().objects.create_user(username="sender")
        self.recipient = get_user_model().objects.create_user(username="recipient")
        self.outsider = get_user_model().objects.create_user(username="outsider")
        self.conversation = Conversation.objects.create()
        self.conversation.participants.create(user=self.sender)
        self.conversation.participants.create(user=self.recipient)
        self.url = reverse("chat:conversation_detail", args=[self.conversation.pk])
        self.client.force_login(self.sender)

    def test_small_image_is_saved_outside_database_and_rendered_through_protected_url(self):
        response = self.client.post(
            self.url,
            {"body": "Look at this", "attachment": self.image_upload()},
        )

        self.assertRedirects(response, self.url)
        message = Message.objects.get(conversation=self.conversation)
        attachment = MessageAttachment.objects.get(message=message)
        self.assertEqual(attachment.original_name, "photo.png")
        self.assertEqual(attachment.content_type, "image/png")
        self.assertGreater(attachment.size_bytes, 0)
        self.assertTrue(attachment.file.name.startswith("chat_attachments/"))
        self.assertTrue(attachment.file.storage.exists(attachment.file.name))
        with self.assertRaises(ValueError):
            attachment.file.url

        page = self.client.get(self.url)
        self.assertContains(page, reverse("chat:attachment_file", args=[attachment.pk]))
        self.assertNotContains(page, "/media/")

    def test_image_only_message_is_allowed(self):
        response = self.client.post(self.url, {"attachment": self.image_upload()})

        self.assertRedirects(response, self.url)
        self.assertEqual(Message.objects.filter(conversation=self.conversation).count(), 1)
        self.assertEqual(MessageAttachment.objects.count(), 1)

    def test_attachment_upload_broadcasts_saved_message_metadata(self):
        with patch("chat.views._broadcast_message") as broadcast:
            response = self.client.post(
                self.url,
                {"body": "Look live", "attachment": self.image_upload()},
                HTTP_X_CHAT_ASYNC="1",
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertIsNotNone(response.json()["message_id"])
        self.assertTrue(broadcast.called)
        broadcasted_message = broadcast.call_args.args[0]
        self.assertEqual(broadcasted_message.conversation_id, self.conversation.pk)
        self.assertEqual(broadcasted_message.attachments.count(), 1)
        self.assertIn('data-message-id="', response.json()["html"])

    def test_text_only_message_still_works(self):
        response = self.client.post(self.url, {"body": "Just text"})

        self.assertRedirects(response, self.url)
        self.assertEqual(Message.objects.get().body, "Just text")
        self.assertFalse(MessageAttachment.objects.exists())

    def test_empty_message_without_image_is_rejected(self):
        response = self.client.post(self.url, {"body": "   "})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Write a message or attach an image.")
        self.assertFalse(Message.objects.exists())
        self.assertFalse(MessageAttachment.objects.exists())

    def test_text_file_disguised_as_image_is_rejected(self):
        upload = SimpleUploadedFile("not-image.png", b"plain text", content_type="image/png")

        response = self.client.post(self.url, {"attachment": upload})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The uploaded file is not a valid image.")
        self.assertFalse(Message.objects.exists())

    def test_oversized_image_is_rejected(self):
        upload = SimpleUploadedFile(
            "large.png",
            b"\x89PNG\r\n\x1a\n" + b"x" * (3 * 1024 * 1024),
            content_type="image/png",
        )

        response = self.client.post(self.url, {"attachment": upload})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Images must be 3 MB or smaller.")
        self.assertFalse(Message.objects.exists())

    def test_participants_can_preview_and_download_but_outsiders_cannot(self):
        self.client.post(self.url, {"attachment": self.image_upload()})
        attachment = MessageAttachment.objects.get()
        attachment_url = reverse("chat:attachment_file", args=[attachment.pk])

        preview = self.client.get(attachment_url)
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview["Content-Type"], "image/png")
        self.assertIn("inline", preview["Content-Disposition"])
        self.assertEqual(preview["X-Content-Type-Options"], "nosniff")

        self.client.force_login(self.recipient)
        download = self.client.get(f"{attachment_url}?download=1")
        self.assertEqual(download.status_code, 200)
        self.assertIn("attachment", download["Content-Disposition"])

        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(attachment_url).status_code, 404)

        anonymous = Client()
        self.assertEqual(anonymous.get(attachment_url).status_code, 302)
