from django.conf import settings
from django.db import models
from django.utils import timezone

from klasse5e.core.models import Person


class ConnectionStatus(models.TextChoices):
    NOT_TESTED = "not_tested", "Noch nicht geprüft"
    OK = "ok", "Verbindung eingerichtet"
    INVALID = "invalid", "Zugangsdaten ungültig"
    MFA_REQUIRED = "mfa_required", "MFA oder SSO erforderlich"
    ERROR = "error", "Verbindung fehlerhaft"
    REMOVED = "removed", "Verbindung entfernt"


class DataScope(models.TextChoices):
    CLASS = "class", "Klassenweit"
    PERSONAL = "personal", "Persönlich"


class WebUntisConnection(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="webuntis_connections"
    )
    student = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="webuntis_connections"
    )
    server = models.CharField(max_length=255, default="thgwob.webuntis.com")
    school = models.CharField(max_length=80, default="thgwob")
    username_encrypted = models.BinaryField()
    password_encrypted = models.BinaryField()
    external_student_id = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=24, choices=ConnectionStatus, default=ConnectionStatus.NOT_TESTED
    )
    status_detail = models.CharField(max_length=160, blank=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_successful_sync_at = models.DateTimeField(null=True, blank=True)
    sync_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "student"], name="unique_webuntis_user_student")
        ]

    def mark_checked(self, status, detail=""):
        self.status = status
        self.status_detail = detail[:160]
        self.last_checked_at = timezone.now()
        self.save(update_fields=["status", "status_detail", "last_checked_at", "updated_at"])


class FeatureKey(models.TextChoices):
    TIMETABLE = "timetable", "Persönlicher Stundenplan"
    TIMETABLE_EXTENDED = "timetable_extended", "Erweiterte Stundeninformationen"
    SUBSTITUTIONS = "substitutions", "Stundenplanänderungen und Vertretungen"
    EXAMS = "exams", "Prüfungen"
    HOMEWORK = "homework", "Hausaufgaben"
    HOLIDAYS = "holidays", "Ferien"
    TIMEGRID = "timegrid", "Stundenraster"
    SUBJECTS = "subjects", "Fächer"
    ROOMS = "rooms", "Räume"
    TEACHERS = "teachers", "Lehrkräfte"
    SCHOOLYEARS = "schoolyears", "Schuljahre"
    STATUSDATA = "statusdata", "Status- und Änderungshinweise"
    CLASS_EVENTS = "class_reg_events", "Klassenbucheinträge (nicht aktiviert)"
    CLASS_EVENT_CATEGORIES = "class_reg_categories", "Klassenbuchkategorien (nicht aktiviert)"
    CLASS_EVENT_GROUPS = (
        "class_reg_category_groups",
        "Klassenbuch-Kategoriegruppen (nicht aktiviert)",
    )


class FeatureState(models.TextChoices):
    AVAILABLE = "available", "Verfügbar"
    NOT_AUTHORIZED = "not_authorized", "Nicht berechtigt"
    UNSUPPORTED = "unsupported", "Nicht durch diesen Adapter unterstützt"
    NOT_CHECKED = "not_checked", "Noch nicht geprüft"


class WebUntisFeaturePreference(models.Model):
    connection = models.ForeignKey(
        WebUntisConnection, on_delete=models.CASCADE, related_name="features"
    )
    key = models.CharField(max_length=40, choices=FeatureKey)
    enabled = models.BooleanField(default=False)
    state = models.CharField(max_length=24, choices=FeatureState, default=FeatureState.NOT_CHECKED)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["connection", "key"], name="unique_webuntis_feature")
        ]


class WebUntisLesson(models.Model):
    connection = models.ForeignKey(
        WebUntisConnection, on_delete=models.CASCADE, related_name="lessons"
    )
    external_fingerprint = models.CharField(max_length=128)
    subject_code = models.CharField(max_length=32, blank=True)
    starts_at = models.DateTimeField()
    teacher_code = models.CharField(max_length=32, blank=True)
    ends_at = models.DateTimeField()
    subject = models.CharField(max_length=100, blank=True)
    room = models.CharField(max_length=60, blank=True)
    teacher_label = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=24, default="regular")
    source_updated_at = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=12, choices=DataScope, default=DataScope.PERSONAL)
    delete_after = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "external_fingerprint"],
                name="unique_webuntis_lesson_fingerprint",
            )
        ]


