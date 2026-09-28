from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm


@login_required
def account(request):
    return render(request, "accounts/account.html", {
        "title": "Account",
        "word_count": request.user.words.count(),
        "category_count": request.user.word_categories.count(),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect("pages:word_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. You are now logged in.")
            return redirect("pages:word_list")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"title": "Register", "form": form})
