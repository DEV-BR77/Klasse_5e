import hashlib
from io import BytesIO

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import (
    ActivationGrant,
    AuditEvent,
    ClassMembership,
    GuardianChildRelationship,
    Household,
    Invitation,
    Person,
    RegistrationApplication,
    RelationshipStatus,
    Role,
    RoleAssignment,
    StudentProfile,
    UserAccount,
)


def create_application(*, email, first_name, last_name, password):
    email = email.strip().casefold()
    first_name, last_name = first_name.strip(), last_name.strip()
    if not email or not first_name or not last_name:
        raise ValidationError("Bitte fülle alle Pflichtfelder aus.")
    validate_password(password)
    if UserAccount.objects.filter(email__iexact=email).exists():
        return None, None
    existing = RegistrationApplication.objects.filter(email__iexact=email).first()
    if existing:
        return None, None
    return RegistrationApplication.issue(
        email=email,
        first_name=first_name[:100],
        last_name=last_name[:100],
        password_hash=make_password(password),
    )


@transaction.atomic
def verify_email(token):
    digest = hashlib.sha256(token.encode()).hexdigest()
    item = RegistrationApplication.objects.select_for_update().filter(email_token_hash=digest).first()
    if not item or item.email_token_expires_at <= timezone.now():
        return None
    if item.status == RegistrationApplication.Status.EMAIL_PENDING:
        item.status = RegistrationApplication.Status.REVIEW_PENDING
        item.email_verified_at = timezone.now()
        item.save(update_fields=["status", "email_verified_at", "updated_at"])
    return item


@transaction.atomic
def activate(token):
    digest = hashlib.sha256(token.encode()).hexdigest()
    grant = ActivationGrant.objects.select_for_update().select_related("application").filter(token_hash=digest).first()
    if not grant or grant.used_at or grant.revoked_at or grant.expires_at <= timezone.now():
        return None
    app = grant.application
    if app.status != RegistrationApplication.Status.APPROVED or not app.school_class_id:
        return None
    user, created = UserAccount.objects.get_or_create(
        email=app.email,
        defaults={"password": app.password_hash, "email_verified_at": app.email_verified_at, "is_active": True},
    )
    if not created and user.is_active:
        return None
    if not created:
        user.password = app.password_hash
        user.email_verified_at = app.email_verified_at
        user.is_active = True
        user.save(update_fields=["password", "email_verified_at", "is_active"])
    person, _ = Person.objects.get_or_create(
        user=user, defaults={"first_name": app.first_name, "last_name": app.last_name}
    )
    ClassMembership.objects.get_or_create(
        school_class=app.school_class,
        person=person,
        defaults={"valid_from": timezone.localdate(), "status": "active"},
    )
    RoleAssignment.objects.get_or_create(
        user=user,
        school=app.school,
        school_class=app.school_class,
        role=Role.GUARDIAN,
        defaults={"assigned_by": app.reviewed_by},
    )
    grant.used_at = timezone.now()
    grant.save(update_fields=["used_at"])
    app.status = RegistrationApplication.Status.ACTIVATED
    app.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(actor=user, action="registration.activated", target_type="user", target_id=str(user.pk))
    family = app.family_request
    if family and not family.completed_at:
        household = Household.objects.create(label=family.household_label)
        household.members.add(person)
        family.household = household
        for child_data in family.children:
            child = Person.objects.create(
                first_name=child_data["first_name"][:100],
                last_name=child_data["last_name"][:100],
            )
            household.members.add(child)
            ClassMembership.objects.create(
                school_class=app.school_class,
                person=child,
                valid_from=timezone.localdate(),
                status="active",
            )
            StudentProfile.objects.create(person=child)
            GuardianChildRelationship.objects.create(
                guardian_person=person,
                student_person=child,
                relationship_type="guardian",
                is_legal_guardian=True,
                may_view_student_profile=True,
                may_manage_profile=True,
                may_manage_general_consents=True,
                may_manage_photo_consents=True,
                may_manage_biometric_consents=True,
                valid_from=timezone.localdate(),
                status=RelationshipStatus.VERIFIED,
                verified_by=app.reviewed_by,
                verified_at=timezone.now(),
            )
        for adult in family.additional_adults:
            invitation, family_token = Invitation.issue(
                adult["email"],
                app.reviewed_by,
                first_name=adult["first_name"],
                last_name=adult["last_name"],
                school_class=app.school_class,
                household=household,
                family_request=family,
            )
            link = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/invitation/{family_token}/"
            send_mail(
                "Dein persönlicher KlassID-Familienzugang",
                f"Lege über diesen einmaligen Link innerhalb von 7 Tagen dein eigenes Passwort fest: {link}",
                settings.DEFAULT_FROM_EMAIL,
                [invitation.email],
            )
        family.status = "completed"
        family.completed_at = timezone.now()
        family.save(update_fields=["household", "status", "completed_at"])
        family.access_code.completed_at = timezone.now()
        family.access_code.save(update_fields=["completed_at"])
    return user


def sanitized_profile_photo(upload):
    if upload.size > 5 * 1024 * 1024:
        raise ValidationError("Das Profilfoto darf höchstens 5 MB groß sein.")
    try:
        image = Image.open(upload)
        image.verify()
        upload.seek(0)
        image = Image.open(upload)
        image = ImageOps.exif_transpose(image)
        if image.width * image.height > 20_000_000:
            raise ValidationError("Das Bild ist zu groß.")
        image.thumbnail((1024, 1024))
        output = BytesIO()
        image.convert("RGB").save(output, format="WEBP", quality=86, method=6)
        return output.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("Das Profilfoto ist ungültig.") from exc
