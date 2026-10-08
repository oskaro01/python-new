from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MessageForm
from .models import Conversation

def landing(request):
    return render(request, "chat/landing.html")

@login_required
def chat_home(request):
    conversations = (
        Conversation.objects.filter(participants__user=request.user)
        .prefetch_related("participants__user")
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user),
            )
        )
        .distinct()
    )
    query = request.GET.get("q", "").strip()
    users = get_user_model().objects.none()
    if query:
        users = (
            get_user_model().objects.filter(username__icontains=query)
            .exclude(pk=request.user.pk)
            .order_by("username")[:10]
        )
    return render(
        request,
        "chat/home.html",
        {"conversations": conversations, "query": query, "users": users},
    )


@login_required
@require_POST
def start_conversation(request, user_id):
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    if other_user == request.user:
        return redirect("chat:home")

    conversation = (
        Conversation.objects.filter(participants__user=request.user)
        .filter(participants__user=other_user)
        .annotate(participant_count=Count("participants"))
        .filter(participant_count=2)
        .first()
    )
    if conversation is None:
        conversation = Conversation.objects.create()
        conversation.participants.create(user=request.user)
        conversation.participants.create(user=other_user)

    return redirect("chat:conversation_detail", conversation_id=conversation.id)


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants__user=request.user,
    )
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
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

