import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from klasse5e.core.models import SchoolClass, SchoolYear
from klasse5e.events.models import Event


class ChatRoom(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    event = models.OneToOneField(Event, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.event_id and (
            self.event.school_class_id != self.school_class_id
            or self.event.school_year_id != self.school_year_id
        ):
            raise ValidationError("event_class_mismatch")


class ChatMessage(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reply_to = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="chat_mentions"
    )
    body = models.CharField(max_length=2000)
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
