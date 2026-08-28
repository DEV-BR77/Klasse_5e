from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    ConsentType,
    OnboardingState,
    Person,
    TutorialState,
)
from .onboarding import (
    STEP_CONTENT,
    TOTAL_ONBOARDING_STEPS,
    active_decision,
    current_policy_version,
    current_relationships,
    may_decide,
    record_decision,
    subjects_for_user,
    withdraw_decision,
)

TUTORIAL_STEPS = (
    ("Dashboard", "Hier findest du Neues, Termine und wichtige Hinweise."),
    ("Kalender", "Wechsle zwischen Tagen und öffne nur Termine deiner Klasse."),
    ("Beiträge und Chat", "Schreibe respektvoll und teile keine fremden Daten weiter."),
    ("Familie", "Nur bestätigte Beziehungen geben Verwaltungsrechte."),
    (
        "Einwilligungen",
        "Jeder freiwillige Zweck hat eine eigene Entscheidung. Ein Nein ist in Ordnung.",
    ),
    ("Benachrichtigungen", "Du entscheidest je Kategorie; sensible Details bleiben im Portal."),
    (
        "Widerruf und Hilfe",
        "Unter Mehr kannst du Entscheidungen ändern und diese Tour neu starten.",
    ),
)


def _person_or_404(user, value):
    if not hasattr(user, "person"):
        raise Http404
    if not value:
        return user.person
    subject = get_object_or_404(Person, id=value)
    if not subjects_for_user(user).filter(id=subject.id).exists():
        raise PermissionDenied
    return subject


@login_required
def onboarding_step(request, step=1):
    if not hasattr(request.user, "person"):
        return render(
            request,
            "onboarding/missing_profile.html",
            {"page_title": "Profil fehlt", "active_section": "more"},
            status=409,
        )
    if step < 1 or step > TOTAL_ONBOARDING_STEPS:
        raise Http404
    state, _ = OnboardingState.objects.get_or_create(user=request.user)
    if step > state.current_step:
        return redirect("onboarding-step", step=state.current_step)
    if request.method == "POST":
        action = request.POST.get("action", "continue")
        if action == "pause":
            state.current_step = step
            state.save(update_fields=["current_step", "updated_at"])
            return redirect("ui-more")
        subject = _person_or_404(request.user, request.POST.get("subject"))
        if step == 2:
            if request.POST.get("identity_confirmed") != "yes":
                return _render_step(
                    request, state, step, subject, "Bitte bestätige zuerst dein Konto."
                )
            state.identity_confirmed_at = timezone.now()
        keys = STEP_CONTENT[step][2]
        for key in keys:
            value = request.POST.get(key)
            if value not in {"granted", "denied"}:
                return _render_step(
                    request, state, step, subject, "Bitte wähle für jeden Zweck Ja oder Nein."
                )
            record_decision(user=request.user, subject=subject, key=key, decision=value)
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
    if state.completed_at and state.completed_policy_version == current_policy_version():
        return redirect("ui-consents")
    if step > state.current_step:
        return redirect("onboarding-step", step=state.current_step)
    return _render_step(
        request, state, step, _person_or_404(request.user, request.GET.get("subject"))
    )


def _render_step(request, state, step, subject, error=""):
    title, explanation, keys = STEP_CONTENT[step]
    choices = []
    for consent_type in ConsentType.objects.filter(key__in=keys).order_by("key"):
        allowed = may_decide(request.user, subject, consent_type)
        if consent_type.key == "biometric_face_search" and not settings.BIOMETRIC_SEARCH_ENABLED:
            allowed = False
        decision = active_decision(consent_type, subject, request.user.person)
        choices.append(
            {
                "type": consent_type,
                "allowed": allowed,
                "decision": decision.decision if decision else "",
            }
        )
    return render(
        request,
        "onboarding/step.html",
        {
            "page_title": title,
            "active_section": "more",
            "step": step,
            "total_steps": TOTAL_ONBOARDING_STEPS,
            "title": title,
            "explanation": explanation,
            "choices": choices,
            "subjects": subjects_for_user(request.user),
            "subject": subject,
            "relationships": current_relationships(request.user.person).select_related(
                "student_person"
            ),
            "state": state,
            "error": error,
            "biometric_enabled": settings.BIOMETRIC_SEARCH_ENABLED,
        },
    )


@login_required
@require_POST
def consent_withdraw(request, key, subject_id):
    subject = _person_or_404(request.user, subject_id)
    withdraw_decision(user=request.user, subject=subject, key=key)
    return redirect("ui-consents")


@login_required
def tutorial_step(request, step=1):
    if step < 1 or step > len(TUTORIAL_STEPS):
        raise Http404
    state, _ = TutorialState.objects.get_or_create(user=request.user)
    if request.method == "POST":
        action = request.POST.get("action", "next")
        if action == "dismiss":
            state.dismissed_at = timezone.now()
            state.save(update_fields=["dismissed_at", "updated_at"])
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
            return redirect("dashboard")
        state.current_step = step + 1
        state.save(update_fields=["current_step", "updated_at"])
        return redirect("tutorial-step", step=step + 1)
    state.current_step = step
    state.save(update_fields=["current_step", "updated_at"])
    title, body = TUTORIAL_STEPS[step - 1]
    return render(
        request,
        "onboarding/tutorial.html",
        {
            "page_title": f"Tutorial: {title}",
            "active_section": "more",
            "step": step,
            "total_steps": len(TUTORIAL_STEPS),
            "title": title,
            "body": body,
        },
    )
