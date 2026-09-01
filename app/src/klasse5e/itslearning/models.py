import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models

from klasse5e.core.models import StudentProfile, UserAccount

from .crypto import decrypt, encrypt


class ItslearningConnection(models.Model):
    owner = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    username_ciphertext = models.BinaryField()
    password_ciphertext = models.BinaryField()
    calendar_url_ciphertext = models.BinaryField(blank=True, default=b"")
    active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=32, default="never")
    last_sync_message = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_secrets(self, username, password, calendar_url=""):
        self.username_ciphertext = encrypt(username)
        self.password_ciphertext = encrypt(password)
        self.calendar_url_ciphertext = encrypt(calendar_url)

    @property
    def calendar_url(self):
        return decrypt(self.calendar_url_ciphertext)


class ItslearningCourse(models.Model):
    connection = models.ForeignKey(ItslearningConnection, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=32)
    title = models.CharField(max_length=180)
    course_url = models.URLField(max_length=500)
    rss_url_ciphertext = models.BinaryField(blank=True, default=b"")
    report_360_url = models.URLField(max_length=500, blank=True)
    learning_objectives_url = models.URLField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "external_id"], name="unique_itslearning_course"
            )
        ]

    @property
    def rss_url(self):
        return decrypt(self.rss_url_ciphertext)

    def set_rss_url(self, value):
        self.rss_url_ciphertext = encrypt(value)


class ItslearningUpdate(models.Model):
    course = models.ForeignKey(ItslearningCourse, on_delete=models.CASCADE, related_name="updates")
    fingerprint = models.CharField(max_length=64)
    title = models.CharField(max_length=300)
    summary = models.TextField(blank=True)
    url = models.URLField(max_length=800, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "fingerprint"], name="unique_itslearning_update"
            )
        ]
        ordering = ["-published_at", "-first_seen_at"]


class ItslearningCalendarItem(models.Model):
    connection = models.ForeignKey(
        ItslearningConnection, on_delete=models.CASCADE, related_name="calendar_items"
    )
    uid = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=800, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["connection", "uid"], name="unique_itslearning_calendar_item"
            )
        ]
        ordering = ["starts_at"]


class WebDavSpace(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    username = models.CharField(max_length=160, unique=True)
    password_hash = models.CharField(max_length=256)
    quota_bytes = models.PositiveBigIntegerField(default=100 * 1024 * 1024)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
