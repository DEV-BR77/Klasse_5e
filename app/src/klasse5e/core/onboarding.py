import hashlib

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import (
    AuditEvent,
    ConsentDecision,
    ConsentTextVersion,
    ConsentType,
    GuardianChildRelationship,
    OnboardingState,
    Person,
    PushPreference,
    PushSubscription,
    RelationshipStatus,
)

TOTAL_ONBOARDING_STEPS = 10
PUSH_KEYS = {"push_general", "push_chat", "push_events"}
WEBUNTIS_KEYS = {
    "webuntis_timetable": "timetable",
    "webuntis_timetable_extended": "timetable_extended",
    "webuntis_substitutions": "substitutions",
    "webuntis_homework": "homework",
    "webuntis_exams": "exams",
    "webuntis_holidays": "holidays",
    "webuntis_timegrid": "timegrid",
    "webuntis_subjects": "subjects",
    "webuntis_rooms": "rooms",
    "webuntis_teachers": "teachers",
    "webuntis_schoolyears": "schoolyears",
    "webuntis_statusdata": "statusdata",
    "webuntis_absences": None,
}

STEP_CONTENT = {
    1: (
        "Willkommen",
        "Du kannst jederzeit pausieren. Freiwillige Funktionen bleiben bis zu deiner Entscheidung aus.",
        (),
    ),
    2: (
        "Identität bestätigen",
        "Prüfe, ob du mit dem richtigen persönlichen Konto angemeldet bist.",
        (),
    ),
    3: (
        "Familie und Zuordnungen",
        "Nur bestätigte Beziehungen erlauben Entscheidungen für ein Kind.",
        (),
    ),
    4: (
        "Datenschutz",
        "Lies die Kurzfassung. Die ausführlichen Informationen bleiben jederzeit erreichbar.",
        (),
    ),
    5: (
        "Kontaktdaten",
        "Entscheide getrennt, ob Kontaktdaten im geschützten Klassenprofil sichtbar sein dürfen.",
        ("profile_contact_visibility",),
    ),
    6: (
        "Fotos und Galerie",
        "Diese Entscheidung umfasst keine biometrische Gesichtssuche.",
        ("photo_gallery",),
    ),
    7: (
        "Benachrichtigungen",
        "Wähle jede Push-Kategorie einzeln. Auf dem Sperrbildschirm stehen keine sensiblen Details.",
        ("push_general", "push_chat", "push_events"),
    ),
    8: (
        "WebUntis",
        "Jede Kategorie ist einzeln und nur für einen manuellen Abruf aktivierbar.",
        (
            "webuntis_timetable",
            "webuntis_timetable_extended",
            "webuntis_substitutions",
            "webuntis_homework",
            "webuntis_exams",
            "webuntis_holidays",
            "webuntis_timegrid",
            "webuntis_subjects",
            "webuntis_rooms",
            "webuntis_teachers",
            "webuntis_schoolyears",
            "webuntis_statusdata",
            "webuntis_absences",
        ),
    ),
    9: (
        "Biometrische Gesichtssuche",
        "Diese besonders sensible Komfortfunktion bleibt ohne vollständige Freigabe aus.",
        ("biometric_face_search",),
    ),
    10: (
        "Zusammenfassung",
        "Prüfe deine Auswahl. Ablehnungen haben keinen Einfluss auf die Kernfunktionen.",
        (),
    ),
}


def current_policy_version():
    rows = ConsentTextVersion.objects.filter(effective_from__lte=timezone.now()).order_by(
        "consent_type__key", "-effective_from", "-id"
    )
    latest = {}
    for row in rows:
        latest.setdefault(row.consent_type_id, f"{row.consent_type.key}:{row.version}")
    material = "|".join(sorted(latest.values())) or "empty"
    return hashlib.sha256(material.encode()).hexdigest()[:32]


def current_relationships(guardian):
    today = timezone.localdate()
    return GuardianChildRelationship.objects.filter(
        guardian_person=guardian,
        status=RelationshipStatus.VERIFIED,
        verified_at__isnull=False,
        valid_from__lte=today,
    ).filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))


def subjects_for_user(user):
    if not hasattr(user, "person"):
        return Person.objects.none()
    child_ids = current_relationships(user.person).values_list("student_person_id", flat=True)
    return Person.objects.filter(Q(id=user.person.id) | Q(id__in=child_ids)).distinct()


