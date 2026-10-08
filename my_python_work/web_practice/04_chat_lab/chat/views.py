from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import Conversation

def landing(request):
    return render(request, "chat/landing.html")

@login_required
def chat_home(request):
    conversations = (
        Conversation.objects.filter(participants__user=request.user)
        .prefetch_related("participants__user")
        .distinct()
    )
    return render(request, "chat/home.html", {"conversations": conversations})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants__user=request.user,
    )
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            return redirect("chat:conversation_detail", conversation_id=conversation.id)
    else:
        form = MessageForm()

    return render(
        request,
        "chat/conversation_detail.html",
        {"conversation": conversation, "form": form},
    )

