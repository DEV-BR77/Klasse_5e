import hashlib
import secrets
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class UserAccountManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("email_required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.update(is_staff=True, is_superuser=True)
        return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserAccountManager()


class Visibility(models.TextChoices):
    SELF = "self", "Nur eigene Person"
    ADMINS = "admins", "Administratoren"
    TEACHERS = "teachers", "Klassenlehrer und Administratoren"
    MEMBERS = "members", "Aktive Klassenmitglieder"
    HIDDEN = "hidden", "Nicht sichtbar"


class Person(models.Model):
    user = models.OneToOneField(UserAccount, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, blank=True)
    other_contact = models.CharField(max_length=200, blank=True)
    street = models.CharField(max_length=180, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=120, blank=True)
    profile_photo = models.ImageField(upload_to="profiles/opaque/", blank=True)
    email_visibility = models.CharField(
        max_length=16, choices=Visibility, default=Visibility.HIDDEN
    )
    phone_visibility = models.CharField(
        max_length=16, choices=Visibility, default=Visibility.HIDDEN
    )
    relationship_visibility = models.CharField(
        max_length=16, choices=Visibility, default=Visibility.HIDDEN
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Household(models.Model):
    label = models.CharField(max_length=120)
    members = models.ManyToManyField(Person, related_name="households")


class SchoolYear(models.Model):
    label = models.CharField(max_length=32, unique=True)
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_active = models.BooleanField(default=False)

    def clean(self):
        if self.ends_on <= self.starts_on:
            raise ValidationError("Das Schuljahr muss nach seinem Beginn enden.")


class School(models.Model):
    source_id = models.CharField(max_length=80, null=True, blank=True, unique=True)
    source_name = models.CharField(max_length=120, blank=True)
    source_imported_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=160)
    search_name = models.CharField(max_length=200, blank=True, db_index=True)
    short_name = models.CharField(max_length=64, blank=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    address = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=10, blank=True, db_index=True)
    city = models.CharField(max_length=120, blank=True, db_index=True)
    federal_state = models.CharField(max_length=80, blank=True, db_index=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    school_type = models.CharField(max_length=120, blank=True, db_index=True)
    legal_status = models.CharField(max_length=120, blank=True, db_index=True)
    provider = models.CharField(max_length=200, blank=True, db_index=True)
    fax = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=80, blank=True)
    director = models.CharField(max_length=160, blank=True)
    source_raw = models.JSONField(default=dict, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_valid = models.BooleanField(default=False)
    possible_duplicate_group = models.CharField(max_length=64, blank=True, db_index=True)
    logo = models.ImageField(upload_to="branding/schools/", blank=True)
    enabled_features = models.JSONField(default=list, blank=True)
    visible_menu_items = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.short_name or self.name


class RegistrationApplication(models.Model):
    class Status(models.TextChoices):
        EMAIL_PENDING = "email_pending", "E-Mail-Prüfung ausstehend"
        REVIEW_PENDING = "review_pending", "Wartet auf Prüfung"
        APPROVED = "approved", "Freigegeben"
        REJECTED = "rejected", "Abgelehnt"
        ACTIVATED = "activated", "Aktiviert"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=256)
    status = models.CharField(max_length=24, choices=Status, default=Status.EMAIL_PENDING)
    email_token_hash = models.CharField(max_length=64, unique=True)
    email_token_expires_at = models.DateTimeField()
    email_verified_at = models.DateTimeField(null=True, blank=True)
    school = models.ForeignKey("School", null=True, blank=True, on_delete=models.PROTECT)
    school_class = models.ForeignKey("SchoolClass", null=True, blank=True, on_delete=models.PROTECT)
    reviewed_by = models.ForeignKey(
        UserAccount, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_registrations"
    )
    review_reason = models.CharField(max_length=500, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def issue(cls, *, email, first_name, last_name, password_hash, lifetime=timedelta(hours=24)):
        token = secrets.token_urlsafe(32)
        item = cls.objects.create(
            email=email.casefold(),
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            email_token_hash=hashlib.sha256(token.encode()).hexdigest(),
            email_token_expires_at=timezone.now() + lifetime,
        )
        return item, token


class ActivationGrant(models.Model):
    application = models.OneToOneField(RegistrationApplication, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def issue(cls, application, lifetime=timedelta(hours=24)):
        token = secrets.token_urlsafe(32)
        grant, _ = cls.objects.update_or_create(
            application=application,
            defaults={
                "token_hash": hashlib.sha256(token.encode()).hexdigest(),
                "expires_at": timezone.now() + lifetime,
                "used_at": None,
                "revoked_at": None,
            },
        )
        return grant, token


class SchoolClass(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="classes"
    )
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=64, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    display_name = models.CharField(max_length=100, blank=True)
    logo = models.ImageField(upload_to="branding/classes/", blank=True)
    enabled_features = models.JSONField(default=list, blank=True)
    visible_menu_items = models.JSONField(default=list, blank=True)
    grade_level = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=24, default="active")
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school", "code", "school_year"], name="unique_school_class_year"
            )
        ]