def _relationship_may_manage(guardian, subject, category):
    relation = current_relationships(guardian).filter(student_person=subject).first()
    if relation is None:
        return False
    field = {
        "photo": "may_manage_photo_consents",
        "biometric": "may_manage_biometric_consents",
    }.get(category, "may_manage_general_consents")
    return relation.is_legal_guardian and getattr(relation, field)


def may_decide(user, subject, consent_type):
    if not hasattr(user, "person"):
        return False
    if subject.id == user.person.id:
        return True
    return _relationship_may_manage(user.person, subject, consent_type.category)


def latest_text(consent_type):
    return (
        consent_type.consenttextversion_set.filter(effective_from__lte=timezone.now())
        .order_by("-effective_from", "-id")
        .first()
    )


def active_decision(consent_type, subject, decider):
    text = latest_text(consent_type)
    if text is None:
        return None
    return (
        ConsentDecision.objects.filter(
            consent_type=consent_type,
            text_version=text,
            subject_person=subject,
            deciding_person=decider,
            valid_from__lte=timezone.now(),
        )
        .order_by("-decided_at", "-id")
        .first()
    )


@transaction.atomic
def record_decision(*, user, subject, key, decision, source="onboarding"):
    consent_type = ConsentType.objects.get(key=key)
    if decision not in {ConsentDecision.Decision.GRANTED, ConsentDecision.Decision.DENIED}:
        raise ValueError("invalid_decision")
    if not may_decide(user, subject, consent_type):
        raise PermissionDenied
    if key == "biometric_face_search" and (
        decision == ConsentDecision.Decision.GRANTED and not settings.BIOMETRIC_SEARCH_ENABLED
    ):
        raise PermissionDenied
    text = latest_text(consent_type)
    if text is None:
        raise ValueError("missing_consent_text")
    item = ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=subject,
        deciding_person=user.person,
        decision=decision,
        source=source,
    )
    from .policies import consent_state

    enabled = (
        decision == ConsentDecision.Decision.GRANTED
        and consent_state(consent_type, subject) == "allowed"
    )
    _apply_feature_state(user, subject, key, enabled)
    AuditEvent.objects.create(
        actor=user,
        action="consent.decided",
        target_type="person",
        target_id=str(subject.id),
        metadata={"consent_key": key, "decision": decision, "version": text.version},
    )
    return item


@transaction.atomic
def withdraw_decision(*, user, subject, key):
    consent_type = ConsentType.objects.get(key=key)
    if not may_decide(user, subject, consent_type):
        raise PermissionDenied
    text = latest_text(consent_type)
    if text is None:
        raise ValueError("missing_consent_text")
    item = ConsentDecision.objects.create(
        consent_type=consent_type,
        text_version=text,
        subject_person=subject,
        deciding_person=user.person,
        decision=ConsentDecision.Decision.REVOKED,
        revoked_at=timezone.now(),
        source="withdrawal",
    )
    _apply_feature_state(user, subject, key, False)
    AuditEvent.objects.create(
        actor=user,
        action="consent.withdrawn",
        target_type="person",
        target_id=str(subject.id),
        metadata={"consent_key": key, "version": text.version},
    )
    return item


def _apply_feature_state(user, subject, key, enabled):
    if key == "profile_contact_visibility" and not enabled:
        subject.email_visibility = "hidden"
        subject.phone_visibility = "hidden"
        subject.save(update_fields=["email_visibility", "phone_visibility"])
    if key in PUSH_KEYS:
        PushPreference.objects.update_or_create(user=user, key=key, defaults={"enabled": enabled})
        if not enabled and not PushPreference.objects.filter(user=user, enabled=True).exists():
            PushSubscription.objects.filter(user=user).update(enabled=False)
    if key in WEBUNTIS_KEYS:
        from klasse5e.webuntis.models import WebUntisFeaturePreference

        feature_key = WEBUNTIS_KEYS[key]
        if feature_key:
            WebUntisFeaturePreference.objects.filter(
                connection__user=user,
                connection__student=subject,
                key=feature_key,
            ).update(enabled=enabled)
    if key == "biometric_face_search" and not enabled:
        from klasse5e.biometrics.models import BiometricProfile

        BiometricProfile.objects.filter(student__person=subject).exclude(status="deleted").update(
            status="deletion_pending", deletion_requested_at=timezone.now()
        )


def onboarding_complete(user):
    state = OnboardingState.objects.filter(user=user).first()
    return bool(
        state and state.completed_at and state.completed_policy_version == current_policy_version()
    )
