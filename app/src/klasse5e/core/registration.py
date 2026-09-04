import hashlib
import secrets
from datetime import timedelta
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
    RelationshipType,
    Role,
    RoleAssignment,
    StudentProfile,
    UserAccount,
    UserNotification,
    normalize_login_email,
)
from .policies import active_class_for_user


def create_application(*, email, first_name, last_name, password, refresh_unverified=False):
    email = normalize_login_email(email)
    first_name, last_name = first_name.strip(), last_name.strip()
    if not email or not first_name or not last_name:
        raise ValidationError("Bitte fülle alle Pflichtfelder aus.")
    validate_password(password)
    if UserAccount.objects.filter(email__iexact=email).exists():
        return None, None
    existing_query = RegistrationApplication.objects
    if refresh_unverified:
        existing_query = existing_query.select_for_update()
    existing = existing_query.filter(email__iexact=email).first()
    if existing:
        if (
            refresh_unverified
            and existing.status == RegistrationApplication.Status.EMAIL_PENDING
            and existing.email_verified_at is None
            and existing.family_request_id is None
        ):
            token = secrets.token_urlsafe(32)
            existing.first_name = first_name[:100]
            existing.last_name = last_name[:100]
            existing.password_hash = make_password(password)
            existing.email_token_hash = hashlib.sha256(token.encode()).hexdigest()
            existing.email_token_expires_at = timezone.now() + timedelta(hours=24)
            existing.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "password_hash",
                    "email_token_hash",
                    "email_token_expires_at",
                    "updated_at",
                ]
            )
            return existing, token
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
    item = (
        RegistrationApplication.objects.select_for_update().filter(email_token_hash=digest).first()
    )
    if not item or item.email_token_expires_at <= timezone.now():
        return None
    if item.status == RegistrationApplication.Status.EMAIL_PENDING:
        item.status = RegistrationApplication.Status.REVIEW_PENDING
        item.email_verified_at = timezone.now()
        item.save(update_fields=["status", "email_verified_at", "updated_at"])
        admin_emails = set(
            UserAccount.objects.filter(is_superuser=True).values_list("email", flat=True)
        )
        admin_emails.update(
            RoleAssignment.objects.filter(
                active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
            ).values_list("user__email", flat=True)
        )
        admin_users = list(
            UserAccount.objects.filter(is_superuser=True)
            | UserAccount.objects.filter(
                roleassignment__active=True,
                roleassignment__role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN],
            )
        )
        revision = hashlib.sha256(
            f"registration:{item.pk}:{item.updated_at.isoformat()}".encode()
        ).hexdigest()[:32]
        for admin in admin_users:
            target_class = active_class_for_user(admin)
            if target_class is None:
                target_class = (
                    RoleAssignment.objects.filter(
                        user=admin,
                        active=True,
                        role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN],
                        school_class__isnull=False,
                    )
                    .values_list("school_class", flat=True)
                    .first()
                )
                if target_class:
                    from .models import SchoolClass

                    target_class = SchoolClass.objects.filter(pk=target_class).first()
            if target_class:
                UserNotification.objects.get_or_create(
                    user=admin,
                    school_class=target_class,
                    category="registrations",
                    object_type="registration_application",
                    object_id=str(item.pk),
                    revision=revision,
                    defaults={
                        "title": "Neue Anmeldung",
                        "summary": f"{item.first_name} {item.last_name} wartet auf Prüfung.",
                        "target_url": "/admin/core/registrationapplication/",
                    },
                )
        if admin_emails:
            send_mail(
                "Neue KlassID-Anmeldung wartet auf Prüfung",
                f"{item.first_name} {item.last_name} ({item.email}) hat die E-Mail-Adresse bestätigt. "
                "Der Antrag kann im Admin-Bereich unter Registrierungen geprüft und einer Schule/Klasse zugeordnet werden.",
                settings.DEFAULT_FROM_EMAIL,
                sorted(admin_emails),
                fail_silently=True,
            )
    return item


