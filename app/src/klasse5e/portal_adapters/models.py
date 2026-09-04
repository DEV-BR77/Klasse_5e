from django.db import models

from klasse5e.core.models import School


class PortalAdapter(models.Model):
    class Provider(models.TextChoices):
        MENSAMAX = "mensamax", "MensaMax"
        DSBMOBILE = "dsbmobile", "DSBmobile"
        MUNDO = "mundo", "MUNDO Schule"
        WIR_LERNEN_ONLINE = "wirlernenonline", "WirLernenOnline"
        WOBILA_BBB = "wobila-bbb", "BBB Wobila"
        WOBILA_MAIL = "wobila-mail", "Mail Wobila"
        CUSTOM = "custom", "Eigenes Portal"

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="portal_adapters")
    provider = models.CharField(max_length=32, choices=Provider.choices)
    name = models.CharField(max_length=120)
    base_url = models.URLField(blank=True)
    project_identifier = models.CharField(max_length=120, blank=True)
    institution_identifier = models.CharField(max_length=120, blank=True)
    school_number = models.CharField(max_length=40, blank=True)
    configuration_note = models.TextField(blank=True, max_length=1200)
    is_enabled = models.BooleanField(default=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_check_status = models.CharField(max_length=32, blank=True)
    last_check_message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("school__name", "provider", "name")
        constraints = [
            models.UniqueConstraint(
                fields=["school", "provider", "name"], name="unique_portal_adapter_per_school"
            )
        ]

    def __str__(self):
        return f"{self.school} · {self.name}"


class PortalAdapterModule(models.Model):
    class Status(models.TextChoices):
        NOT_CONFIGURED = "not_configured", "Noch nicht angebunden"
        READY = "ready", "Bereit zur Anbindung"
        ACTIVE = "active", "Aktiv"
        ERROR = "error", "Prüfung fehlgeschlagen"

    adapter = models.ForeignKey(PortalAdapter, on_delete=models.CASCADE, related_name="modules")
    key = models.SlugField(max_length=80)
    label = models.CharField(max_length=120)
    description = models.CharField(max_length=300, blank=True)
    is_enabled = models.BooleanField(default=False)
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
