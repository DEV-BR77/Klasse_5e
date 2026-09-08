"""Private absence reads and local drafts; no browser or write transport."""

from datetime import time, timedelta

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from klasse5e.core.family_context import available_child_contexts
from klasse5e.core.models import (
    AuditEvent,
    ClassMembership,
    ConsentType,
    Person,
    PushPreference,
    UserNotification,
)
from klasse5e.core.module_flags import module_enabled
from klasse5e.core.policies import consent_state, has_active_membership, visible_student_people

from .importer import MissingStudentId, _date_value
from .models import AbsenceDraft, WebUntisAbsence, WebUntisConnection


def child_contexts(user):
    consent = ConsentType.objects.filter(key="webuntis_absences").first()
    return [
        child
        for child in available_child_contexts(user)
        if child.school_class
        and child.relationship.is_legal_guardian
        and has_active_membership(user, child.school_class)
        and module_enabled("webuntis_timetable", child.school_class)
        and consent
        and consent_state(consent, child.student) == "allowed"
    ]


def absence_data_allowed(student):
    consent = ConsentType.objects.filter(key="webuntis_absences").first()
    if consent is None:
        return False
    today = timezone.localdate()
    membership = (
        ClassMembership.objects.filter(
            person=student,
            status="active",
            valid_from__lte=today,
            school_class__school_year__starts_on__lte=today,
            school_class__school_year__ends_on__gte=today,
        )
        .filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
        .select_related("school_class")
        .first()
    )
    return bool(
        membership
        and module_enabled("webuntis_timetable", membership.school_class)
        and consent_state(consent, student) == "allowed"
    )


def visible_absence_students(user):
    """Return consented absence subjects visible to the child or a guardian."""

    allowed_ids = [
        student.pk for student in visible_student_people(user) if absence_data_allowed(student)
    ]
    return Person.objects.filter(pk__in=allowed_ids)


def _clock(value):
    if value is None or value == "":
        return None
    text = str(value)
    if ":" in text:
        return time.fromisoformat(text)
    text = text.zfill(4)
    return time(int(text[:-2]), int(text[-2:]))


@transaction.atomic
def sync_absences(connection, adapter, *, today=None):
    connection = WebUntisConnection.objects.select_for_update().get(pk=connection.pk)
    child = next(
        (c for c in child_contexts(connection.user) if c.student.pk == connection.student_id), None
    )
    if child is None or not connection.features.filter(key="absences", enabled=True).exists():
        raise PermissionDenied
    if not connection.external_student_id:
        raise MissingStudentId()
    today = today or timezone.localdate()
    payload = adapter.call_readonly(
        "absences",
        studentId=connection.external_student_id,
        startDate=(today - timedelta(days=90)).isoformat(),
        endDate=today.isoformat(),
    )
    if isinstance(payload, dict):
        payload = payload.get("data", payload)
    if isinstance(payload, dict):
        payload = payload.get("absences")
    if not isinstance(payload, list):
        raise ValueError("Invalid absence response")
    changes = 0
    for item in payload:
        # An explicit student binding prevents sibling records leaking from broad responses.
        if not isinstance(item, dict) or str(item.get("studentId")) != str(
            connection.external_student_id
        ):
            raise ValueError("Invalid absence student binding")
        source_id = item.get("id")
        if isinstance(source_id, bool) or not isinstance(source_id, int | str):
            raise ValueError("Invalid absence identifier")
        external_id = str(source_id).strip()
        start, end = _date_value(item.get("startDate")), _date_value(item.get("endDate"))
        if not external_id or len(external_id) > 128 or not start or not end or end < start:
            raise ValueError("Invalid absence interval")
        if end < today - timedelta(days=90) or start > today:
            continue
        start_time, end_time = _clock(item.get("startTime")), _clock(item.get("endTime"))
        if (
            start == end
            and start_time is not None
            and end_time is not None
            and end_time <= start_time
        ):
            raise ValueError("Invalid absence time")
        defaults = dict(
            starts_on=start,
            ends_on=end,
            starts_time=start_time,
            ends_time=end_time,
            source_status=str(item.get("status") or "")[:80],
        )
        existing = connection.absences.filter(external_id=external_id).first()
        changed = existing is None or any(
            getattr(existing, key) != value for key, value in defaults.items()
        )
        absence, created = WebUntisAbsence.objects.update_or_create(
            connection=connection, external_id=external_id, defaults=defaults
        )
        changes += int(changed)
        if (
            created
            and PushPreference.objects.filter(
                user=connection.user, key="inapp_absences", enabled=True
            ).exists()
        ):
            UserNotification.objects.get_or_create(
                user=connection.user,
                school_class=child.school_class,
                object_type="webuntis_absence",
                object_id=str(absence.pk),
                revision="new",
                defaults=dict(
                    category="absences",
                    title="Neue Abwesenheit in WebUntis",
                    summary="Eine neue persönliche Information ist verfügbar.",
                    target_url="/abwesenheiten/",
                ),
            )
    return changes


