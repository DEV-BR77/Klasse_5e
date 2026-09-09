from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models, transaction
from django.utils import timezone

from klasse5e.core.models import (
    AuditEvent,
    GuardianChildRelationship,
    Role,
    RoleAssignment,
    SchoolClass,
    StudentProfile,
)
from klasse5e.core.policies import active_roles, has_active_membership

from .models import (
    ChatMessage,
    ChatReadState,
    ChatRetentionCategory,
    ChatRoom,
    DirectConversation,
)
from .safety import filter_chat_language


def _image_safety_status(attachment):
    if not attachment or not attachment.content_type.startswith("image/"):
        return "approved" if attachment else "not_applicable"
    from klasse5e.biometrics.client import VisionClient, VisionError

    try:
        content = attachment.read()
        attachment.seek(0)
        result = VisionClient(timeout=12).classify_image_safety(
            content, attachment.content_type
        )
    except (OSError, VisionError):
        return "pending"
    decision = result.get("decision")
    return decision if decision in {"approved", "blocked"} else "pending"


def _mentioned_users(room, body):
    import re

    from klasse5e.core.models import UserAccount

    direct = getattr(room, "direct_conversation", None)
    if direct:
        users = UserAccount.objects.filter(
            pk__in=[direct.participant_one_id, direct.participant_two_id]
        )
    else:
        users = UserAccount.objects.filter(
            person__classmembership__school_class=room.school_class,
            person__classmembership__status="active",
        )
    users = users.select_related("person").distinct()
    found = []
    for candidate in users:
        aliases = {candidate.person.first_name.strip(), candidate.person.chat_display_name.strip()}
        if any(alias and re.search(rf"(?<!\w)@{re.escape(alias)}(?!\w)", body, re.IGNORECASE) for alias in aliases):
            found.append(candidate)
    return found


def require_room_access(user, room):
    direct = getattr(room, "direct_conversation", None)
    if direct:
        if (
            user.pk not in {direct.participant_one_id, direct.participant_two_id}
            or not has_active_membership(user, room.school_class)
        ):
            raise PermissionDenied
        return
    is_portal_admin = user.is_superuser or RoleAssignment.objects.filter(
        user=user,
        active=True,
        role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.SCHOOL_ADMIN, Role.CLASS_ADMIN],
    ).filter(
        models.Q(school_class=room.school_class)
        | models.Q(school=room.school_class.school)
        | models.Q(school__isnull=True, school_class__isnull=True)
    ).exists()
    if is_portal_admin:
        return
    if not has_active_membership(user, room.school_class):
        raise PermissionDenied
    if room.audience == room.Audience.STUDENTS:
        if not StudentProfile.objects.filter(person=user.person).exists():
            raise PermissionDenied
    elif room.audience == room.Audience.GUARDIANS:
        today = timezone.localdate()
        is_guardian = GuardianChildRelationship.objects.filter(
            guardian_person=user.person,
            student_person__classmembership__school_class=room.school_class,
            student_person__classmembership__status="active",
            student_person__classmembership__valid_from__lte=today,
            status="verified",
            verified_at__isnull=False,
            may_view_student_profile=True,
            valid_from__lte=today,
        ).filter(
            models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today),
            models.Q(student_person__classmembership__valid_until__isnull=True)
            | models.Q(student_person__classmembership__valid_until__gte=today),
        ).exists()
        if not is_guardian:
            raise PermissionDenied
    elif room.audience == room.Audience.PARENT_REPRESENTATIVES:
        if not RoleAssignment.objects.filter(
            user=user,
            school_class=room.school_class,
            role=Role.PARENT_REPRESENTATIVE,
            active=True,
        ).exists():
            raise PermissionDenied


def may_moderate(user, room):
    return bool(
        active_roles(user, room.school_class)
        & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.MODERATOR}
    )


