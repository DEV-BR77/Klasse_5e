import secrets

from django.db import transaction
from django.utils import timezone

from .models import (
    AccountDeletionRequest,
    AuditEvent,
    ClassMembership,
    ConsentDecision,
    GuardianChildRelationship,
    MembershipStatus,
    PushSubscription,
    RoleAssignment,
)


@transaction.atomic
def erase_account_data(item: AccountDeletionRequest) -> None:
    """Irreversibly removes private payloads while retaining anonymous audit references."""
    request_item = AccountDeletionRequest.objects.select_for_update().select_related(
        "user__person"
    ).get(pk=item.pk)
    if request_item.status != AccountDeletionRequest.Status.PENDING:
        return
    user = request_item.user
    person = getattr(user, "person", None)

    # Integration credentials, sessions, push endpoints and personal notifications
    # have no retention purpose after withdrawal.
    user.webuntis_connections.all().delete()
    user.itslearningconnection_set.all().delete()
    PushSubscription.objects.filter(user=user).delete()
    user.notifications.all().delete()
    user.chat_mentions.clear()

    # User-authored chat text and files disappear; the anonymous record preserves
    # conversation ordering for other participants.
    for message in user.chatmessage_set.all():
        if message.attachment:
            message.attachment.delete(save=False)
        message.body = "[Beitrag gelöscht]"
        message.attachment = ""
        message.attachment_name = ""
        message.attachment_content_type = ""
        message.save(
            update_fields=[
                "body",
                "attachment",
                "attachment_name",
                "attachment_content_type",
            ]
        )

    if person is not None:
        # Uploaded photo files are removed even where an anonymous moderation row
        # must remain because of protected relations.
        for photo in user.photo_set.all():
            for field_name in ("display_file", "thumbnail_file", "download_file"):
                stored_file = getattr(photo, field_name)
                if stored_file:
                    stored_file.delete(save=False)
                    setattr(photo, field_name, "")
            photo.status = "withdrawn"
            photo.save(
                update_fields=["display_file", "thumbnail_file", "download_file", "status"]
            )
        if person.profile_photo:
            person.profile_photo.delete(save=False)
        ConsentDecision.objects.filter(subject_person=person).delete()
        GuardianChildRelationship.objects.filter(
            guardian_person=person
        ).update(status="revoked", valid_until=timezone.localdate())
        GuardianChildRelationship.objects.filter(
            student_person=person
        ).update(status="revoked", valid_until=timezone.localdate())
        ClassMembership.objects.filter(person=person).update(
            status=MembershipStatus.ENDED, valid_until=timezone.localdate()
        )
        person.first_name = "Gelöschtes"
        person.last_name = "Konto"
        person.phone = ""
        person.other_contact = ""
        person.street = ""
        person.postal_code = ""
        person.city = ""
        person.home_latitude = None
        person.home_longitude = None
        person.chat_display_name = ""
        person.profile_photo = ""
        person.save()

    RoleAssignment.objects.filter(user=user).update(active=False)
    user.email = f"deleted-{user.pk}-{secrets.token_hex(6)}@invalid.local"
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.locked_at = timezone.now()
    user.set_unusable_password()
    user.save()
    AuditEvent.objects.create(
        actor=None,
        action="privacy.account.erased",
        target_type="anonymous-account",
        target_id=str(user.pk),
    )
    request_item.status = AccountDeletionRequest.Status.COMPLETED
    request_item.processed_at = timezone.now()
    request_item.save(update_fields=["status", "processed_at"])