class ClassDomain(models.Model):
    school_class = models.OneToOneField(
        SchoolClass, on_delete=models.CASCADE, related_name="domain"
    )
    hostname = models.CharField(max_length=253, unique=True)
    is_reserved_exception = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from .school_domains import validate_class_hostname

        validate_class_hostname(self.hostname, reserved_exception=self.is_reserved_exception)


class BrandingAsset(models.Model):
    class Kind(models.TextChoices):
        LOGO = "logo", "Logo"
        HERO = "hero", "Titelbild"

    class Status(models.TextChoices):
        ACTIVE = "active", "Aktiv"
        REMOVED = "removed", "Entfernt"

    school = models.ForeignKey(
        School, null=True, blank=True, on_delete=models.CASCADE, related_name="branding_assets"
    )
    school_class = models.ForeignKey(
        SchoolClass,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="branding_assets",
    )
    kind = models.CharField(max_length=12, choices=Kind)
    image = models.ImageField(upload_to="branding/opaque/")
    preview = models.ImageField(upload_to="branding/opaque/", blank=True)
    alt_text = models.CharField(max_length=180)
    rights_notice = models.CharField(max_length=240, blank=True)
    publication_rights_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=Status, default=Status.ACTIVE)
    created_by = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(school__isnull=False, school_class__isnull=True) | models.Q(school__isnull=True, school_class__isnull=False)),
                name="branding_exactly_one_scope",
            ),
            models.UniqueConstraint(
                fields=["school", "kind"],
                condition=models.Q(status="active", school__isnull=False),
                name="one_active_school_branding_kind",
            ),
            models.UniqueConstraint(
                fields=["school_class", "kind"],
                condition=models.Q(status="active", school_class__isnull=False),
                name="one_active_class_branding_kind",
            ),
        ]


class PortalConfigurationKey(models.Model):
    class ValueType(models.TextChoices):
        BOOLEAN = "boolean", "Ja/Nein"
        STRING = "string", "Text"

    key = models.SlugField(unique=True)
    version = models.PositiveSmallIntegerField(default=1)
    value_type = models.CharField(max_length=12, choices=ValueType)
    default_value = models.JSONField()
    school_override_allowed = models.BooleanField(default=False)
    class_override_allowed = models.BooleanField(default=False)
    active = models.BooleanField(default=True)


class PortalConfigurationValue(models.Model):
    key = models.ForeignKey(PortalConfigurationKey, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, null=True, blank=True, on_delete=models.CASCADE)
    value = models.JSONField()
    updated_by = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(school__isnull=True, school_class__isnull=True) | models.Q(school__isnull=False, school_class__isnull=True) | models.Q(school__isnull=True, school_class__isnull=False)),
                name="configuration_at_most_one_scope",
            ),
            models.UniqueConstraint(fields=["key", "school", "school_class"], name="unique_configuration_scope"),
        ]


class PortalModule(models.Model):
    class Stability(models.TextChoices):
        STABLE = "stable", "Stabil"
        BETA = "beta", "Beta"
        EXPERIMENTAL = "experimental", "Experimentell"

    key = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    stability = models.CharField(max_length=16, choices=Stability)
    default_enabled = models.BooleanField(default=False)
    dependencies = models.JSONField(default=list, blank=True)
    last_successful_test_at = models.DateTimeField(null=True, blank=True)


class PortalModuleOverride(models.Model):
    module = models.ForeignKey(PortalModule, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, null=True, blank=True, on_delete=models.CASCADE)
    enabled = models.BooleanField()
    reason = models.CharField(max_length=300, blank=True)
    updated_by = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(school__isnull=True, school_class__isnull=True) | models.Q(school__isnull=False, school_class__isnull=True) | models.Q(school__isnull=True, school_class__isnull=False)),
                name="module_override_at_most_one_scope",
            ),
            models.UniqueConstraint(fields=["module", "school", "school_class"], name="unique_module_override_scope"),
        ]


class LogoRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        SUBMITTED = "submitted", "Eingereicht"
        REVIEW = "review", "In Prüfung"
        QUESTION = "question", "Rückfrage"
        OFFER = "offer", "Angebot"
        COMMISSIONED = "commissioned", "Beauftragt"
        DELIVERED = "delivered", "Geliefert"
        REJECTED = "rejected", "Abgelehnt"
        CANCELLED = "cancelled", "Storniert"

    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, null=True, blank=True, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    desired_text = models.CharField(max_length=160)
    colors = models.CharField(max_length=300, blank=True)
    motifs = models.CharField(max_length=500, blank=True)
    style = models.CharField(max_length=300, blank=True)
    reference_notes = models.CharField(max_length=1000, blank=True)
    transparent_background = models.BooleanField(default=True)
    intended_uses = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status, default=Status.DRAFT)
    admin_notes = models.CharField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(school__isnull=False, school_class__isnull=True) | models.Q(school__isnull=True, school_class__isnull=False)),
                name="logo_request_exactly_one_scope",
            )
        ]


class StudentProfile(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    profile_photo_reference = models.CharField(max_length=200, blank=True)


class MembershipStatus(models.TextChoices):
    ACTIVE = "active", "Aktiv"
    ENDED = "ended", "Beendet"
    SUSPENDED = "suspended", "Gesperrt"


class ClassMembership(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=16, choices=MembershipStatus, default=MembershipStatus.ACTIVE
    )
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["school_class", "person"], name="unique_class_person")
        ]

    def is_current(self, on=None):
        on = on or timezone.localdate()
        return (
            self.status == MembershipStatus.ACTIVE
            and self.valid_from <= on
            and (self.valid_until is None or self.valid_until >= on)
            and self.school_class.school_year.starts_on
            <= on
            <= self.school_class.school_year.ends_on
        )


class Role(models.TextChoices):
    PRIMARY_ADMIN = "primary_admin", "Hauptadministrator"
    SCHOOL_ADMIN = "school_admin", "Schuladministrator"
    CLASS_ADMIN = "class_admin", "Klassenadministrator"
    DEPUTY_ADMIN = "deputy_admin", "Stellvertretender Administrator"
    TEACHER = "teacher", "Klassenlehrer"
    EDITOR = "editor", "Redakteur"
    MODERATOR = "moderator", "Moderator"
    ORGANIZER = "organizer", "Organisator"
    GUARDIAN = "guardian", "Elternteil"
    PUSH_SUBSCRIBER = "push_subscriber", "Benachrichtigungs-Abonnent"


class RoleAssignment(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, null=True, blank=True, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, choices=Role)
    active = models.BooleanField(default=True)
    assigned_by = models.ForeignKey(
        UserAccount, null=True, on_delete=models.SET_NULL, related_name="roles_assigned"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "school_class", "role"], name="unique_user_class_role"
            )
        ]


class RelationshipType(models.TextChoices):
    MOTHER = "mother", "Mutter"
    FATHER = "father", "Vater"
    GUARDIAN = "guardian", "Sorgeberechtigte Person"
    FOSTER = "foster", "Pflegeelternteil"
    STEP = "step", "Stiefelternteil"
    OTHER = "other", "Sonstige autorisierte Bezugsperson"


class RelationshipStatus(models.TextChoices):
    PENDING = "pending", "Unbestätigt"
    VERIFIED = "verified", "Bestätigt"
    REVOKED = "revoked", "Widerrufen"


class GuardianChildRelationship(models.Model):
    guardian_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="guardian_relationships"
    )
    student_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="student_relationships"
    )
    relationship_type = models.CharField(max_length=24, choices=RelationshipType)
    is_legal_guardian = models.BooleanField(default=False)
    may_view_student_profile = models.BooleanField(default=False)
    may_manage_profile = models.BooleanField(default=False)
    may_manage_general_consents = models.BooleanField(default=False)
    may_manage_photo_consents = models.BooleanField(default=False)
    may_manage_biometric_consents = models.BooleanField(default=False)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=RelationshipStatus, default=RelationshipStatus.PENDING
    )
    verified_by = models.ForeignKey(UserAccount, null=True, blank=True, on_delete=models.SET_NULL)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["guardian_person", "student_person"], name="unique_guardian_student"
            ),
            models.CheckConstraint(
                condition=~models.Q(guardian_person=models.F("student_person")),
                name="guardian_not_student",
            ),
        ]

    def is_current(self, on=None):
        on = on or timezone.localdate()
        return (
            self.status == RelationshipStatus.VERIFIED
            and self.verified_at is not None
            and self.valid_from <= on
            and (self.valid_until is None or self.valid_until >= on)
        )


