import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from klasse5e.core.models import SchoolClass, SchoolYear
from klasse5e.events.models import Event


class ChatRetentionCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    retention_days = models.PositiveSmallIntegerField(default=30)
    automatic_deletion_enabled = models.BooleanField(default=False)
    intended_for_events = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-intended_for_events", "retention_days", "name"]

    def __str__(self):
        if not self.automatic_deletion_enabled:
            return f"{self.name} (keine automatische Löschung)"
        return f"{self.name} ({self.retention_days} Tage)"


class ChatRoom(models.Model):
    class Audience(models.TextChoices):
        GENERAL = "general", "Alle Klassenmitglieder"
        GUARDIANS = "guardians", "Nur Eltern"
        STUDENTS = "students", "Nur Schülerinnen und Schüler"
        PARENT_REPRESENTATIVES = "parent_representatives", "Nur Elternvertretung"

    class Appearance(models.TextChoices):
        STANDARD = "standard", "Standard"
        CLASSIC = "classic", "Klassische Schultafel"
        MODERN = "modern", "Moderne Tafel"
        MATH = "math", "Mathe-Tafel"

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    event = models.OneToOneField(Event, null=True, blank=True, on_delete=models.CASCADE)
    retention_category = models.ForeignKey(ChatRetentionCategory, null=True, blank=True, on_delete=models.PROTECT)
    title = models.CharField(max_length=120)
    audience = models.CharField(
        max_length=24, choices=Audience.choices, default=Audience.GENERAL
    )
    appearance = models.CharField(
        max_length=16, choices=Appearance.choices, default=Appearance.STANDARD
    )
    parent_representative_chat = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school_class"],
                condition=models.Q(parent_representative_chat=True),
                name="unique_parent_representative_chat_per_class",
            ),
        ]

    def clean(self):
        if self.event_id and (
            self.event.school_class_id != self.school_class_id
            or self.event.school_year_id != self.school_year_id
        ):
            raise ValidationError("event_class_mismatch")


class DirectConversation(models.Model):
    room = models.OneToOneField(
        ChatRoom, on_delete=models.CASCADE, related_name="direct_conversation"
    )
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    participant_one = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="direct_conversations_as_one",
    )
    participant_two = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="direct_conversations_as_two",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "participant_one", "participant_two"],
                name="unique_direct_conversation_pair_class",
            ),
            models.CheckConstraint(
                condition=models.Q(participant_one__lt=models.F("participant_two")),
                name="direct_conversation_ordered_participants",
            ),
        ]

    def clean(self):
        if self.participant_one_id and self.participant_two_id:
            if self.participant_one_id >= self.participant_two_id:
                raise ValidationError("direct_participants_must_be_ordered")
        if self.room_id and self.school_class_id:
            if self.room.school_class_id != self.school_class_id:
                raise ValidationError("direct_conversation_class_mismatch")

    def other_participant(self, user):
        if user.pk == self.participant_one_id:
            return self.participant_two
        if user.pk == self.participant_two_id:
            return self.participant_one
        return None


class ChatMessage(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="chat_mentions"
    )
    body = models.CharField(max_length=2000, blank=True)
    attachment = models.FileField(upload_to="chat/opaque/", blank=True)
    attachment_name = models.CharField(max_length=180, blank=True)
    attachment_content_type = models.CharField(max_length=80, blank=True)
    attachment_safety_status = models.CharField(
        max_length=16,
        choices=[
            ("not_applicable", "Nicht erforderlich"),
            ("pending", "Prüfung ausstehend"),
            ("approved", "Freigegeben"),
            ("blocked", "Gesperrt"),
        ],
        default="not_applicable",
    )
    language_filter_hits = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    hidden_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="hidden_chat_messages",
    )

    def clean(self):
        if self.reply_to_id and self.reply_to.room_id != self.room_id:
            raise ValidationError("reply_room_mismatch")


class ChatReadState(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["room", "user"], name="unique_chat_read_state")
        ]


class ChatReport(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.CharField(
        max_length=32,
        choices=[
            ("inappropriate", "Ungeeignet"),
            ("privacy", "Datenschutz"),
            ("other", "Sonstiges"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["message", "reporter"], name="unique_chat_report")
        ]


class ChatPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    push_enabled = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "room"], name="unique_chat_preference")
        ]
