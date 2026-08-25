import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from klasse5e.core.models import Person, SchoolClass, SchoolYear, UserAccount, Visibility


def protected_path(instance, filename):
    suffix = ".pdf" if filename.lower().endswith(".pdf") else ".bin"
    return f"protected/{instance.school_class_id}/{uuid.uuid4().hex}{suffix}"


def validate_pdf(upload):
    if upload.size > 15 * 1024 * 1024:
        raise ValidationError("pdf_too_large")
    pos = upload.tell()
    head = upload.read(5)
    upload.seek(pos)
    if head != b"%PDF-":
        raise ValidationError("invalid_pdf_content")


class ProtectedDocument(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        PUBLISHED = "published", "Veröffentlicht"

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80)
    document_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    version = models.CharField(max_length=32)
    original = models.FileField(upload_to=protected_path, validators=[validate_pdf])
    fillable = models.FileField(upload_to=protected_path, validators=[validate_pdf], blank=True)
    is_updated = models.BooleanField(default=False)
    acknowledgement_required = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    created_by = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


class TeacherProfile(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    subjects = models.CharField(max_length=300)
    class_function = models.CharField(max_length=120)
    school_email = models.EmailField(blank=True)
    office_hours = models.CharField(max_length=160, blank=True)
    introduction = models.TextField(blank=True)
    email_visibility = models.CharField(
        max_length=16, choices=Visibility, default=Visibility.HIDDEN
    )
    office_hours_visibility = models.CharField(
        max_length=16, choices=Visibility, default=Visibility.HIDDEN
    )


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Entwurf"
        PUBLISHED = "published", "Veröffentlicht"

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    body = models.TextField()
    category = models.CharField(max_length=80)
    author = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=Status, default=Status.DRAFT)
    pinned = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    comments_closed = models.BooleanField(default=False)
    attachments = models.ManyToManyField(ProtectedDocument, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_visible(self):
        now = timezone.now()
        return self.status == self.Status.PUBLISHED and (
            not self.expires_at or self.expires_at > now
        )


class Comment(models.Model):
    class Status(models.TextChoices):
        VISIBLE = "visible", "Sichtbar"
        WITHDRAWN = "withdrawn", "Zurückgezogen"
        HIDDEN = "hidden", "Moderiert"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    body = models.TextField(max_length=4000)
    status = models.CharField(max_length=16, choices=Status, default=Status.VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)


class CommentReport(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reporter = models.ForeignKey(UserAccount, on_delete=models.PROTECT)
    reason = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["comment", "reporter"], name="unique_comment_report")
        ]
