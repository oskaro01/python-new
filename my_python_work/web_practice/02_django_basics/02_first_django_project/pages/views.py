"""Views for simple website pages."""

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from dictionary.models import Word

from .forms import WordForm


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


@login_required
def new_word(request):
    if request.method == "POST":
        form = WordForm(request.POST)

        if form.is_valid():
            word = form.save(commit=False)
            word.owner = request.user
            word.save()
            messages.success(request, "Word saved.")
            return redirect("pages:word_list")
    else:
        form = WordForm()

    context = {
        "title": "New Word",
        "heading": "Add A Dictionary Word",
        "message": "Save a word to your dictionary.",
        "form": form,
    }
    return render(request, "pages/word_form.html", context)


@login_required
def word_list(request):
    words = Word.objects.filter(owner=request.user)
    query = request.GET.get("q", "").strip()

    if query:
        words = words.filter(
            Q(word__icontains=query)
            | Q(meaning__icontains=query)
            | Q(example__icontains=query)
        )
    page = Paginator(words, 5).get_page(request.GET.get("page"))
    return render(request, "pages/word_list.html", {
        "title": "Words",
        "words": page,
        "query": query,
    })


@login_required
def word_detail(request, word_id):
    word = get_object_or_404(Word, pk=word_id, owner=request.user)
    return render(request, "pages/word_detail.html", {"title": word.word, "word": word})


@login_required
def edit_word(request, word_id):
    word = get_object_or_404(Word, pk=word_id, owner=request.user)

    if request.method == "POST":
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            messages.success(request, "Word updated.")
            return redirect("pages:word_detail", word_id=word.pk)
    else:
        form = WordForm(instance=word)

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
        messages.success(request, "Word deleted.")
        return redirect("pages:word_list")

    return render(request, "pages/word_confirm_delete.html", {
        "title": "Delete Word",
        "word": word,
    })
