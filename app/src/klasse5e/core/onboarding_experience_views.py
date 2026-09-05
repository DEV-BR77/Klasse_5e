from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from klasse5e.webuntis.models import WebUntisConnection
from klasse5e.webuntis.services import eligible_students

from .models import ConsentDecision, ConsentType, OnboardingState, Person, TutorialState
from .onboarding import (
    STEP_CONTENT,
    TOTAL_ONBOARDING_STEPS,
    active_decision,
    current_policy_version,
    current_relationships,
    may_decide,
    record_decision,
    subjects_for_user,
)
from .onboarding_content import CONSENT_GUIDANCE, STEP_GUIDANCE, TUTORIAL_STEPS


def _subjects_for_step(user, step):
    if step == 8:
        return eligible_students(user).order_by("first_name", "last_name")
    return subjects_for_user(user).order_by("first_name", "last_name")


def _subject_or_404(user, step, value=None):
    subjects = _subjects_for_step(user, step)
    if value:
        subject = get_object_or_404(Person, id=value)
        if not subjects.filter(id=subject.id).exists():
            raise PermissionDenied
        return subject
    if step == 8:
        connection = (
            WebUntisConnection.objects.filter(user=user, student__in=subjects)
            .select_related("student")
            .first()
        )
        if connection:
            return connection.student
    if hasattr(user, "person"):
        own = subjects.filter(id=user.person.id).first()
        if own:
            return own
    return subjects.first()


def _is_editing(request, state):
    return bool(
        state.completed_at
        and state.completed_policy_version == current_policy_version()
        and (request.GET.get("mode") == "settings" or request.POST.get("mode") == "settings")
    )


@login_required
def onboarding_step(request, step=None):
    if not hasattr(request.user, "person"):
        return render(
            request,
            "onboarding/missing_profile.html",
            {"page_title": "Profil fehlt", "active_section": "more"},
            status=409,
        )
    state, _ = OnboardingState.objects.get_or_create(user=request.user)
    if step is None:
        if state.completed_at and state.completed_policy_version == current_policy_version():
            return redirect("ui-consents")
        step = state.current_step
    if step < 1 or step > TOTAL_ONBOARDING_STEPS:
        raise Http404
    editing = _is_editing(request, state)
    if not editing and step > state.current_step:
        return redirect("onboarding-step", step=state.current_step)

    subjects = _subjects_for_step(request.user, step)
    subject = _subject_or_404(
        request.user, step, request.POST.get("subject") or request.GET.get("subject")
    )
    if request.method == "POST":
        action = request.POST.get("action", "continue")
        if action == "pause" and not editing:
            state.current_step = step
            state.save(update_fields=["current_step", "updated_at"])
            return redirect("onboarding-paused")
        if step == 2 and request.POST.get("identity_confirmed") != "yes":
            return _render_step(
                request, state, step, subject, subjects, editing, "Bitte bestätige dein Konto."
            )
        if step == 2:
            state.identity_confirmed_at = timezone.now()
        keys = STEP_CONTENT[step][2]
        if keys and subject is None and step != 8:
            return _render_step(
                request,
                state,
                step,
                subject,
                subjects,
                editing,
                "Für diese Einstellung ist noch kein bestätigtes Kind verfügbar.",
            )
        for key in keys if subject is not None else ():
            value = request.POST.get(key)
            if key == "biometric_face_search" and not settings.BIOMETRIC_SEARCH_ENABLED:
                value = ConsentDecision.Decision.DENIED
            if value not in {ConsentDecision.Decision.GRANTED, ConsentDecision.Decision.DENIED}:
                return _render_step(
                    request,
                    state,
                    step,
                    subject,
                    subjects,
                    editing,
                    "Bitte wähle für jeden Zweck Aktivieren oder Aus lassen.",
                )
            record_decision(
                user=request.user,
                subject=subject,
                key=key,
                decision=value,
                source="settings" if editing else "onboarding",
            )
        if editing:
            state.completed_policy_version = current_policy_version()
            state.save(update_fields=["completed_policy_version", "updated_at"])
            return redirect("ui-consents")
        if step == TOTAL_ONBOARDING_STEPS:
            state.current_step = TOTAL_ONBOARDING_STEPS
            state.completed_at = timezone.now()
            state.completed_policy_version = current_policy_version()
            state.save()
            TutorialState.objects.get_or_create(user=request.user)
            return redirect("tutorial-step", step=1)
        state.current_step = min(TOTAL_ONBOARDING_STEPS, step + 1)
        state.completed_at = None
        state.save()
        return redirect("onboarding-step", step=state.current_step)
    if state.completed_at and state.completed_policy_version == current_policy_version() and not editing:
        return redirect("ui-consents")
    return _render_step(request, state, step, subject, subjects, editing)


