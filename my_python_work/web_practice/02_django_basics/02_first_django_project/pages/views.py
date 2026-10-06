"""Views for simple website pages."""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from dictionary.models import Category, Word

from .forms import ImportWordsForm, WordForm
from .import_export import (
    csv_response,
    json_response,
    read_import_rows,
    row_bool,
    row_text,
)
from .database_schema import get_database_schema


logger = logging.getLogger(__name__)
STAFF_DASHBOARD_STATS_CACHE_KEY = "staff-dashboard-stats"
STAFF_DASHBOARD_STATS_TIMEOUT = 60


def clear_staff_dashboard_cache():
    cache.delete(STAFF_DASHBOARD_STATS_CACHE_KEY)


def get_staff_dashboard_stats():
    stats = cache.get(STAFF_DASHBOARD_STATS_CACHE_KEY)
    if stats is not None:
        return stats

    User = get_user_model()
    stats = {
        "total_words": Word.objects.count(),
        "total_categories": Category.objects.count(),
        "total_users": User.objects.count(),
        "users_with_words": User.objects.filter(words__isnull=False).distinct().count(),
        "orphan_words": Word.objects.filter(owner__isnull=True).count(),
    }
    cache.set(STAFF_DASHBOARD_STATS_CACHE_KEY, stats, STAFF_DASHBOARD_STATS_TIMEOUT)
    return stats


def home(request):
    context = {
        "title": "Home",
        "heading": "Hello From A Django Template",
        "message": "The pages app is now rendering an HTML template.",
        "lesson_points": [
            "urls.py matched the route.",
            "views.py prepared the context data.",
            "home.html displayed the page.",
            "base.html shared the layout.",
        ],
    }
    return render(request, "pages/home.html", context)


def about(request):
    context = {
        "title": "About",
        "heading": "About This Tiny Django Site",
        "message": "This page also uses the shared base template.",
    }
    return render(request, "pages/about.html", context)


