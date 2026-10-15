from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.http import content_disposition_header
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import MessageForm, MessageReportForm, ProfileForm, SignUpForm
from .models import (
    Conversation,
    FriendRequest,
    Friendship,
    Message,
    MessageAttachment,
    MessageReport,
    Profile,
    UserBlock,
)

def landing(request):
    return render(request, "chat/landing.html")


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok", "service": "chat-lab"})


def signup(request):
    if request.user.is_authenticated:
        return redirect("chat:home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("chat:home")
    return render(request, "registration/signup.html", {"form": form})


def _profile_for(user):
    return Profile.objects.get_or_create(user=user)[0]


def _user_display_name(user):
    return user.get_full_name() or user.get_username()


def _user_avatar_url(user):
    profile = getattr(user, "profile", None)
    return profile.avatar_url if profile else ""


def _friend_ids(user):
    # Keep the two directions separate for the local SQLite query planner.
    return set(Friendship.objects.filter(user=user).values_list("friend_id", flat=True)) | set(
        Friendship.objects.filter(friend=user).values_list("user_id", flat=True)
    )


def _blocked_user_ids(user):
    outgoing = UserBlock.objects.filter(blocker=user).values_list("blocked_id", flat=True)
    incoming = UserBlock.objects.filter(blocked=user).values_list("blocker_id", flat=True)
    return set(outgoing) | set(incoming)


def _users_are_blocked(first_user, second_user):
    return UserBlock.objects.filter(
        Q(blocker=first_user, blocked=second_user)
        | Q(blocker=second_user, blocked=first_user)
    ).exists()


def _search_people(user, query):
    if not query:
        return []
    friends = _friend_ids(user)
    incoming = dict(FriendRequest.objects.filter(
        to_user=user, status=FriendRequest.Status.PENDING,
    ).values_list("from_user_id", "id"))
    outgoing = set(FriendRequest.objects.filter(
        from_user=user, status=FriendRequest.Status.PENDING,
    ).values_list("to_user_id", flat=True))
    candidates = get_user_model().objects.select_related("profile").filter(
        Q(username__icontains=query) | Q(first_name__icontains=query)
        | Q(last_name__icontains=query) | Q(email__icontains=query)
    ).filter(is_active=True).exclude(pk=user.pk).exclude(
        pk__in=_blocked_user_ids(user)
    ).order_by("username")[:10]
    results = []
    for candidate in candidates:
        name = _user_display_name(candidate)
        status = "friends" if candidate.pk in friends else (
            "incoming" if candidate.pk in incoming else "pending" if candidate.pk in outgoing else "add"
        )
        results.append({
            "id": candidate.pk, "name": name, "initial": name[:1].upper(),
            "status": status, "request_id": incoming.get(candidate.pk),
            "avatar_url": _user_avatar_url(candidate),
        })
    return results


def _sidebar_context(request):
    blocked_ids = _blocked_user_ids(request.user)
    conversations = list(
        Conversation.objects.filter(participants__user=request.user)
        .prefetch_related("participants__user")
        .annotate(unread_count=Count(
            "messages", filter=Q(messages__is_read=False, messages__expires_at__gt=timezone.now()) & ~Q(messages__sender=request.user),
        )).distinct()
    )
    conversations = [
        conversation
        for conversation in conversations
        if not any(
            participant.user_id in blocked_ids
            for participant in conversation.participants.all()
        )
    ]
    for conversation in conversations:
        conversation.display_name = conversation.display_name_for(request.user)
        conversation.search_names = " ".join(
            f"{participant.user.get_username()} {participant.user.get_full_name()}"
            for participant in conversation.participants.all()
        )
    chat_query = request.GET.get("chat_q", "").strip()
    if chat_query:
        conversations = [c for c in conversations if chat_query.casefold() in c.search_names.casefold()]
    friends = get_user_model().objects.select_related("profile").filter(
        pk__in=_friend_ids(request.user), is_active=True,
    ).order_by("username")
    if chat_query:
        friends = friends.filter(
            Q(username__icontains=chat_query) | Q(first_name__icontains=chat_query)
            | Q(last_name__icontains=chat_query)
        )
    friends = list(friends)
    for friend in friends:
        friend.chat_name = _user_display_name(friend)
        friend.chat_avatar_url = _user_avatar_url(friend)
    query = request.GET.get("q", "").strip()
    return {
        "conversations": conversations, "friends": friends, "profile": _profile_for(request.user),
        "chat_query": chat_query,
        "query": query, "users": _search_people(request.user, query),
        "incoming_requests": FriendRequest.objects.filter(
            to_user=request.user, status=FriendRequest.Status.PENDING,
        ).select_related("from_user", "from_user__profile").order_by("created_at"),
    }

@login_required
def chat_home(request):
    self_conversation = Conversation.objects.filter(
        is_self=True,
        participants__user=request.user,
    ).first()
    if self_conversation is None:
        self_conversation = Conversation.objects.create(is_self=True)
        self_conversation.participants.create(user=request.user)

    return render(request, "chat/home.html", _sidebar_context(request))


@login_required
def profile_settings(request):
    profile = _profile_for(request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("chat:home")
    return render(request, "chat/profile.html", {"form": form, "profile": profile})


@login_required
@require_POST
def start_conversation(request, user_id):
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    if other_user == request.user or _users_are_blocked(request.user, other_user):
        return redirect("chat:home")

    conversation = (
        Conversation.objects.annotate(participant_count=Count("participants", distinct=True))
        .filter(participants__user=request.user)
        .filter(participants__user=other_user)
        .filter(participant_count=2, is_self=False)
        .first()
    )
    if conversation is None:
        conversation = Conversation.objects.create()
        conversation.participants.create(user=request.user)
        conversation.participants.create(user=other_user)

    return redirect("chat:conversation_detail", conversation_id=conversation.id)


@login_required
@require_GET
def search_users(request):
    query = request.GET.get("q", "").strip()
    return JsonResponse({"users": _search_people(request.user, query)})


def _friend_action_response(request, payload):
    if request.headers.get("Accept") == "application/json":
        return JsonResponse(payload)
    return redirect("chat:home")


@login_required
@require_POST
def send_friend_request(request, user_id):
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    if other_user == request.user:
        return JsonResponse({"error": "You cannot add yourself."}, status=400)
    if _users_are_blocked(request.user, other_user):
        return _friend_action_response(request, {"status": "blocked"})
    if (
        Friendship.objects.filter(user=request.user, friend=other_user).exists()
        or Friendship.objects.filter(user=other_user, friend=request.user).exists()
    ):
        return _friend_action_response(request, {"status": "friends"})

    incoming = FriendRequest.objects.filter(
        from_user=other_user, to_user=request.user, status=FriendRequest.Status.PENDING,
    ).first()
    if incoming:
        return _friend_action_response(request, {"status": "incoming", "request_id": incoming.pk})

    FriendRequest.objects.get_or_create(
        from_user=request.user,
        to_user=other_user,
        status=FriendRequest.Status.PENDING,
    )
    return _friend_action_response(request, {"status": "pending"})


@login_required
@require_POST
def respond_friend_request(request, request_id):
    action = request.POST.get("action")
    if action not in {"accept", "decline"}:
        return JsonResponse({"error": "Choose accept or decline."}, status=400)
    with transaction.atomic():
        friend_request = get_object_or_404(FriendRequest, pk=request_id, to_user=request.user)
        status = FriendRequest.Status.ACCEPTED if action == "accept" else FriendRequest.Status.DECLINED
        # Only a still-pending request may change; repeated clicks are harmless.
        changed = FriendRequest.objects.filter(
            pk=friend_request.pk, status=FriendRequest.Status.PENDING,
        ).update(status=status, responded_at=timezone.now())
        if changed and action == "accept":
            if friend_request.from_user_id not in _friend_ids(request.user):
                first_id, second_id = sorted([request.user.pk, friend_request.from_user_id])
                Friendship.objects.get_or_create(user_id=first_id, friend_id=second_id)
            FriendRequest.objects.filter(
                from_user=request.user, to_user=friend_request.from_user,
                status=FriendRequest.Status.PENDING,
            ).update(status=FriendRequest.Status.ACCEPTED, responded_at=timezone.now())
        if not changed:
            status = friend_request.status
    return _friend_action_response(request, {"status": "friends" if status == "accepted" else status})


@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(
        Conversation,
        pk=conversation_id,
        participants__user=request.user,
    )
    other_ids = conversation.participants.exclude(user=request.user).values_list("user_id", flat=True)
    if UserBlock.objects.filter(
        Q(blocker=request.user, blocked_id__in=other_ids)
        | Q(blocked=request.user, blocker_id__in=other_ids)
    ).exists():
        raise Http404
    other_user = conversation.participants.exclude(user=request.user).select_related("user").first()
    visible_messages = conversation.messages.filter(expires_at__gt=timezone.now())
    conversation.display_name = conversation.display_name_for(request.user)
    if request.method == "POST":
        async_request = request.headers.get("X-Chat-Async") == "1"
        form = MessageForm(request.POST, request.FILES)
        if not form.is_valid():
            if async_request:
                errors = form.errors.get_json_data()
                message = " ".join(
                    error["message"]
                    for field_errors in errors.values()
                    for error in field_errors
                )
                return JsonResponse({"ok": False, "error": message}, status=400)
        else:
            upload = form.cleaned_data.get("attachment")
            saved_attachment = None
            try:
                with transaction.atomic():
                    message = form.save(commit=False)
                    message.conversation = conversation
                    message.sender = request.user
                    message.save()
                    if upload:
                        saved_attachment = MessageAttachment.objects.create(
                            message=message,
                            file=upload,
                            original_name=upload.name.rsplit("\\", 1)[-1].rsplit("/", 1)[-1][:255],
                            content_type=upload.content_type,
                            size_bytes=upload.size,
                        )
                    conversation.updated_at = timezone.now()
                    conversation.save(update_fields=["updated_at"])
            except Exception:
                if saved_attachment and saved_attachment.file:
                    saved_attachment.file.delete(save=False)
                raise
            if async_request:
                message = Message.objects.select_related("sender").prefetch_related(
                    "attachments"
                ).get(pk=message.pk)
                return JsonResponse({
                    "ok": True,
                    "html": render_to_string(
                        "chat/_message.html",
                        {
                            "message": message,
                            "user": request.user,
                            "report_reasons": MessageReport.Reason.choices,
                        },
                        request=request,
                    ),
                    "pagination_html": render_to_string(
                        "chat/_message_pagination.html",
                        {
                            "conversation": conversation,
                            "page_obj": Paginator(
                                conversation.messages.filter(expires_at__gt=timezone.now())
                                .order_by("-created_at", "-pk"), 20,
                            ).get_page(1),
                            "message_query": "",
                        },
                        request=request,
                    ),
                })
            return redirect("chat:conversation_detail", conversation_id=conversation.id)
    else:
        form = MessageForm()

    message_query = request.GET.get("message_q", "").strip()[:200]
    if message_query:
        visible_messages = visible_messages.filter(body__icontains=message_query)
    # Slice in SQL before loading senders and attachments. Page 1 is the newest.
    page_obj = Paginator(
        visible_messages.order_by("-created_at", "-pk")
        .select_related("sender").prefetch_related("attachments"), 20,
    ).get_page(request.GET.get("page", 1))
    messages = list(page_obj.object_list)
    # Only the received messages actually displayed on this page become read.
    conversation.messages.filter(
        pk__in=[message.pk for message in messages], is_read=False,
    ).exclude(sender=request.user).update(is_read=True)

    return render(
        request,
        "chat/conversation_detail.html",
        {
            **_sidebar_context(request), "conversation": conversation, "form": form,
            "messages": list(reversed(messages)),
            "page_obj": page_obj, "message_query": message_query,
            "other_user": other_user.user if other_user else None,
            "report_reasons": MessageReport.Reason.choices,
        },
    )


@login_required
@require_POST
def block_user(request, user_id):
    other_user = get_object_or_404(get_user_model(), pk=user_id)
    if other_user != request.user:
        UserBlock.objects.get_or_create(blocker=request.user, blocked=other_user)
        FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=other_user)
            | Q(from_user=other_user, to_user=request.user),
            status=FriendRequest.Status.PENDING,
        ).update(status=FriendRequest.Status.DECLINED, responded_at=timezone.now())
    return redirect("chat:home")