def may_start_direct_conversation(user, target_person, school_class):
    if (
        not getattr(user, "is_authenticated", False)
        or not getattr(user, "is_active", False)
        or user.locked_at
        or not target_person.user_id
        or target_person.user_id == user.pk
        or not target_person.user.is_active
        or target_person.user.locked_at
        or not has_active_membership(user, school_class)
        or not has_active_membership(target_person.user, school_class)
    ):
        return False
    today = timezone.localdate()
    return GuardianChildRelationship.objects.filter(
        guardian_person=target_person,
        status="verified",
        verified_at__isnull=False,
        may_view_student_profile=True,
        valid_from__lte=today,
        student_person__classmembership__school_class=school_class,
        student_person__classmembership__status="active",
        student_person__classmembership__valid_from__lte=today,
    ).filter(
        models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today),
        models.Q(student_person__classmembership__valid_until__isnull=True)
        | models.Q(student_person__classmembership__valid_until__gte=today),
    ).exists()


@transaction.atomic
def get_or_create_direct_conversation(user, target_person, school_class):
    school_class = SchoolClass.objects.select_for_update().get(pk=school_class.pk)
    if not may_start_direct_conversation(user, target_person, school_class):
        raise PermissionDenied
    participant_one_id, participant_two_id = sorted([user.pk, target_person.user_id])
    existing = DirectConversation.objects.select_related("room").filter(
        school_class=school_class,
        participant_one_id=participant_one_id,
        participant_two_id=participant_two_id,
    ).first()
    if existing:
        return existing
    retention, _created = ChatRetentionCategory.objects.get_or_create(
        name="Private Nachrichten",
        defaults={
            "retention_days": 180,
            "automatic_deletion_enabled": True,
            "intended_for_events": False,
            "is_active": True,
        },
    )
    room = ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title="Private Unterhaltung",
        retention_category=retention,
    )
    conversation = DirectConversation.objects.create(
        room=room,
        school_class=school_class,
        participant_one_id=participant_one_id,
        participant_two_id=participant_two_id,
    )
    AuditEvent.objects.create(
        actor=user,
        action="chat.direct_conversation.created",
        target_type="direct_conversation",
        target_id=str(room.public_id),
    )
    return conversation


def room_title_for_user(room, user):
    direct = getattr(room, "direct_conversation", None)
    if not direct:
        return room.title
    other = direct.other_participant(user)
    if not other:
        return "Private Unterhaltung"
    person = getattr(other, "person", None)
    if not person:
        return "Private Unterhaltung"
    return person.chat_display_name or person.first_name or "Private Unterhaltung"


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
        attachment_name = attachment.name[:180]
        if attachment.content_type.startswith("image/"):
            from .safety import ImagePixelationError, sanitize_chat_image

            try:
                clean_image = sanitize_chat_image(attachment.read())
            except ImagePixelationError as exc:
                raise ValidationError("invalid_attachment") from exc
            attachment = SimpleUploadedFile(
                "chat-image.jpg", clean_image, content_type="image/jpeg"
            )
    else:
        attachment_name = ""
    if reply_to and reply_to.room_id != room.id:
        raise ValidationError("reply_room_mismatch")
    filtered_body, filter_hits = filter_chat_language(body)
    attachment_safety_status = _image_safety_status(attachment)
    message = ChatMessage.objects.create(
        room=room,
        author=user,
        body=filtered_body,
        reply_to=reply_to,
        attachment=attachment,
        attachment_name=attachment_name,
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
    if attachment and attachment.content_type.startswith("image/"):
        AuditEvent.objects.create(
            actor=user,
            action=f"chat.image_safety.{attachment_safety_status}",
            target_type="chat_message",
            target_id=str(message.public_id),
        )
    if getattr(room, "direct_conversation", None):
        from .notifications import notify_direct_message

        transaction.on_commit(lambda: notify_direct_message(message.pk))
    else:
        mentioned = [
            candidate
            for candidate in _mentioned_users(room, filtered_body)
            if candidate.pk != user.pk
        ]
        if mentioned:
            message.mentions.add(*mentioned)
            from .notifications import notify_mentions

            transaction.on_commit(lambda: notify_mentions(message.pk))
        from .notifications import notify_parent_representatives

        transaction.on_commit(lambda: notify_parent_representatives(message.pk))
    return message


def mark_read(room, user):
    require_room_access(user, room)
    ChatReadState.objects.update_or_create(
        room=room, user=user, defaults={"last_read_at": timezone.now()}
    )
