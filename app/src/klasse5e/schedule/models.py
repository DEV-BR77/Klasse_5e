import hashlib
import secrets

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from klasse5e.core.models import SchoolClass, SchoolYear


class TimeGrid(models.Model):
    school = models.ForeignKey("core.School", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    def clean(self):
        if self.valid_until and self.valid_until < self.valid_from:
            raise ValidationError("Das Ende des Stundenrasters liegt vor seinem Beginn.")


class LessonPeriod(models.Model):
    time_grid = models.ForeignKey(TimeGrid, on_delete=models.CASCADE, related_name="periods")
    number = models.PositiveSmallIntegerField()
    starts_at = models.TimeField()
    ends_at = models.TimeField()

    class Meta:
        ordering = ["number"]
        constraints = [models.UniqueConstraint(fields=["time_grid", "number"], name="unique_grid_period")]

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError("Eine Unterrichtsstunde muss nach ihrem Beginn enden.")
        overlap = LessonPeriod.objects.filter(time_grid=self.time_grid, starts_at__lt=self.ends_at, ends_at__gt=self.starts_at)
        if self.pk:
            overlap = overlap.exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError("Unterrichtsstunden dürfen sich nicht überschneiden.")


class SchoolBreak(models.Model):
    time_grid = models.ForeignKey(TimeGrid, on_delete=models.CASCADE, related_name="breaks")
    label = models.CharField(max_length=80)
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    after_period = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["starts_at"]

    def clean(self):
        if self.ends_at <= self.starts_at:
            raise ValidationError("Eine Pause muss nach ihrem Beginn enden.")
        overlap = SchoolBreak.objects.filter(time_grid=self.time_grid, starts_at__lt=self.ends_at, ends_at__gt=self.starts_at)
        if self.pk:
            overlap = overlap.exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError("Pausen dürfen sich nicht überschneiden.")


class TimetableEntry(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    weekday = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    subject = models.CharField(max_length=100)
    room = models.CharField(max_length=60, blank=True)
    teacher_label = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["weekday", "starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "weekday", "starts_at"], name="unique_class_lesson_start"
            )
        ]


class CalendarEntry(models.Model):
    class Kind(models.TextChoices):
        EXAM = "exam", "Klassenarbeit"
        TRIP = "trip", "Ausflug"
        EVENT = "event", "Veranstaltung"
        CANCELLATION = "cancellation", "Ausfall"
        SUBSTITUTION = "substitution", "Vertretung"
        ROOM_CHANGE = "room_change", "Raumänderung"

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    kind = models.CharField(max_length=20, choices=Kind)
    title = models.CharField(max_length=160)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    room = models.CharField(max_length=60, blank=True)
    details = models.CharField(max_length=500, blank=True)
    revision = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)


class CalendarChange(models.Model):
    entry = models.ForeignKey(CalendarEntry, on_delete=models.CASCADE, related_name="changes")
    revision = models.PositiveIntegerField()
    changed_fields = models.JSONField(default=list)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["entry", "revision"], name="unique_calendar_revision")
        ]


class CalendarDelivery(models.Model):
    entry = models.ForeignKey(CalendarEntry, on_delete=models.CASCADE)
    revision = models.PositiveIntegerField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entry", "revision", "user"], name="unique_calendar_delivery"
            )
        ]


class ICalSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=64, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, user, school_class):
        token = secrets.token_urlsafe(32)
        item = cls.objects.create(
            user=user,
            school_class=school_class,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
        )
        return item, token

    @classmethod
    def resolve(cls, token):
        return cls.objects.filter(
            token_hash=hashlib.sha256(token.encode()).hexdigest(), active=True
        ).first()
