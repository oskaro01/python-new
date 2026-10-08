from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def landing(request):
    return render(request, "chat/landing.html")

@login_required
def chat_home(request):
    return render(request, "chat/home.html")