class Invitation(models.Model):
    email = models.EmailField()
    token_hash = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def issue(cls, email, invited_by, lifetime=timedelta(days=7)):
        token = secrets.token_urlsafe(32)
        invitation = cls.objects.create(
            email=email.casefold(),
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=timezone.now() + lifetime,
            invited_by=invited_by,
        )
        return invitation, token

    @classmethod
    def consume(cls, token):
        digest = hashlib.sha256(token.encode()).hexdigest()
        invitation = cls.objects.filter(token_hash=digest).first()
        if invitation is None or invitation.used_at or invitation.expires_at <= timezone.now():
            return None
        invitation.used_at = timezone.now()
        invitation.save(update_fields=["used_at"])
        return invitation


class ConsentCategory(models.TextChoices):
    GENERAL = "general", "Allgemein"
    PHOTO = "photo", "Foto"
    BIOMETRIC = "biometric", "Biometrie"


class ConsentType(models.Model):
    key = models.SlugField(unique=True)
    label = models.CharField(max_length=160)
    category = models.CharField(max_length=16, choices=ConsentCategory)
    purpose = models.TextField()
    recipients = models.TextField()


class ConsentTextVersion(models.Model):
    consent_type = models.ForeignKey(ConsentType, on_delete=models.PROTECT)
    version = models.CharField(max_length=32)
    text = models.TextField(help_text="Fachlicher Entwurf bis zur rechtlichen Freigabe")
    effective_from = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["consent_type", "version"], name="unique_consent_version"
            )
        ]


class ConsentDecision(models.Model):
    class Decision(models.TextChoices):
        GRANTED = "granted", "Zugestimmt"
        DENIED = "denied", "Abgelehnt"
        REVOKED = "revoked", "Widerrufen"

    consent_type = models.ForeignKey(ConsentType, on_delete=models.PROTECT)
    text_version = models.ForeignKey(ConsentTextVersion, on_delete=models.PROTECT)
    subject_person = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="consents_about"
    )
    deciding_person = models.ForeignKey(
        Person, on_delete=models.PROTECT, related_name="consent_decisions"
    )
    decision = models.CharField(max_length=16, choices=Decision)
    decided_at = models.DateTimeField(default=timezone.now)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=64, default="web")


class AuditEvent(models.Model):
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(UserAccount, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=80)
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ["-occurred_at"]


class PushSubscription(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    endpoint_hash = models.CharField(max_length=64, unique=True)
    endpoint = models.TextField()
    p256dh = models.TextField()
    auth = models.TextField()
    enabled = models.BooleanField(default=True)
    device_label = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def from_values(cls, user, endpoint, p256dh, auth, device_label=""):
        digest = hashlib.sha256(endpoint.encode()).hexdigest()
        existing = cls.objects.filter(endpoint_hash=digest).first()
        if existing is not None and existing.user_id != user.pk:
            raise ValidationError("Dieses Push-Gerät gehört zu einem anderen Konto.")
        return cls.objects.update_or_create(
            endpoint_hash=digest,
            defaults={
                "user": user,
                "endpoint": endpoint,
                "p256dh": p256dh,
                "auth": auth,
                "enabled": True,
                "device_label": device_label[:80],
            },
        )


class UserNotification(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="notifications")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    category = models.SlugField(max_length=40)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=128)
    revision = models.CharField(max_length=64)
    title = models.CharField(max_length=160)
    summary = models.CharField(max_length=240, blank=True)
    target_url = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "school_class", "object_type", "object_id", "revision"],
                name="unique_personal_notification_revision",
            )
        ]
        indexes = [models.Index(fields=["user", "school_class", "read_at"])]


class PushPreference(models.Model):
    """Per-category opt-in. Creating a subscription never enables a category."""

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    key = models.SlugField(max_length=40)
    enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "key"], name="unique_push_preference")
        ]


class OnboardingState(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    current_step = models.PositiveSmallIntegerField(default=1)
    identity_confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_policy_version = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class TutorialState(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    current_step = models.PositiveSmallIntegerField(default=1)
    completed_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
