from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

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
    return render(request, "chat/conversation_detail.html", {"conversation": conversation})