@require_GET
def health_check(request):
    """Return a safe status response for Render and uptime checks."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        logger.exception("Health check failed.")
        return JsonResponse({"status": "unavailable"}, status=503)

    return JsonResponse({"status": "ok", "database": "ok"})


@permission_required("dictionary.view_all_words", raise_exception=True)
@require_GET
def database_explorer(request):
    try:
        schema = get_database_schema()
    except Exception:
        logger.exception("Database schema inspection failed.")
        return render(
            request,
            "pages/database_explorer.html",
            {
                "title": "Database Explorer",
                "schema_error": "The database schema could not be read right now.",
            },
            status=503,
        )

    return render(
        request,
        "pages/database_explorer.html",
        {
            "title": "Database Explorer",
            "schema": schema,
        },
    )


@login_required
def new_word(request):
    if request.method == "POST":
        form = WordForm(request.POST, user=request.user)

        if form.is_valid():
            form.instance.owner = request.user
            form.save()
            clear_staff_dashboard_cache()
            messages.success(request, "Word saved.")
            return redirect("pages:word_list")
    else:
        form = WordForm(user=request.user)

    context = {
        "title": "New Word",
        "heading": "Add A Dictionary Word",
        "message": "Save a word to your dictionary.",
        "form": form,
    }
    return render(request, "pages/word_form.html", context)


@login_required
def word_list(request, focus_only=False):
    words = Word.objects.select_related("category").filter(owner=request.user)
    query = request.GET.get("q", "").strip()

    if focus_only:
        words = words.filter(focus_first=True)
    if query:
        words = words.filter(
            Q(word__icontains=query)
            | Q(meaning__icontains=query)
            | Q(example__icontains=query)
        )
    words = words.order_by("-focus_first", "word")
    page = Paginator(words, 50).get_page(request.GET.get("page"))
    return render(request, "pages/word_list.html", {
        "title": "Words",
        "words": page,
        "query": query,
        "focus_only": focus_only,
    })


@login_required
def focus_first_list(request):
    return word_list(request, focus_only=True)


@login_required
def manage_words(request):
    words = Word.objects.select_related("category").filter(owner=request.user)
    query = request.GET.get("q", "").strip()

    if query:
        words = words.filter(
            Q(word__icontains=query)
            | Q(meaning__icontains=query)
            | Q(example__icontains=query)
        )

    page = Paginator(words.order_by("-focus_first", "word"), 50).get_page(
        request.GET.get("page")
    )
    return render(request, "pages/word_manage.html", {
        "title": "Manage words",
        "words": page,
        "query": query,
    })


@login_required
@require_POST
def bulk_word_action(request):
    selected_ids = request.POST.getlist("selected_words")
    action = request.POST.get("action", "")
    return_to = request.POST.get("return_to")
    redirect_name = (
        "pages:focus_first_list"
        if return_to == "focus"
        else "pages:manage_words"
        if return_to == "manage"
        else "pages:word_list"
    )

    if not selected_ids:
        messages.info(request, "Select at least one word first.")
        return redirect(redirect_name)

    words = Word.objects.filter(owner=request.user, pk__in=selected_ids)
    selected_count = words.count()

    if action == "focus":
        words.update(focus_first=True)
        messages.success(request, f"{selected_count} word(s) moved to Focus first.")
    elif action == "unfocus":
        words.update(focus_first=False)
        messages.success(request, f"{selected_count} word(s) removed from Focus first.")
    elif action == "delete":
        words.delete()
        clear_staff_dashboard_cache()
        messages.success(request, f"{selected_count} word(s) deleted.")
    else:
        messages.error(request, "Choose a valid bulk action.")

    return redirect(redirect_name)


@login_required
@require_GET
def export_words_csv(request):
    words = Word.objects.filter(owner=request.user).select_related("category")
    return csv_response(words)


@login_required
@require_GET
def export_words_json(request):
    words = Word.objects.filter(owner=request.user).select_related("category")
    return json_response(words)


@login_required
@require_http_methods(["GET", "POST"])
def import_words(request):
    form = ImportWordsForm(request.POST or None, request.FILES or None)
    result = None

    if request.method == "POST" and form.is_valid():
        try:
            rows = read_import_rows(form.cleaned_data["file"])
        except ValueError as error:
            form.add_error("file", str(error))
        else:
            existing_words = {
                value.casefold()
                for value in Word.objects.filter(owner=request.user).values_list("word", flat=True)
            }
            imported_words = set()
            errors = []
            imported = 0
            duplicates = 0
            invalid = 0

            for row_number, row in enumerate(rows, start=2):
                word_value = row_text(row, "word")
                normalized_word = word_value.casefold()

                if not word_value:
                    invalid += 1
                    errors.append(f"Row {row_number}: word is required.")
                    continue

                if normalized_word in existing_words or normalized_word in imported_words:
                    duplicates += 1
                    continue

                word_form = WordForm(
                    {
                        "word": word_value,
                        "meaning": row_text(row, "meaning"),
                        "example": row_text(row, "example"),
                        "category_name": row_text(row, "category", "category_name"),
                        "focus_first": row_bool(row, "focus_first"),
                    },
                    user=request.user,
                )

                if word_form.is_valid():
                    word_form.instance.owner = request.user
                    word_form.save()
                    clear_staff_dashboard_cache()
                    imported_words.add(normalized_word)
                    imported += 1
                else:
                    invalid += 1
                    error_text = "; ".join(
                        f"{field}: {', '.join(errors)}"
                        for field, errors in word_form.errors.items()
                    )
                    errors.append(f"Row {row_number}: {error_text}")

            result = {
                "imported": imported,
                "duplicates": duplicates,
                "invalid": invalid,
                "errors": errors[:5],
            }

    return render(request, "pages/word_import.html", {
        "title": "Import Words",
        "form": form,
        "result": result,
    })


@login_required
def word_detail(request, word_id):
    word = get_object_or_404(
        Word.objects.select_related("category"),
        pk=word_id,
        owner=request.user,
    )
    return render(request, "pages/word_detail.html", {"title": word.word, "word": word})


@login_required
def edit_word(request, word_id):
    word = get_object_or_404(Word, pk=word_id, owner=request.user)

    if request.method == "POST":
        form = WordForm(request.POST, instance=word, user=request.user)
        if form.is_valid():
            form.save()
            clear_staff_dashboard_cache()
            messages.success(request, "Word updated.")
            return redirect("pages:word_detail", word_id=word.pk)
    else:
        form = WordForm(instance=word, user=request.user)

    return render(request, "pages/word_form.html", {
        "title": "Edit Word",
        "heading": f"Edit {word.word}",
        "message": "Update this dictionary entry.",
        "form": form,
    })


@login_required
def delete_word(request, word_id):
    word = get_object_or_404(Word, pk=word_id, owner=request.user)

    if request.method == "POST":
        word.delete()
        clear_staff_dashboard_cache()
        messages.success(request, "Word deleted.")
        return redirect("pages:word_list")

    return render(request, "pages/word_confirm_delete.html", {
        "title": "Delete Word",
        "word": word,
    })


@permission_required("dictionary.view_all_words", raise_exception=True)
def staff_dashboard(request):
    User = get_user_model()
    stats = get_staff_dashboard_stats()
    recent_words = Word.objects.select_related("owner", "category").order_by("-created_at")[:8]
    top_categories = (
        Category.objects.annotate(word_count=Count("words"))
        .filter(word_count__gt=0)
        .order_by("-word_count", "name")[:5]
    )
    top_users = (
        User.objects.annotate(word_count=Count("words"))
        .filter(word_count__gt=0)
        .order_by("-word_count", "username")[:5]
    )

    return render(request, "pages/staff_dashboard.html", {
        "title": "Staff Dashboard",
        **stats,
        "recent_words": recent_words,
        "top_categories": top_categories,
        "top_users": top_users,
    })


def page_not_found(request, exception):
    logger.warning("404 page not found: %s", request.path)
    return render(request, "pages/404.html", {"title": "Page Not Found"}, status=404)


def server_error(request):
    logger.error("500 server error: %s", request.path)
    return render(request, "pages/500.html", {"title": "Server Error"}, status=500)
