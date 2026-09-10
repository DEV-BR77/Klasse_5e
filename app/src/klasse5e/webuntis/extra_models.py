import hashlib
import secrets

from django.db import models

from klasse5e.portal_adapters.models import PortalAdapter

from .models import WebUntisConnection


class WebUntisSubjectMapping(models.Model):
    adapter = models.ForeignKey(
        PortalAdapter, null=True, blank=True, on_delete=models.CASCADE, related_name="webuntis_subject_mappings"
    )
    code = models.CharField(max_length=32)
    label = models.CharField(max_length=120)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["adapter", "code"], name="unique_webuntis_subject_mapping_integration"
            )
        ]

    def __str__(self):
        return f"{self.code}: {self.label}"


class WebUntisTeacherMapping(models.Model):
    adapter = models.ForeignKey(
        PortalAdapter, null=True, blank=True, on_delete=models.CASCADE, related_name="webuntis_teacher_mappings"
    )
    code = models.CharField(max_length=32)
    label = models.CharField(max_length=120)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["adapter", "code"], name="unique_webuntis_teacher_mapping_integration"
            )
        ]

    def __str__(self):
        return f"{self.code}: {self.label}"


class WebUntisCalendarSubscription(models.Model):
    connection = models.ForeignKey(
        WebUntisConnection, on_delete=models.CASCADE, related_name="calendar_subscriptions"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, connection):
        token = secrets.token_urlsafe(32)
        item = cls.objects.create(
            connection=connection,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
        )
        return item, token

    @classmethod
    def resolve(cls, token):
        return cls.objects.select_related("connection", "connection__student").filter(
            token_hash=hashlib.sha256(token.encode()).hexdigest(), active=True
        ).first()
