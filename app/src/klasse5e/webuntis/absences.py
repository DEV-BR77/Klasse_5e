"""Private absence reads, drafts, and explicitly requested browser submissions."""

import hashlib
import json
import uuid
from datetime import datetime, time, timedelta

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
from klasse5e.portal_adapters.models import PortalAdapter
from klasse5e.portal_adapters.policies import provider_available_for_student

from .absence_submission import SubmissionOutcome, submit_once
from .absence_verification import AbsenceRecord
from .browser_absences import PlaywrightAbsenceClient
from .crypto import decrypt
from .forms import AbsenceSubmissionForm
from .importer import MissingStudentId, _date_value
from .models import AbsenceDraft, AbsenceSubmission, WebUntisAbsence, WebUntisConnection


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


def submission_connections(user):
    """Only current guardian-owned, school-approved personal browser logins."""
    contexts = child_contexts(user)
    allowed_ids = [
        context.student.pk
        for context in contexts
        if provider_available_for_student(context.student, PortalAdapter.Provider.WEBUNTIS)
    ]
    connections = (
        WebUntisConnection.objects.filter(
            user=user,
            student_id__in=allowed_ids,
            features__key="absences",
            features__enabled=True,
        )
        .select_related("student")
        .distinct()
    )
    return {connection.student_id: connection for connection in connections}


def submission_children(user):
    connections = submission_connections(user)
    return [context for context in child_contexts(user) if context.student.pk in connections], connections


def _submission_fingerprint(student_id, starts_at, ends_at, note):
    payload = json.dumps(
        {"student": student_id, "starts": starts_at.isoformat(), "ends": ends_at.isoformat(), "note": note},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _submit_browser(connection, expected, user):
    def authorize():
        fresh = submission_connections(user).get(connection.student_id)
        if fresh is None or fresh.pk != connection.pk:
            raise PermissionDenied

    with PlaywrightAbsenceClient(
        decrypt(connection.username_encrypted),
        decrypt(connection.password_encrypted),
        server=connection.server,
        school=connection.school,
        student_key=str(connection.student_id),
    ) as browser:
        return submit_once(browser, expected, authorize=authorize)


def create_submission(user, form, connections):
    """Claim a token once, then issue exactly one browser write for its owner."""
    if not form.is_valid():
        return form, None
    student_id = form.cleaned_data["student"]
    starts_at = datetime.combine(form.cleaned_data["starts_on"], form.cleaned_data["starts_time"])
    ends_at = datetime.combine(form.cleaned_data["ends_on"], form.cleaned_data["ends_time"])
    note = form.cleaned_data["note"].strip()
    fingerprint = _submission_fingerprint(student_id, starts_at, ends_at, note)
    with transaction.atomic():
        submission, created = AbsenceSubmission.objects.get_or_create(
            token=form.cleaned_data["token"],
            defaults={"user": user, "student_id": student_id, "fingerprint": fingerprint},
        )
    if submission.user_id != user.id or submission.fingerprint != fingerprint:
        raise Http404
    if not created:
        return form, submission
    connection = connections.get(student_id)
    if connection is None:
        outcome = SubmissionOutcome.NOT_SENT
    else:
        expected = AbsenceRecord(str(student_id), starts_at, ends_at, note)
        try:
            outcome = _submit_browser(connection, expected, user)
        except Exception:
            # Login and browser start happen before any form action.  Keep the
            # technical detail out of the response and audit trail.
            outcome = SubmissionOutcome.NOT_SENT
    submission.status = outcome
    submission.completed_at = timezone.now()
    submission.save(update_fields=["status", "completed_at"])
    AuditEvent.objects.create(
        actor=user,
        action="absence.browser_submission",
        target_type="absence_submission",
        target_id=str(submission.token),
        metadata={"student_id": str(student_id), "outcome": outcome},
    )
    return form, submission


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
    submission_children_list, _connections = submission_children(request.user)
    from klasse5e.core.family_context import active_child_context

    _all_children, active_child = active_child_context(request)
    selected_id = (
        active_child.student.pk
        if active_child and any(item.student.pk == active_child.student.pk for item in submission_children_list)
        else None
    )
    submission_token = request.POST.get("submission-token") or request.GET.get("submission") or uuid.uuid4()
    try:
        submission_token = uuid.UUID(str(submission_token))
    except (TypeError, ValueError):
        raise Http404 from None
    submission_form = AbsenceSubmissionForm(
        request.POST if request.method == "POST" and request.POST.get("action") == "submit" else None,
        prefix="submission",
        children=submission_children_list,
        selected_id=selected_id,
        initial={"token": submission_token},
    )
    if request.method == "POST" and request.POST.get("action") == "submit":
        # The token is part of the submitted form; no query-string trust is used.
        submission_form, submission = create_submission(request.user, submission_form, _connections)
        if submission:
            return redirect(f"{redirect('absence-portal').url}?submission={submission.token}")
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
            "submission_form": submission_form if submission_children_list else None,
            "submission_children": submission_children_list,
            "submission_result": AbsenceSubmission.objects.filter(
                token=submission_token, user=request.user
            ).select_related("student").first(),
            "webuntis_url": "https://thgwob.webuntis.com/student-absences",
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