@transaction.atomic
def activate(token):
    digest = hashlib.sha256(token.encode()).hexdigest()
    grant = (
        ActivationGrant.objects.select_for_update()
        .select_related("application")
        .filter(token_hash=digest)
        .first()
    )
    if not grant or grant.used_at or grant.revoked_at or grant.expires_at <= timezone.now():
        return None
    app = grant.application
    if app.status != RegistrationApplication.Status.APPROVED or not app.school_class_id:
        return None
    user, created = UserAccount.objects.get_or_create(
        email=app.email,
        defaults={
            "password": app.password_hash,
            "email_verified_at": app.email_verified_at,
            "is_active": True,
        },
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
    AuditEvent.objects.create(
        actor=user, action="registration.activated", target_type="user", target_id=str(user.pk)
    )
    family = app.family_request
    if family and not family.completed_at:
        household = Household.objects.create(label=family.household_label)
        household.members.add(person)
        family.household = household
        access_code = family.access_code
        existing_guardian = access_code.existing_guardian
        existing_guardian_person = None
        if existing_guardian and existing_guardian != user:
            existing_guardian_person = getattr(existing_guardian, "person", None)
            if existing_guardian_person is None:
                raise ValidationError(
                    "Der bereits zugeordnete Elternzugang besitzt kein Personenprofil."
                )
            household.members.add(existing_guardian_person)
            ClassMembership.objects.get_or_create(
                school_class=app.school_class,
                person=existing_guardian_person,
                defaults={"valid_from": timezone.localdate(), "status": "active"},
            )
            role_assignment, _ = RoleAssignment.objects.get_or_create(
                user=existing_guardian,
                school_class=app.school_class,
                role=Role.GUARDIAN,
                defaults={"school": app.school, "assigned_by": app.reviewed_by},
            )
            if not role_assignment.active:
                role_assignment.active = True
                role_assignment.save(update_fields=["active"])
        child_account_setups = {
            (setup.first_name.casefold(), setup.last_name.casefold()): setup
            for setup in family.child_accounts.select_for_update().all()
        }
        for child_data in family.children:
            child_key = (
                child_data["first_name"].casefold(),
                child_data["last_name"].casefold(),
            )
            child_setup = child_account_setups.get(child_key)
            child_user = None
            if child_setup:
                child_user, child_user_created = UserAccount.objects.get_or_create(
                    email=child_setup.email,
                    defaults={
                        "password": child_setup.password_hash,
                        "email_verified_at": app.email_verified_at or timezone.now(),
                        "is_active": True,
                    },
                )
                if not child_user_created and child_user.is_active:
                    raise ValidationError(
                        f"Für {child_setup.first_name} besteht bereits ein aktiver Zugang."
                    )
                if not child_user_created:
                    child_user.password = child_setup.password_hash
                    child_user.email_verified_at = app.email_verified_at or timezone.now()
                    child_user.is_active = True
                    child_user.save(
                        update_fields=["password", "email_verified_at", "is_active"]
                    )
            child = Person.objects.create(
                user=child_user,
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
            if child_setup:
                child_setup.activated_user = child_user
                child_setup.save(update_fields=["activated_user"])
                RegistrationApplication.objects.filter(
                    email__iexact=child_setup.email,
                    status=RegistrationApplication.Status.EMAIL_PENDING,
                    family_request__isnull=True,
                ).update(
                    family_request=family,
                    status=RegistrationApplication.Status.ACTIVATED,
                    email_verified_at=app.email_verified_at or timezone.now(),
                )
                AuditEvent.objects.create(
                    actor=user,
                    action="family.child_account.activated",
                    target_type="user",
                    target_id=str(child_user.pk),
                )
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
            if existing_guardian_person:
                GuardianChildRelationship.objects.update_or_create(
                    guardian_person=existing_guardian_person,
                    student_person=child,
                    defaults={
                        "relationship_type": (
                            access_code.existing_guardian_relationship_type
                            or RelationshipType.GUARDIAN
                        ),
                        "is_legal_guardian": True,
                        "may_view_student_profile": True,
                        "may_manage_profile": True,
                        "may_manage_general_consents": True,
                        "may_manage_photo_consents": True,
                        "may_manage_biometric_consents": True,
                        "valid_from": timezone.localdate(),
                        "valid_until": None,
                        "status": RelationshipStatus.VERIFIED,
                        "verified_by": app.reviewed_by,
                        "verified_at": timezone.now(),
                    },
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
        if family.access_code.max_uses > 1 and existing_guardian:
            family.access_code.existing_guardian = None
            family.access_code.existing_guardian_relationship_type = ""
            family.access_code.save(
                update_fields=["existing_guardian", "existing_guardian_relationship_type"]
            )
        if family.access_code.use_count >= family.access_code.max_uses:
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
