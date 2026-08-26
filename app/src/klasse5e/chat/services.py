from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import AuditEvent, Role
from klasse5e.core.policies import active_roles, has_active_membership

from .models import ChatMessage, ChatReadState


def require_room_access(user, room):
    if not has_active_membership(user, room.school_class):
        raise PermissionDenied


def may_moderate(user, room):
    return bool(
        active_roles(user, room.school_class)
        & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.MODERATOR}
    )


@transaction.atomic
def create_message(room, user, body, reply_to=None):
    require_room_access(user, room)
    if not room.is_open:
        raise ValidationError("room_closed")
    body = body.strip()
    if not body or len(body) > 2000:
        raise ValidationError("invalid_body")
    if reply_to and reply_to.room_id != room.id:
        raise ValidationError("reply_room_mismatch")
    message = ChatMessage.objects.create(room=room, author=user, body=body, reply_to=reply_to)
    AuditEvent.objects.create(
        actor=user,
        action="chat.message.created",
        target_type="chat_message",
        target_id=str(message.public_id),
    )
    return message


def mark_read(room, user):
    require_room_access(user, room)
    ChatReadState.objects.update_or_create(
        room=room, user=user, defaults={"last_read_at": timezone.now()}
    )
