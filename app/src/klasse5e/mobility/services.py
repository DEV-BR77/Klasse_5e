from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from klasse5e.core.models import AuditEvent

from .models import MobilityListing, MobilityReaction, PickupDisclosure
from .policies import is_verified_guardian


@transaction.atomic
def create_reaction(*, listing, user, kind, message=""):
    locked = (
        MobilityListing.objects.select_for_update()
        .select_related("school_class")
        .get(pk=listing.pk)
    )
    if not is_verified_guardian(user, locked.school_class) or locked.creator_id == user.id:
        raise PermissionDenied
    if locked.status != MobilityListing.Status.ACTIVE or locked.valid_until < timezone.localdate():
        raise ValidationError("listing_not_active")
    reaction, _ = MobilityReaction.objects.update_or_create(
        listing=locked,
        user=user,
        defaults={"kind": kind, "message": message[:400], "status": MobilityReaction.Status.OPEN},
    )
    AuditEvent.objects.create(
        actor=user,
        action="mobility.reaction.created",
        target_type="mobility_reaction",
        target_id=str(reaction.id),
        metadata={"listing_id": str(locked.public_id), "kind": kind},
    )
    return reaction


@transaction.atomic
def decide_reaction(*, reaction, actor, decision):
    locked = (
        MobilityReaction.objects.select_for_update()
        .select_related("listing__school_class")
        .get(pk=reaction.pk)
    )
    if locked.listing.creator_id != actor.id or not is_verified_guardian(
        actor, locked.listing.school_class
    ):
        raise PermissionDenied
    if decision not in {MobilityReaction.Status.ACCEPTED, MobilityReaction.Status.DECLINED}:
        raise ValidationError("invalid_decision")
    locked.status = decision
    locked.save(update_fields=["status", "updated_at"])
    if decision == MobilityReaction.Status.ACCEPTED:
        locked.listing.status = MobilityListing.Status.MATCHED
        locked.listing.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action=f"mobility.reaction.{decision}",
        target_type="mobility_reaction",
        target_id=str(locked.id),
    )
    return locked


@transaction.atomic
def share_pickup(*, reaction, actor, exact_address, valid_until):
    locked = (
        MobilityReaction.objects.select_for_update()
        .select_related("listing__school_class")
        .get(pk=reaction.pk)
    )
    if locked.status != MobilityReaction.Status.ACCEPTED:
        raise ValidationError("reaction_not_accepted")
    if actor.id not in {locked.user_id, locked.listing.creator_id}:
        raise PermissionDenied
    if not is_verified_guardian(actor, locked.listing.school_class):
        raise PermissionDenied
    recipient = locked.listing.creator if actor.id == locked.user_id else locked.user
    disclosure, _ = PickupDisclosure.objects.get_or_create(
        reaction=locked,
        defaults={
            "listing": locked.listing,
            "shared_by": actor,
            "recipient": recipient,
            "encrypted_address": "",
            "valid_until": valid_until,
            "revoked_at": None,
        },
    )
    disclosure.listing = locked.listing
    disclosure.shared_by = actor
    disclosure.recipient = recipient
    disclosure.valid_until = valid_until
    disclosure.revoked_at = None
    disclosure.set_address(exact_address)
    disclosure.save()
    AuditEvent.objects.create(
        actor=actor,
        action="mobility.pickup.shared",
        target_type="pickup_disclosure",
        target_id=str(disclosure.id),
        metadata={"recipient_id": recipient.id},
    )
    return disclosure


@transaction.atomic
def revoke_pickup(*, disclosure, actor):
    locked = (
        PickupDisclosure.objects.select_for_update()
        .select_related("listing__school_class")
        .get(pk=disclosure.pk)
    )
    if locked.shared_by_id != actor.id or not is_verified_guardian(
        actor, locked.listing.school_class
    ):
        raise PermissionDenied
    if locked.revoked_at is None:
        locked.revoked_at = timezone.now()
        locked.encrypted_address = ""
        locked.save(update_fields=["revoked_at", "encrypted_address"])
        AuditEvent.objects.create(
            actor=actor,
            action="mobility.pickup.revoked",
            target_type="pickup_disclosure",
            target_id=str(locked.id),
        )
    return locked
