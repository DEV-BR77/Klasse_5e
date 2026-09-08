"""Person-scoped forms for the family centre; never infer rights from a household."""
import secrets

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from .avatar_designer import validate_avatar_seed
from .models import (
    AuditEvent,
    ChildJoinRequest,
    ConsentDecision,
    ConsentType,
    FamilyAccessCode,
    Person,
    SchoolClass,
)
from .onboarding import active_decision, latest_text, may_decide, record_decision, withdraw_decision
from .registration import sanitized_profile_photo


class FamilyPersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "birth_date", "street", "postal_code", "city",
                  "contact_email", "phone", "chat_display_name"]
        labels = {"first_name": "Vorname", "last_name": "Nachname", "birth_date": "Geburtsdatum", "street": "Straße und Hausnummer",
                  "postal_code": "Postleitzahl", "city": "Ort", "contact_email": "Kontakt-E-Mail",
                  "phone": "Telefonnummer", "chat_display_name": "Anzeigename im Chat"}


def person_card(person, user, editable):
    form = FamilyPersonForm(instance=person, prefix=f"person-{person.pk}")
    if not person.contact_email and person.user_id:
        form.fields["contact_email"].initial = person.user.email
    fields = []
    for field in form:
        key = field.name
        shared = (person.email_visibility == "members" if key == "contact_email" else
                  person.phone_visibility == "members" if key == "phone" else
                  person.field_visibility.get(key, key in {"first_name", "last_name"}))
        fields.append({"field": field, "shared": shared})
    from .policies import consent_state

    consents = []
    for consent in ConsentType.objects.order_by("category", "label"):
        text = latest_text(consent)
        if not text or not may_decide(user, person, consent):
            continue
        decision = active_decision(consent, person, user.person)
        consents.append({"type": consent, "text": text, "decision": decision,
            "effective": consent_state(consent, person) == "allowed",
            "enabled": bool(decision and decision.decision == ConsentDecision.Decision.GRANTED),
            "disabled": consent.key == "biometric_face_search" and not settings.BIOMETRIC_SEARCH_ENABLED})
    return {"person": person, "fields": fields, "editable": editable, "consents": consents}


def save_person(request, person):
    form = FamilyPersonForm(request.POST, instance=person, prefix=f"person-{person.pk}")
    if not form.is_valid():
        raise ValidationError([f"{form.fields[key].label}: {error}" for key, errors in form.errors.items() for error in errors])
    photo = request.FILES.get("profile_photo")
    encoded = sanitized_profile_photo(photo) if photo else None
    seed = request.POST.get("avatar_seed", "")
    validate_avatar_seed(seed)
    with transaction.atomic():
        person = form.save(commit=False)
        person.field_visibility = {key: request.POST.get(f"share_{key}") == "on" for key in form.fields}
        person.email_visibility = "members" if person.field_visibility["contact_email"] else "hidden"
        person.phone_visibility = "members" if person.field_visibility["phone"] else "hidden"
        person.avatar_seed = seed
        if encoded:
            person.profile_photo.save(f"{secrets.token_urlsafe(18)}.webp", ContentFile(encoded), save=False)
            person.profile_image_mode = "photo"
        elif request.POST.get("profile_image_mode") == "avatar":
            person.profile_image_mode = "avatar"
        elif person.profile_photo and request.POST.get("profile_image_mode") == "photo":
            person.profile_image_mode = "photo"
        person.save()
        AuditEvent.objects.create(actor=request.user, action="family.profile.updated",
                                  target_type="person", target_id=str(person.pk))


def save_consent(request, person):
    consent = ConsentType.objects.filter(key=request.POST.get("consent_key")).first()
    if not consent or not latest_text(consent):
        raise ValidationError("Diese Einwilligung ist nicht verfügbar.")
    decision = request.POST.get("decision")
    if decision is None:
        decision = "granted" if request.POST.get("enabled") == "on" else "denied"
    if decision == "revoked":
        withdraw_decision(user=request.user, subject=person, key=consent.key)
    elif decision in {"granted", "denied"}:
        record_decision(user=request.user, subject=person, key=consent.key,
                        decision=decision, source="settings")
    else:
        raise ValidationError("Bitte eine gültige Entscheidung auswählen.")


@transaction.atomic
def request_child(request):
    first = request.POST.get("first_name", "").strip()
    last = request.POST.get("last_name", "").strip()
    if not first or not last or max(len(first), len(last)) > 100:
        raise ValidationError("Bitte Vor- und Nachnamen des Kindes angeben (höchstens 100 Zeichen).")
    token = request.POST.get("invitation_code", "").strip()
    code = FamilyAccessCode.resolve(token, for_update=True) if token else None
    if token and (not code or code.existing_guardian_id not in {None, request.user.pk}):
        raise ValidationError("Der Einladungscode ist ungültig oder nicht für dein Konto vorgesehen.")
    class_id = request.POST.get("school_class", "")
    school_class = code.school_class if code else available_classes().filter(
        pk=int(class_id) if class_id.isascii() and class_id.isdecimal() and len(class_id) < 19 else None
    ).first()
    if not school_class:
        raise ValidationError("Bitte eine Schule und Klasse auswählen oder einen gültigen Einladungscode eingeben.")
    item, created = ChildJoinRequest.objects.get_or_create(
        guardian=request.user.person, first_name=first, last_name=last,
        school_class=school_class, status="pending")
    if created and code:
        code.use_count += 1
        code.submitted_at = timezone.now()
        code.save(update_fields=["use_count", "submitted_at"])
    return item


def available_classes():
    today = timezone.localdate()
    return SchoolClass.objects.filter(school__is_active=True,
        school_year__starts_on__lte=today, school_year__ends_on__gte=today).select_related("school").order_by("school__name", "name")
