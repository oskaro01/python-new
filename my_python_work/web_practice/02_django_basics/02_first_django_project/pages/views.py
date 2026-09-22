"""Views for simple website pages."""

from django.shortcuts import render

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


def new_word(request):
    submitted_word = None

    if request.method == "POST":
        form = WordForm(request.POST)

        if form.is_valid():
            submitted_word = form.cleaned_data
    else:
        form = WordForm()

    context = {
        "title": "New Word",
        "heading": "Add A Dictionary Word",
        "message": "This form validates the word data but does not save it yet.",
        "form": form,
        "submitted_word": submitted_word,
    }
    return render(request, "pages/word_form.html", context)
