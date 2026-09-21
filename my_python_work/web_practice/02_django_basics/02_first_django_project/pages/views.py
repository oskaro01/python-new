"""Views for simple website pages."""

from django.shortcuts import render


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