class WebUntisHomework(models.Model):
    connection = models.ForeignKey(
        WebUntisConnection, on_delete=models.CASCADE, related_name="homework"
    )
    external_fingerprint = models.CharField(max_length=128)
    subject = models.CharField(max_length=100, blank=True)
    assigned_on = models.DateField(null=True, blank=True)
    due_on = models.DateField(null=True, blank=True)
    text = models.TextField(blank=True)
    source_status = models.CharField(max_length=40, blank=True)
    fetched_at = models.DateTimeField(auto_now=True)
    visibility = models.CharField(max_length=12, choices=DataScope, default=DataScope.PERSONAL)
    delete_after = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "external_fingerprint"],
                name="unique_webuntis_homework_fingerprint",
            )
        ]


class SyncSchedule(models.Model):
    class Mode(models.TextChoices):
        INTERVAL = "interval", "Festes Intervall"
        FIXED_TIMES = "fixed_times", "Feste Uhrzeiten"

    source = models.CharField(max_length=40, default="webuntis", unique=True)
    enabled = models.BooleanField(default=False)
    mode = models.CharField(max_length=16, choices=Mode, default=Mode.FIXED_TIMES)
    interval_minutes = models.PositiveIntegerField(null=True, blank=True)
    timezone_name = models.CharField(max_length=64, default="Europe/Berlin")
    times = models.JSONField(default=list)
    weekdays_only = models.BooleanField(default=True)
    weekends = models.BooleanField(default=False)
    holidays = models.BooleanField(default=False)
    max_runs_per_day = models.PositiveSmallIntegerField(default=3)
    min_interval_minutes = models.PositiveSmallIntegerField(default=15)
    updated_at = models.DateTimeField(auto_now=True)
    next_run_at = models.DateTimeField(null=True, blank=True, db_index=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_started_at = models.DateTimeField(null=True, blank=True)
    last_finished_at = models.DateTimeField(null=True, blank=True)
    last_duration_ms = models.PositiveIntegerField(null=True, blank=True)
    last_status = models.CharField(max_length=24, blank=True)
    last_error_class = models.CharField(max_length=40, blank=True)

    def clean(self):
        from .scheduling import validate_schedule

        validate_schedule(self)

    @classmethod
    def current(cls):
        return cls.objects.order_by("pk").first() or cls.objects.create(
            enabled=True,
            times=["06:00", "12:00", "18:00"],
            max_runs_per_day=3,
        )


class SyncRun(models.Model):
    class Trigger(models.TextChoices):
        MANUAL = "manual", "Manuell"
        AUTOMATIC = "automatic", "Automatisch"

    class Status(models.TextChoices):
        RUNNING = "running", "L�uft"
        SUCCESS = "success", "Erfolgreich"
        NO_CHANGE = "no_change", "Keine �nderungen"
        FAILED = "failed", "Fehlgeschlagen"
        THROTTLED = "throttled", "Zu h�ufig"

    connection = models.ForeignKey(
        WebUntisConnection, on_delete=models.CASCADE, related_name="sync_runs"
    )
    trigger = models.CharField(max_length=16, choices=Trigger)
    status = models.CharField(max_length=16, choices=Status, default=Status.RUNNING)
    idempotency_key = models.CharField(max_length=80, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    change_count = models.PositiveIntegerField(default=0)
    categories = models.JSONField(default=list)
    error_code = models.CharField(max_length=40, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    terminal_notification_sent_at = models.DateTimeField(null=True, blank=True)

# Imported here so Django registers the models under the webuntis app.
from .extra_models import (  # noqa: E402,F401
    WebUntisCalendarSubscription,
    WebUntisSubjectMapping,
    WebUntisTeacherMapping,
)
