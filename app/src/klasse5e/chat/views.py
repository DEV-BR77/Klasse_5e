import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from klasse5e.core.models import AuditEvent
from klasse5e.core.policies import family_label

from .models import ChatMessage, ChatReport, ChatRoom
from .services import create_message, mark_read, may_moderate, require_room_access


def _room(room_id):
    return get_object_or_404(ChatRoom, public_id=room_id)


@login_required
def room_detail(request, room_id):
    room = _room(room_id)
    try:
        require_room_access(request.user, room)
    except PermissionDenied:
        raise Http404 from None
    return JsonResponse(
        {
            "id": str(room.public_id),
            "title": room.title,
            "poll_url": f"/chat/rooms/{room.public_id}/messages/",
        }
    )


@login_required
@require_http_methods(["GET", "POST"])
def messages(request, room_id):
    room = _room(room_id)
    try:
        require_room_access(request.user, room)
        if request.method == "POST":
            reply = None
            reply_id = request.POST.get("reply_to")
            if reply_id:
                reply = get_object_or_404(ChatMessage, public_id=reply_id, room=room)
            message = create_message(room, request.user, request.POST.get("body", ""), reply)
            return JsonResponse({"id": str(message.public_id)}, status=201)
        since = request.GET.get("since")
        query = room.messages.select_related("author__person").order_by("created_at")
        if since:
            query = query.filter(created_at__gt=since)
        data = [
            {
                "id": str(item.public_id),
                "body": "" if item.withdrawn_at or item.hidden_at else item.body,
                "author": family_label(item.author),
                "created_at": item.created_at.isoformat(),
                "withdrawn": bool(item.withdrawn_at),
                "hidden": bool(item.hidden_at),
            }
            for item in query[:200]
        ]
        mark_read(room, request.user)
        return JsonResponse({"messages": data})
    except (PermissionDenied, ValidationError):
        raise Http404 from None


@login_required
@require_http_methods(["PATCH", "DELETE"])
def edit_or_delete_message(request, message_id):
    message = get_object_or_404(ChatMessage, public_id=message_id)
    try:
        require_room_access(request.user, message.room)
    except PermissionDenied:
        raise Http404 from None
    if message.author_id != request.user.id or message.withdrawn_at:
        raise Http404
    if request.method == "DELETE":
        message.body = ""
        message.withdrawn_at = timezone.now()
        action = "chat.message.withdrawn"
    else:
        try:
            body = json.loads(request.body or b"{}").get("body", "").strip()
        except (ValueError, TypeError):
            body = ""
        if not body or len(body) > 2000:
            return JsonResponse({"error": "invalid_body"}, status=400)
        message.body = body
        message.edited_at = timezone.now()
        action = "chat.message.edited"
    message.save()
    AuditEvent.objects.create(
        actor=request.user,
        action=action,
        target_type="chat_message",
        target_id=str(message.public_id),
    )
    return HttpResponse(status=204)


@login_required
@require_POST
def report_message(request, message_id):
    message = get_object_or_404(ChatMessage, public_id=message_id)
    try:
        require_room_access(request.user, message.room)
    except PermissionDenied:
        raise Http404 from None
    reason = request.POST.get("reason", "other")
    if reason not in {"inappropriate", "privacy", "other"}:
        reason = "other"
    ChatReport.objects.get_or_create(
        message=message, reporter=request.user, defaults={"reason": reason}
    )
    return HttpResponse(status=204)


@login_required
@require_POST
def moderate_message(request, message_id):
    message = get_object_or_404(ChatMessage, public_id=message_id)
    if not may_moderate(request.user, message.room):
        raise Http404
    message.hidden_at = timezone.now()
    message.hidden_by = request.user
    message.save(update_fields=["hidden_at", "hidden_by"])
    AuditEvent.objects.create(
        actor=request.user,
        action="chat.message.hidden",
        target_type="chat_message",
        target_id=str(message.public_id),
    )
    return HttpResponse(status=204)