@login_required
@require_POST
def report_message(request, message_id):
    message = get_object_or_404(
        Message.objects.filter(
            conversation__participants__user=request.user,
            expires_at__gt=timezone.now(),
        ),
        pk=message_id,
    )
    form = MessageReportForm(request.POST)
    if form.is_valid():
        MessageReport.objects.get_or_create(
            message=message,
            reporter=request.user,
            defaults={"reason": form.cleaned_data["reason"]},
        )
        return redirect("chat:conversation_detail", conversation_id=message.conversation_id)
    return redirect("chat:conversation_detail", conversation_id=message.conversation_id)


@login_required
@require_GET
def attachment_file(request, attachment_id):
    """Stream an attachment only to a participant in its conversation."""

    attachment = get_object_or_404(
        MessageAttachment.objects.select_related("message", "message__conversation").filter(
            message__conversation__participants__user=request.user,
            expires_at__gt=timezone.now(),
            message__expires_at__gt=timezone.now(),
        ),
        pk=attachment_id,
    )
    try:
        file_handle = attachment.file.open("rb")
    except (FileNotFoundError, OSError, ValueError):
        raise Http404 from None

    response = FileResponse(file_handle, content_type=attachment.content_type)
    as_attachment = request.GET.get("download") == "1"
    response["Content-Disposition"] = content_disposition_header(
        as_attachment,
        attachment.original_name,
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response

