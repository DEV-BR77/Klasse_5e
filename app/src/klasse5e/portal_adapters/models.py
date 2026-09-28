from django.conf import settings
from django.db import models

from klasse5e.core.models import Person, School, SchoolClass


class PortalAdapterDefinition(models.Model):
    """Reusable, school-independent definition of a reviewed provider."""

    class IntegrationType(models.TextChoices):
        IMPORT = "import", "Datenimport"
        EXTERNAL = "external", "Externes Portal"
        CUSTOM = "custom", "Individuelle Schnittstelle"

    provider = models.CharField(max_length=32, unique=True)
    label = models.CharField(max_length=120)
    hint = models.CharField(max_length=300, blank=True)
    default_url = models.URLField(blank=True)
    integration_type = models.CharField(
        max_length=16, choices=IntegrationType.choices, default=IntegrationType.IMPORT
    )
    is_published = models.BooleanField(default=False)
    is_technically_reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("label",)

    def __str__(self):
        return self.label


class PortalAdapterDefinitionModule(models.Model):
    """Reusable module contract offered by an adapter definition."""

    class AccessModel(models.TextChoices):
        NONE = "none", "Ohne persönlichen Zugang"
        CHILD = "child", "Zugang je Kind"
        FAMILY = "family", "Zugang je Familie"
        EXTERNAL = "external", "Nur extern öffnen"

    definition = models.ForeignKey(
        PortalAdapterDefinition, on_delete=models.CASCADE, related_name="modules"
    )
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    access_model = models.CharField(
        max_length=16, choices=AccessModel.choices, default=AccessModel.NONE
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ("label",)
        constraints = [
            models.UniqueConstraint(
                fields=["definition", "key"], name="unique_adapter_definition_module"
            )
        ]

    def __str__(self):
        return f"{self.definition} · {self.label}"


class PortalAdapter(models.Model):
    class Provider(models.TextChoices):
        WEBUNTIS = "webuntis", "WebUntis"
        ITSLEARNING = "itslearning", "itslearning"
        MENSAMAX = "mensamax", "MensaMax"
        DSBMOBILE = "dsbmobile", "DSBmobile"
        MUNDO = "mundo", "MUNDO Schule"
        WIR_LERNEN_ONLINE = "wirlernenonline", "WirLernenOnline"
        SCHULMANAGER = "schulmanager", "Schulmanager Online"
        WOBILA_BBB = "wobila-bbb", "BBB Wobila"
        WOBILA_MAIL = "wobila-mail", "Mail Wobila"
        CUSTOM = "custom", "Eigenes Portal"

    # An adapter is one concrete, reviewed integration for exactly one school.
    # Provider is the reusable adapter code; endpoint and identifiers below are
    # integration data and must never be shared implicitly between schools.
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="portal_adapters"
    )
    definition = models.ForeignKey(
        PortalAdapterDefinition,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="school_integrations",
    )
    provider = models.CharField(max_length=32, choices=Provider.choices)
    name = models.CharField(max_length=120)
    base_url = models.URLField(blank=True)
    project_identifier = models.CharField(max_length=120, blank=True)
    institution_identifier = models.CharField(max_length=120, blank=True)
    school_number = models.CharField(max_length=40, blank=True)
    configuration_note = models.TextField(blank=True, max_length=1200)
    is_enabled = models.BooleanField(default=True)
    requires_child_credentials = models.BooleanField(default=False)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_check_status = models.CharField(max_length=32, blank=True)
    last_check_message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "provider")
        constraints = [
            models.UniqueConstraint(
                fields=["school", "provider", "name"],
                name="unique_portal_adapter_integration",
            )
        ]

    def __str__(self):
        return self.name


class PortalAdapterModule(models.Model):
    class Status(models.TextChoices):
        NOT_CONFIGURED = "not_configured", "Noch nicht angebunden"
        READY = "ready", "Bereit zur Anbindung"
        ACTIVE = "active", "Aktiv"
        ERROR = "error", "Prüfung fehlgeschlagen"

    adapter = models.ForeignKey(PortalAdapter, on_delete=models.CASCADE, related_name="modules")
    definition_module = models.ForeignKey(
        PortalAdapterDefinitionModule,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="school_modules",
    )
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    is_enabled = models.BooleanField(default=False)
    requires_child_credentials = models.BooleanField(
        default=False,
        help_text="Für dieses Modul hinterlegen Familien einen persönlichen Schulzugang beim Kind.",
    )
    access_model = models.CharField(
        max_length=16,
        choices=PortalAdapterDefinitionModule.AccessModel.choices,
        default=PortalAdapterDefinitionModule.AccessModel.NONE,
        help_text="Fachliches Zugangsmodell für Familien und Kinder.",
    )
    available_to_classes = models.ManyToManyField(
        SchoolClass,
        blank=True,
        related_name="available_portal_adapter_modules",
        help_text="Leer bedeutet: für alle aktiven Klassen dieser Schule verfügbar.",
    )
    configuration_note = models.TextField(blank=True, max_length=1200)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NOT_CONFIGURED
    )
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_sync_message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("label",)
        constraints = [
            models.UniqueConstraint(
                fields=["adapter", "key"], name="unique_portal_adapter_module_key"
            )
        ]

    def __str__(self):
        return f"{self.adapter} · {self.label}"


class ChildModuleConnection(models.Model):
    """A family's opt-in to one school-approved module for one child.

    The record deliberately contains no credential fields. Concrete adapters own
    their encrypted secrets, while this model only controls whether a parent
    wants the already school-approved function to appear for the child.
    """

    class ConnectionState(models.TextChoices):
        NOT_CONNECTED = "not_connected", "Noch nicht verbunden"
        CREDENTIALS_NEEDED = "credentials_needed", "Zugangsdaten hinterlegen"
        CONNECTED = "connected", "Verbunden"
        EXTERNAL = "external", "Extern öffnen"

    student = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="module_connections"
    )
    module = models.ForeignKey(
        PortalAdapterModule, on_delete=models.CASCADE, related_name="child_connections"
    )
    is_enabled = models.BooleanField(default=False)
    connection_state = models.CharField(
        max_length=24, choices=ConnectionState.choices, default=ConnectionState.NOT_CONNECTED
    )
    configured_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    configured_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "module"], name="unique_child_portal_module"
            )
        ]

    def __str__(self):
        return f"{self.student} · {self.module}"


class SchoolmanagerConnection(models.Model):
    """Encrypted personal credentials for the read-only Schulmanager adapter."""

    class Status(models.TextChoices):
        NOT_TESTED = "not_tested", "Noch nicht geprüft"
        OK = "ok", "Verbindung eingerichtet"
        INVALID = "invalid", "Zugangsdaten ungültig"
        ERROR = "error", "Verbindung fehlerhaft"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schoolmanager_connections"
    )
    student = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="schoolmanager_connections")
    username_encrypted = models.BinaryField()
    password_encrypted = models.BinaryField()
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.NOT_TESTED)
    status_detail = models.CharField(max_length=160, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "student"], name="unique_schoolmanager_user_student")
        ]
