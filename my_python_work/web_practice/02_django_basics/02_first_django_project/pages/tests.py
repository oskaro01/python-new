"""Tests for the dictionary's important user-facing rules."""

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError
from django.test import TestCase
from django.urls import reverse

from dictionary.models import Category, Word


User = get_user_model()


class HealthCheckTests(TestCase):
    def test_health_check_reports_database_status(self):
        response = self.client.get(reverse("pages:health"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"status": "ok", "database": "ok"},
        )

    @patch("pages.views.connection.cursor")
    def test_health_check_returns_503_when_database_fails(self, mock_cursor):
        mock_cursor.side_effect = DatabaseError("database unavailable")

        response = self.client.get(reverse("pages:health"))

        self.assertEqual(response.status_code, 503)
        self.assertJSONEqual(
            response.content,
            {"status": "unavailable"},
        )


class DatabaseExplorerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="schema-reader",
            password="test-password-123",
        )

    def test_database_explorer_requires_permission(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pages:database_explorer"))

        self.assertEqual(response.status_code, 403)

    def test_database_explorer_shows_live_schema_metadata(self):
        permission = Permission.objects.get(
            content_type__app_label="dictionary",
            codename="view_all_words",
        )
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        response = self.client.get(reverse("pages:database_explorer"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Database Explorer")
        self.assertContains(response, "dictionary_word")
        self.assertContains(response, "dictionary_category")
        self.assertContains(response, "Foreign-key map")
        self.assertContains(response, "word")


class WordAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ayzal",
            email="ayzal@example.com",
            password="test-password-123",
        )
        cls.other_user = User.objects.create_user(
            username="liebe",
            email="liebe@example.com",
            password="test-password-123",
        )
        cls.category = Category.objects.create(owner=cls.user, name="adjective")
        cls.own_word = Word.objects.create(
            owner=cls.user,
            word="serene",
            meaning="calm and peaceful",
            category=cls.category,
        )
        cls.other_word = Word.objects.create(
            owner=cls.other_user,
            word="stern",
            meaning="serious and unrelenting",
        )

    def login_user(self):
        self.client.force_login(self.user)

    def test_logged_out_user_is_redirected_from_words(self):
        response = self.client.get(reverse("pages:word_list"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('pages:word_list')}",
        )

    def test_user_sees_only_their_own_words(self):
        self.login_user()

        response = self.client.get(reverse("pages:word_list"))

        self.assertContains(response, "serene")
        self.assertNotContains(response, "stern")

    def test_user_cannot_open_another_users_word(self):
        self.login_user()

        response = self.client.get(
            reverse("pages:word_detail", args=[self.other_word.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_user_can_create_edit_and_delete_their_word(self):
        self.login_user()

        create_response = self.client.post(
            reverse("pages:new_word"),
            {
                "word": "vivid",
                "meaning": "full of life",
                "example": "The colors were vivid.",
                "category_name": "adjective",
            },
        )
        self.assertRedirects(create_response, reverse("pages:word_list"))

        new_word = Word.objects.get(word="vivid")
        self.assertEqual(new_word.owner, self.user)
        self.assertEqual(new_word.category, self.category)

        edit_response = self.client.post(
            reverse("pages:edit_word", args=[new_word.pk]),
            {
                "word": "vivid",
                "meaning": "bright and lively",
                "example": "The colors were vivid.",
                "category_name": "adjective",
            },
        )
        self.assertRedirects(
            edit_response,
            reverse("pages:word_detail", args=[new_word.pk]),
        )
        new_word.refresh_from_db()
        self.assertEqual(new_word.meaning, "bright and lively")

        delete_response = self.client.post(
            reverse("pages:delete_word", args=[new_word.pk])
        )
        self.assertRedirects(delete_response, reverse("pages:word_list"))
        self.assertFalse(Word.objects.filter(pk=new_word.pk).exists())

    def test_search_finds_meaning(self):
        self.login_user()

        response = self.client.get(reverse("pages:word_list"), {"q": "calm"})

        self.assertContains(response, "serene")
        self.assertNotContains(response, "stern")


class ImportExportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ayzal",
            email="ayzal@example.com",
            password="test-password-123",
        )
        cls.other_user = User.objects.create_user(
            username="liebe",
            email="liebe@example.com",
            password="test-password-123",
        )
        Word.objects.create(owner=cls.user, word="serene", meaning="calm")
        Word.objects.create(owner=cls.other_user, word="private-word")

    def setUp(self):
        self.client.force_login(self.user)

    def test_csv_export_contains_only_current_users_words(self):
        response = self.client.get(reverse("pages:export_words_csv"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("word,meaning,example,category", content)
        self.assertIn("serene", content)
        self.assertNotIn("private-word", content)

    def test_json_export_contains_only_current_users_words(self):
        response = self.client.get(reverse("pages:export_words_json"))
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["word"], "serene")

    def test_json_import_assigns_owner_and_skips_duplicate(self):
        content = json.dumps(
            [
                {"word": "serene", "meaning": "changed"},
                {
                    "word": "stern",
                    "meaning": "serious",
                    "category": "adjective",
                },
            ]
        ).encode("utf-8")
        upload = SimpleUploadedFile(
            "backup.json",
            content,
            content_type="application/json",
        )

        response = self.client.post(
            reverse("pages:import_words"),
            {"file": upload},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Imported: 1")
        self.assertContains(response, "Skipped duplicates: 1")
        imported_word = Word.objects.get(word="stern")
        self.assertEqual(imported_word.owner, self.user)
        self.assertEqual(imported_word.category.owner, self.user)


class PermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="liebe",
            email="liebe@example.com",
            password="test-password-123",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_user_without_dashboard_permission_gets_forbidden(self):
        response = self.client.get(reverse("pages:staff_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_group_permission_allows_staff_dashboard(self):
        permission = Permission.objects.get(
            content_type__app_label="dictionary",
            codename="view_all_words",
        )
        group = Group.objects.create(name="Dictionary Managers")
        group.permissions.add(permission)
        self.user.groups.add(group)

        response = self.client.get(reverse("pages:staff_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff Dashboard")


class AccountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="ayzal",
            email="ayzal@example.com",
            password="test-password-123",
        )

    def test_account_page_requires_login(self):
        response = self.client.get(reverse("accounts:account"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:account')}",
        )

    def test_logged_in_user_can_open_password_change_form(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:password_change"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Change password")