class AbsenceDraftForm(forms.ModelForm):
    class Meta:
        model = AbsenceDraft
        fields = ["student", "starts_on", "ends_on", "starts_time", "ends_time", "reason", "note"]
        labels = dict(
            student="Kind",
            starts_on="Von",
            ends_on="Bis",
            starts_time="Uhrzeit von (optional)",
            ends_time="Uhrzeit bis (optional)",
            reason="Grund",
            note="Freitext (optional)",
        )
        widgets = {
            **{
                key: forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
                for key in ("starts_on", "ends_on")
            },
            **{
                key: forms.TimeInput(attrs={"type": "time"}) for key in ("starts_time", "ends_time")
            },
        }

    def __init__(self, *args, children, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student"].queryset = Person.objects.filter(
            pk__in=[c.student.pk for c in children]
        )

    def clean(self):
        data = super().clean()
        start, end = data.get("starts_on"), data.get("ends_on")
        st, et = data.get("starts_time"), data.get("ends_time")
        if (
            start
            and end
            and (end < start or (end == start and st is not None and et is not None and et <= st))
        ):
            raise forms.ValidationError("Das Ende muss nach dem Beginn liegen.")
        return data


@login_required
@require_http_methods(["GET", "POST"])
def absence_portal(request):
    children = child_contexts(request.user)
    visible_ids = list(visible_absence_students(request.user).values_list("pk", flat=True))
    if not visible_ids:
        raise Http404
    draft_ids = [child.student.pk for child in children]
    form = (
        AbsenceDraftForm(request.POST if request.method == "POST" else None, children=children)
        if children
        else None
    )
    if request.method == "POST" and request.POST.get("action") == "delete":
        try:
            draft_id = int(request.POST.get("draft_id", ""))
        except (TypeError, ValueError):
            raise Http404 from None
        draft = AbsenceDraft.objects.filter(
            pk=draft_id, user=request.user, student_id__in=draft_ids
        ).first()
        if draft is None:
            raise Http404
        draft.delete()
        return redirect("absence-portal")
    if request.method == "POST" and form is not None and form.is_valid():
        draft = form.save(commit=False)
        draft.user = request.user
        draft.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="absence.draft.created",
            target_type="absence_draft",
            target_id=str(draft.pk),
        )
        return redirect("absence-portal")
    response = render(
        request,
        "webuntis/absences.html",
        {
            "page_title": "Abwesenheiten",
            "form": form,
            "absences": WebUntisAbsence.objects.filter(
                connection__student_id__in=visible_ids,
                ends_on__gte=timezone.localdate() - timedelta(days=90),
            ).select_related("connection__student"),
            "drafts": AbsenceDraft.objects.filter(
                user=request.user,
                student_id__in=draft_ids,
                created_at__gte=timezone.now() - timedelta(days=30),
            ).select_related("student"),
        },
    )
    response["Cache-Control"] = "private, no-store"
    return response
