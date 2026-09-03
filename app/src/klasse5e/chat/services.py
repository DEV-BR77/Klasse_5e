from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import AuditEvent, Role
from klasse5e.core.policies import active_roles, has_active_membership

from .models import ChatMessage, ChatReadState
from .safety import filter_chat_language


def _mentioned_users(room, body):
    import re

    from klasse5e.core.models import UserAccount

    users = UserAccount.objects.filter(
        person__classmembership__school_class=room.school_class,
        person__classmembership__status="active",
    ).select_related("person").distinct()
    found = []
    for candidate in users:
        aliases = {candidate.person.first_name.strip(), candidate.person.chat_display_name.strip()}
        if any(alias and re.search(rf"(?<!\w)@{re.escape(alias)}(?!\w)", body, re.IGNORECASE) for alias in aliases):
            found.append(candidate)
    return found


def require_room_access(user, room):
    if not has_active_membership(user, room.school_class):
        raise PermissionDenied


def may_moderate(user, room):
    return bool(
        active_roles(user, room.school_class)
        & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.MODERATOR}
    )


@transaction.atomic
def create_message(room, user, body, reply_to=None, attachment=None):
    require_room_access(user, room)
    if not room.is_open:
        raise ValidationError("room_closed")
    body = body.strip()
    if (not body and not attachment) or len(body) > 2000:
        raise ValidationError("invalid_body")
    if attachment:
        allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf", "audio/webm", "audio/ogg", "audio/mp4"}
        if attachment.size > 8 * 1024 * 1024 or attachment.content_type not in allowed:
            raise ValidationError("invalid_attachment")
    if reply_to and reply_to.room_id != room.id:
        raise ValidationError("reply_room_mismatch")
    filtered_body, filter_hits = filter_chat_language(body)
    attachment_safety_status = "not_applicable"
    if attachment:
        attachment_safety_status = (
            "pending" if attachment.content_type.startswith("image/") else "approved"
        )
    message = ChatMessage.objects.create(
        room=room,
        author=user,
        body=filtered_body,
        reply_to=reply_to,
        attachment=attachment,
        attachment_name=(attachment.name[:180] if attachment else ""),
        attachment_content_type=(attachment.content_type[:80] if attachment else ""),
        attachment_safety_status=attachment_safety_status,
        language_filter_hits=filter_hits,
    )
    AuditEvent.objects.create(
        actor=user,
        action="chat.message.created",
        target_type="chat_message",
        target_id=str(message.public_id),
    )
    if filter_hits:
        AuditEvent.objects.create(
            actor=user,
            action="chat.language_filter.applied",
            target_type="chat_message",
            target_id=str(message.public_id),
            metadata={"hit_count": filter_hits},
        )
    mentioned = [
        candidate for candidate in _mentioned_users(room, filtered_body) if candidate.pk != user.pk
    ]
    if mentioned:
        message.mentions.add(*mentioned)
        from .notifications import notify_mentions

        transaction.on_commit(lambda: notify_mentions(message.pk))
    return message


def mark_read(room, user):
    require_room_access(user, room)
    ChatReadState.objects.update_or_create(
        room=room, user=user, defaults={"last_read_at": timezone.now()}
    )