def _render_step(request, state, step, subject, subjects, editing=False, error=""):
    title, explanation, keys = STEP_CONTENT[step]
    choices = []
    for consent_type in ConsentType.objects.filter(key__in=keys).order_by("key"):
        allowed = bool(subject and may_decide(request.user, subject, consent_type))
        if consent_type.key == "biometric_face_search" and not settings.BIOMETRIC_SEARCH_ENABLED:
            allowed = False
        decision = active_decision(consent_type, subject, request.user.person) if subject else None
        choices.append(
            {
                "type": consent_type,
                "allowed": allowed,
                "decision": decision.decision if decision else "",
                "guidance": CONSENT_GUIDANCE.get(consent_type.key, {}),
            }
        )
    relationships = current_relationships(request.user.person).select_related("student_person")
    connection = None
    if step == 8 and subject:
        connection = WebUntisConnection.objects.filter(user=request.user, student=subject).first()
    return render(
        request,
        "onboarding/experience_step.html",
        {
            "page_title": title,
            "active_section": "more",
            "step": step,
            "total_steps": TOTAL_ONBOARDING_STEPS,
            "title": title,
            "explanation": explanation,
            "guidance": STEP_GUIDANCE[step],
            "choices": choices,
            "subjects": subjects,
            "subject": subject,
            "relationships": relationships,
            "state": state,
            "error": error,
            "editing": editing,
            "connection": connection,
            "biometric_enabled": settings.BIOMETRIC_SEARCH_ENABLED,
        },
    )


@login_required
def onboarding_paused(request):
    state, _ = OnboardingState.objects.get_or_create(user=request.user)
    return render(
        request,
        "onboarding/paused.html",
        {"page_title": "Einführung pausiert", "active_section": "more", "state": state},
    )


@login_required
def tutorial_step(request, step=None):
    state, _ = TutorialState.objects.get_or_create(user=request.user)
    step = step or state.current_step
    if step < 1 or step > len(TUTORIAL_STEPS):
        raise Http404
    if request.method == "POST":
        action = request.POST.get("action", "next")
        if action == "dismiss":
            state.dismissed_at = timezone.now()
            state.save(update_fields=["dismissed_at", "updated_at"])
            messages.info(request, "Die Tour wurde beendet. Du bist wieder auf der Startseite.")
            return redirect("dashboard")
        if action == "restart":
            state.current_step = 1
            state.completed_at = None
            state.dismissed_at = None
            state.save()
            return redirect("tutorial-step", step=1)
        if step == len(TUTORIAL_STEPS):
            state.completed_at = timezone.now()
            state.current_step = step
            state.save()
            messages.info(request, "Die Tour ist abgeschlossen. Du bist wieder auf der Startseite.")
            return redirect("dashboard")
        state.current_step = step + 1
        state.save(update_fields=["current_step", "updated_at"])
        return redirect("tutorial-step", step=step + 1)
    state.current_step = step
    state.save(update_fields=["current_step", "updated_at"])
    item = TUTORIAL_STEPS[step - 1]
    return render(
        request,
        "onboarding/tutorial_v2.html",
        {
            "page_title": f"Tour: {item['title']}",
            "active_section": "more",
            "step": step,
            "total_steps": len(TUTORIAL_STEPS),
            "item": item,
        },
    )
