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
        self.assertContains(response, "Migration status")
        self.assertContains(response, "Applied migration history")
        self.assertContains(response, "0005_word_word_owner_word_idx_word_word_created_idx")
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
                "focus_first": "on",
            },
        )
        self.assertRedirects(create_response, reverse("pages:word_list"))

        new_word = Word.objects.get(word="vivid")
        self.assertEqual(new_word.owner, self.user)
        self.assertEqual(new_word.category, self.category)
        self.assertTrue(new_word.focus_first)

        edit_response = self.client.post(
            reverse("pages:edit_word", args=[new_word.pk]),
            {
                "word": "vivid",
                "meaning": "bright and lively",
                "example": "The colors were vivid.",
                "category_name": "adjective",
                "focus_first": "on",
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

    def test_word_list_shows_fifty_words_per_page(self):
        Word.objects.bulk_create(
            [
                Word(owner=self.user, word=f"word-{number:02d}")
                for number in range(50)
            ]
        )
        self.login_user()

        first_page = self.client.get(reverse("pages:word_list"))
        second_page = self.client.get(reverse("pages:word_list"), {"page": 2})

        self.assertEqual(len(first_page.context["words"]), 50)
        self.assertEqual(len(second_page.context["words"]), 1)

    def test_focus_first_words_are_listed_before_regular_words(self):
        Word.objects.create(owner=self.user, word="zebra", focus_first=True)
        self.login_user()

        response = self.client.get(reverse("pages:word_list"))
        listed_words = [entry.word for entry in response.context["words"]]

        self.assertEqual(listed_words[0], "zebra")

    def test_focus_first_page_shows_only_focused_words(self):
        Word.objects.create(owner=self.user, word="daily", focus_first=True)
        self.login_user()

        response = self.client.get(reverse("pages:focus_first_list"))

        self.assertContains(response, "daily")
        self.assertContains(response, "Focus first")
        self.assertNotContains(response, "serene")

    def test_words_page_links_to_focus_first_page(self):
        self.login_user()

        response = self.client.get(reverse("pages:word_list"))

        self.assertContains(response, reverse("pages:focus_first_list"))

    def test_word_pages_do_not_show_bulk_checkboxes(self):
        self.login_user()

        words_response = self.client.get(reverse("pages:word_list"))
        focus_response = self.client.get(reverse("pages:focus_first_list"))

        self.assertNotContains(words_response, 'name="selected_words"')
        self.assertNotContains(focus_response, 'name="selected_words"')

    def test_manage_page_contains_bulk_controls(self):
        self.login_user()

        response = self.client.get(reverse("pages:manage_words"))

        self.assertContains(response, "Manage words")
        self.assertContains(response, 'name="selected_words"')
        self.assertContains(response, "Delete selected")

    def test_bulk_focus_only_changes_the_current_users_words(self):
        self.login_user()

        response = self.client.post(
            reverse("pages:bulk_word_action"),
            {
                "action": "focus",
                "selected_words": [self.own_word.pk, self.other_word.pk],
                "return_to": "focus",
            },
        )

        self.assertRedirects(response, reverse("pages:focus_first_list"))
        self.own_word.refresh_from_db()
        self.other_word.refresh_from_db()
        self.assertTrue(self.own_word.focus_first)
        self.assertFalse(self.other_word.focus_first)

    def test_bulk_delete_only_removes_the_current_users_words(self):
        self.login_user()

        self.client.post(
            reverse("pages:bulk_word_action"),
            {
                "action": "delete",
                "selected_words": [self.own_word.pk, self.other_word.pk],
            },
        )

        self.assertFalse(Word.objects.filter(pk=self.own_word.pk).exists())
        self.assertTrue(Word.objects.filter(pk=self.other_word.pk).exists())


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
        self.assertIn("word,meaning,example,category,focus_first", content)
        self.assertIn("serene", content)
        self.assertNotIn("private-word", content)

    def test_json_export_contains_only_current_users_words(self):
        response = self.client.get(reverse("pages:export_words_json"))
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["word"], "serene")
        self.assertFalse(data[0]["focus_first"])

    def test_import_page_shows_json_structure_example(self):
        response = self.client.get(reverse("pages:import_words"))

        self.assertContains(response, "JSON structure")
        self.assertContains(response, '"focus_first": true')

    def test_json_import_assigns_owner_and_skips_duplicate(self):
        content = json.dumps(
            [
                {"word": "serene", "meaning": "changed"},
                {
                    "word": "stern",
                    "meaning": "serious",
                    "category": "adjective",
                    "focus_first": True,
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
        self.assertTrue(imported_word.focus_first)


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
