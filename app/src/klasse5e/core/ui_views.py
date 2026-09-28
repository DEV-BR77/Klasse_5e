import base64
import csv
import io
import json
import secrets
import tempfile
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import content_disposition_header
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from klasse5e.chat.forms import ChatAssetForm
from klasse5e.chat.models import ChatAsset, ChatReadState, ChatRetentionCategory, ChatRoom
from klasse5e.chat.services import may_create_room, may_manage_room, may_publish_message
from klasse5e.core.module_permissions import may_access_module
from klasse5e.content.models import Post, ProtectedDocument, TeacherProfile
from klasse5e.events.models import (
    ContributionCategory,
    ContributionItem,
    Event,
    EventParticipation,
    EventPoll,
    EventPollOption,
    EventPollVote,
    Reservation,
)
from klasse5e.events.services import (
    cancel_reservation_for_user,
    create_reservation,
    set_event_participation,
)
from klasse5e.events.spoonacular import SpoonacularUnavailable, search_food_items
from klasse5e.events.policies import may_create_event, may_manage_event
from klasse5e.itslearning.models import (
    ItslearningCalendarItem,
    ItslearningConnection,
    ItslearningUpdate,
    WebDavSpace,
)
from klasse5e.itslearning.webdav import used_bytes
from klasse5e.meals.models import MealDay, MealPlan
from klasse5e.media.models import Gallery
from klasse5e.media.policies import may_access_gallery, may_manage_gallery, may_create_gallery
from klasse5e.portal_adapters.catalog import (
    ADAPTER_CATALOG,
    provider_definition,
    seed_default_modules,
)
from klasse5e.portal_adapters.models import (
    ChildModuleConnection,
    PortalAdapter,
    PortalAdapterDefinition,
    PortalAdapterDefinitionModule,
    PortalAdapterModule,
    SchoolmanagerConnection,
)
from klasse5e.schedule.models import CalendarEntry, TimetableEntry
from klasse5e.schoolmanager.crypto import encrypt as encrypt_schoolmanager
from klasse5e.webuntis.extra_models import WebUntisSubjectMapping, WebUntisTeacherMapping
from klasse5e.webuntis.models import (
    HomeworkProgress,
    WebUntisAbsence,
    WebUntisConnection,
    WebUntisHomework,
    WebUntisLesson,
)

from .calendar_presenter import build_calendar_context
from .contact_data import format_phone_number, normalize_email_address
from .family_context import active_child_context
from .family_handouts import create_family_handout
from .models import (
    AuditEvent,
    ClassMembership,
    ConsentDecision,
    ConsentType,
    FamilyPhoto,
    GuardianChildRelationship,
    Household,
    Invitation,
    Person,
    PilotReport,
    PortalConfigurationKey,
    PortalConfigurationValue,
    PortalModule,
    PortalTheme,
    PushPreference,
    PushSubscription,
    RegistrationApplication,
    Role,
    RoleAssignment,
    School,
    SchoolClass,
    SchoolYear,
    StudentProfile,
    UserAccount,
    UserNotification,
)
from .policies import active_roles, consent_state, family_label, visible_student_people, has_active_membership
from .registration import sanitized_profile_photo
from .school_import import EXPECTED_FIELDS, detect_encoding, import_schools
from .school_setup_transfer import apply_rows as apply_school_setup_rows
from .school_setup_transfer import export_csv as export_school_setup_csv
from .school_setup_transfer import parse_csv as parse_school_setup_csv
from .session_security import (
    DEFAULT_IDLE_TIMEOUT_MINUTES,
    MAX_IDLE_TIMEOUT_MINUTES,
    MIN_IDLE_TIMEOUT_MINUTES,
    SESSION_IDLE_TIMEOUT_KEY,
    idle_timeout_minutes,
)

TEMPLATE_PREVIEW_CATALOG = (
    {
        "key": "velora-ui",
        "name": "Velora UI",
        "stack": "Next.js · Tailwind · Motion",
        "license": "MIT",
        "repo": "https://github.com/ColorlibHQ/velora-ui",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Weiche Farbflächen, große Rundungen und ruhige Verläufe",
    },
    {
        "key": "hyperui",
        "name": "HyperUI",
        "stack": "HTML · Tailwind",
        "license": "MIT",
        "repo": "https://github.com/markmead/hyperui",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Klar, kompakt und kontrastreich mit grünen Akzenten",
    },
    {
        "key": "flowbite",
        "name": "Flowbite",
        "stack": "HTML/JS · Tailwind",
        "license": "MIT",
        "repo": "https://github.com/themesberg/flowbite",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Vertraute App-Optik mit Blau, Karten und deutlichen Zuständen",
    },
    {
        "key": "preline-ui",
        "name": "Preline UI",
        "stack": "HTML · Tailwind plugin",
        "license": "MIT",
        "repo": "https://github.com/htmlstreamofficial/preline",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Warme Flächen, feine Linien und ein freundlicher Editorial-Stil",
    },
    {
        "key": "astrowind",
        "name": "AstroWind",
        "stack": "Astro · Tailwind",
        "license": "MIT",
        "repo": "https://github.com/arthelokyo/astrowind",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Luftige Typografie mit leuchtendem Verlauf und viel Weißraum",
    },
    {
        "key": "cruip-open-react",
        "name": "Cruip Open React",
        "stack": "Next.js · React · Tailwind",
        "license": "MIT",
        "repo": "https://github.com/cruip/open-react-template",
        "source": "Colorlib 33 Tailwind templates",
        "style_note": "Dunkle Oberfläche mit leuchtenden Violett- und Cyan-Akzenten",
    },
)


# These are the color and layout tokens derived from the six local design studies
# above.  They deliberately stay inactive until an administrator releases them.
TEMPLATE_THEME_DEFAULTS = {
    "velora-ui": {
        "name": "Velora UI",
        "description": "Weiche Farbflächen, große Rundungen und ruhige Verläufe",
        "audience": PortalTheme.Audience.ADULTS,
        "primary": "#6D4AFF",
        "primary_dark": "#4F2EE8",
        "primary_light": "#EEEAFF",
        "accent": "#EC6FB3",
        "background": "#F3F1FF",
        "surface": "#FFFFFF",
        "text": "#251F46",
        "text_muted": "#736D91",
        "radius": "1.35rem",
        "shadow_strength": 18,
    },
    "hyperui": {
        "name": "HyperUI",
        "description": "Klar, kompakt und kontrastreich mit grünen Akzenten",
        "audience": PortalTheme.Audience.ADULTS,
        "primary": "#087F5B",
        "primary_dark": "#065F46",
        "primary_light": "#EEF7F2",
        "accent": "#12A779",
        "background": "#F8FAF9",
        "surface": "#FFFFFF",
        "text": "#101814",
        "text_muted": "#58655F",
        "radius": ".7rem",
        "shadow_strength": 5,
    },
    "flowbite": {
        "name": "Flowbite",
        "description": "Vertraute App-Optik mit Blau, Karten und deutlichen Zuständen",
        "audience": PortalTheme.Audience.ADULTS,
        "primary": "#2563EB",
        "primary_dark": "#1D4ED8",
        "primary_light": "#EFF6FF",
        "accent": "#06B6D4",
        "background": "#F9FAFB",
        "surface": "#FFFFFF",
        "text": "#111827",
        "text_muted": "#6B7280",
        "radius": "1rem",
        "shadow_strength": 3,
    },
    "preline-ui": {
        "name": "Preline UI",
        "description": "Warme Flächen, feine Linien und ein freundlicher Editorial-Stil",
        "audience": PortalTheme.Audience.ADULTS,
        "primary": "#7C3AED",
        "primary_dark": "#6D28D9",
        "primary_light": "#FFF1E7",
        "accent": "#F97316",
        "background": "#FFFAF5",
        "surface": "#FFFFFF",
        "text": "#30231E",
        "text_muted": "#816F65",
        "radius": "1rem",
        "shadow_strength": 12,
    },
    "astrowind": {
        "name": "AstroWind",
        "description": "Luftige Typografie mit leuchtendem Verlauf und viel Weißraum",
        "audience": PortalTheme.Audience.ADULTS,
        "primary": "#0284C7",
        "primary_dark": "#0369A1",
        "primary_light": "#E9F7FF",
        "accent": "#7C3AED",
        "background": "#F5F9FF",
        "surface": "#FFFFFF",
        "text": "#0F172A",
        "text_muted": "#64748B",
        "radius": "1.35rem",
        "shadow_strength": 18,
    },
    "cruip-open-react": {
        "name": "Cruip Open React",
        "description": "Dunkle Oberfläche mit leuchtenden Violett- und Cyan-Akzenten",
        "audience": PortalTheme.Audience.ADULTS,
        "is_dark": True,
        "primary": "#6D28D9",
        "primary_dark": "#4F46E5",
        "primary_light": "#22263A",
        "accent": "#22D3EE",
        "background": "#0B0D17",
        "surface": "#151824",
        "text": "#F5F7FF",
        "text_muted": "#A3ACC2",
        "radius": "1rem",
        "shadow_strength": 20,
    },
}


def _template_theme_key(template_key):
    return f"template-{template_key}"


def _template_catalog_with_release_state():
    themes = PortalTheme.objects.filter(
        key__in=[_template_theme_key(item["key"]) for item in TEMPLATE_PREVIEW_CATALOG]
    )
    themes_by_key = {theme.key: theme for theme in themes}
    return tuple(
        {
            **item,
            "released_theme": themes_by_key.get(_template_theme_key(item["key"])),
        }
        for item in TEMPLATE_PREVIEW_CATALOG
    )


def _merge_adjacent_lessons(lessons):
    merged = []
    for lesson in lessons:
        if merged:
            previous = merged[-1]
            if (
                previous.subject == lesson.subject
                and previous.room == lesson.room
                and previous.teacher_label == lesson.teacher_label
                and previous.ends_at == lesson.starts_at
            ):
                previous.ends_at = lesson.ends_at
                continue
        merged.append(lesson)
    return merged


def _require_portal_admin(user):
    if not _can_manage_portal(user):
        raise Http404


def _can_manage_portal(user):
    return (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True,
            role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.SCHOOL_ADMIN, Role.CLASS_ADMIN],
        ).exists()
    )


def _manageable_classes(user):
    query = SchoolClass.objects.filter(status="active").select_related("school", "school_year")
    if (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    ):
        return query.order_by("school__name", "display_name", "name")
    school_ids = user.roleassignment_set.filter(
        active=True, role=Role.SCHOOL_ADMIN, school__isnull=False
    ).values("school_id")
    class_ids = user.roleassignment_set.filter(
        active=True, role=Role.CLASS_ADMIN, school_class__isnull=False
    ).values("school_class_id")
    return query.filter(Q(school_id__in=school_ids) | Q(id__in=class_ids)).order_by(
        "school__name", "display_name", "name"
    )


def _manageable_schools(user):
    if (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    ):
        return School.objects.filter(is_active=True).order_by("name")
    return School.objects.filter(pk__in=_manageable_classes(user).values("school_id")).order_by(
        "name"
    )


def _manageable_portal_adapters(user):
    """Return only adapters inside the administrator's assigned school scope."""
    adapters = PortalAdapter.objects.all()
    if (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    ):
        return adapters
    schools = _manageable_schools(user)
    return adapters.filter(school__in=schools)


def _may_manage_school_catalog(user):
    return (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    )


def _may_manage_roles(user):
    return (
        user.is_superuser
        or user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    )


def _membership(user, request=None):
    if request is not None:
        _children, selected_child = active_child_context(request)
        if selected_child and selected_child.membership:
            return selected_child.membership
    today = timezone.localdate()
    return (
        ClassMembership.objects.filter(
            person__user=user,
            status="active",
            valid_from__lte=today,
            school_class__school_year__starts_on__lte=today,
            school_class__school_year__ends_on__gte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .select_related("school_class", "school_class__school_year")
        .first()
    )


def _class_or_404(user, request=None):
    membership = _membership(user, request)
    if membership:
        return membership.school_class
    if user.is_superuser or active_roles(user) & {
        Role.PRIMARY_ADMIN,
        Role.DEPUTY_ADMIN,
        Role.SCHOOL_ADMIN,
        Role.CLASS_ADMIN,
    }:
        school_class = _manageable_classes(user).first()
        if school_class:
            return school_class
    raise Http404


def _day_from_request(request):
    value = request.GET.get("tag")
    if value:
        try:
            return timezone.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass
    now = timezone.localtime()
    day = now.date()
    if now.hour >= 15:
        day += timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def _dashboard_day_copy(day, *, today=None):
    """Name the day actually shown on the dashboard, not always today."""

    today = today or timezone.localdate()
    if day == today:
        return {
            "dashboard_heading": "Was steht heute an?",
            "dashboard_schedule_label": "Heute",
            "dashboard_empty_schedule_text": "Heute ist kein Unterricht eingetragen.",
        }
    if day == today + timedelta(days=1):
        return {
            "dashboard_heading": "Was steht morgen an?",
            "dashboard_schedule_label": "Morgen",
            "dashboard_empty_schedule_text": "Für morgen ist kein Unterricht eingetragen.",
        }
    return {
        "dashboard_heading": "Was steht am nächsten Schultag an?",
        "dashboard_schedule_label": "Nächster Schultag",
        "dashboard_empty_schedule_text": "Für den nächsten Schultag ist kein Unterricht eingetragen.",
    }


def _shared(request, title, section):
    school_class = _membership(request.user, request)
    return {
        "page_title": title,
        "active_section": section,
        "membership": school_class,
        "roles": active_roles(request.user, school_class.school_class if school_class else None),
        "family_name": family_label(request.user),
    }


def _connections_for_active_child(connections, child, user=None):
    """Keep personal school data in the child area, never mixed by accident."""

    person_id = child.student.id if child else None
    if person_id is None and user and visible_student_people(user).filter(pk=user.person.pk).exists():
        person_id = user.person.pk
    if person_id is None:
        return connections.none()
    if connections.model is ItslearningConnection:
        return connections.filter(student__person_id=person_id)
    return connections.filter(student_id=person_id)


def _family_overview_items(children, *, now):
    """Create a compact family timeline from class information and changes."""

    children_by_class = {
        child.school_class.id: child for child in children if child.school_class is not None
    }
    class_ids = list(children_by_class)
    if not class_ids:
        return []
    rows = []
    for entry in (
        CalendarEntry.objects.filter(school_class_id__in=class_ids, ends_at__gte=now)
        .select_related("school_class")
        .order_by("starts_at")[:18]
    ):
        child = children_by_class.get(entry.school_class_id)
        if child:
            rows.append(
                {
                    "child": child,
                    "tone": child.tone,
                    "kind": entry.get_kind_display(),
                    "title": entry.title,
                    "when": entry.starts_at,
                    "detail": entry.room or entry.details,
                    "url": "/kalender/",
                }
            )
    for event in (
        Event.objects.filter(
            school_class_id__in=class_ids,
            status=Event.Status.PUBLISHED,
            ends_at__gte=now,
        )
        .select_related("school_class")
        .order_by("starts_at")[:12]
    ):
        child = children_by_class.get(event.school_class_id)
        if child:
            rows.append(
                {
                    "child": child,
                    "tone": child.tone,
                    "kind": "Veranstaltung",
                    "title": event.title,
                    "when": event.starts_at,
                    "detail": event.location,
                    "url": f"/mehr/veranstaltungen/{event.pk}/",
                }
            )
    for post in (
        Post.objects.filter(school_class_id__in=class_ids, status=Post.Status.PUBLISHED)
        .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
        .select_related("school_class")
        .order_by("-important", "-pinned", "-published_at", "-updated_at")[:12]
    ):
        child = children_by_class.get(post.school_class_id)
        if child:
            rows.append(
                {
                    "child": child,
                    "tone": child.tone,
                    "kind": "Wichtige Information" if post.important else "Aktuelles",
                    "title": post.title,
                    "when": post.published_at or post.updated_at,
                    "detail": post.category,
                    "url": f"/mehr/aktuelles/{post.pk}/",
                }
            )
    rows.sort(key=lambda item: (item["when"], item["title"]))
    return rows[:8]


@login_required
@require_POST
def select_active_child(request, student_id=None):
    """Persist the selected child in the browser session after access validation."""

    children, _selected = active_child_context(request)
    if student_id is None:
        request.session.pop("active_child_person_id", None)
    elif any(item.student.id == student_id for item in children):
        request.session["active_child_person_id"] = student_id
    else:
        raise Http404
    target = request.POST.get("next", "")
    if not target.startswith("/") or target.startswith("//"):
        target = "/"
    return redirect(target)


def _itslearning_connections(user):
    return ItslearningConnection.objects.filter(
        student__person__in=visible_student_people(user), active=True
    )


def _webuntis_connections(user):
    from klasse5e.webuntis.services import visible_connections

    return visible_connections(user)


@login_required
def dashboard(request):
    family_children, active_child = active_child_context(request)
    # A household with exactly one child has an unambiguous personal portal
    # context even before the family switcher has been used in this browser.
    dashboard_child = active_child or (family_children[0] if len(family_children) == 1 else None)
    school_class = dashboard_child.school_class if dashboard_child else None
    if school_class is None and not family_children:
        school_class = _class_or_404(request.user, request)
    dashboard_class_ids = [
        child.school_class.pk for child in family_children if child.school_class is not None
    ]
    if school_class:
        dashboard_class_ids = [school_class.pk]
    # A dashboard request is read-only. Imports, retention cleanup and meal
    # synchronization run through their scheduled management commands, never
    # through a member opening this page. That keeps a provider outage from
    # changing data, adding latency or masking an operational failure here.
    day = _day_from_request(request)
    hour = timezone.localtime().hour
    greeting = "Guten Morgen" if hour < 12 else "Guten Tag" if hour < 18 else "Guten Abend"
    week_start = day - timedelta(days=day.weekday())
    meal_days = list(
        MealDay.objects.filter(
            plan__status=MealPlan.Status.READY,
            is_published=True,
            date__gte=week_start,
            date__lte=week_start + timedelta(days=4),
        )
        .select_related("plan")
        .prefetch_related("options")
        .order_by("date")
    )
    daily_meal = next((meal for meal in meal_days if meal.date == day), None)
    meal_week = [
        {
            "date": week_start + timedelta(days=offset),
            "meal": next(
                (meal for meal in meal_days if meal.date == week_start + timedelta(days=offset)),
                None,
            ),
        }
        for offset in range(5)
    ]
    context = _shared(request, "Start", "start")
    portal_connections = _connections_for_active_child(
        _itslearning_connections(request.user), dashboard_child, request.user
    )
    webuntis_connections = _connections_for_active_child(
        _webuntis_connections(request.user), dashboard_child, request.user
    )
    webuntis_last_sync = (
        webuntis_connections.order_by("-last_successful_sync_at")
        .values_list("last_successful_sync_at", flat=True)
        .first()
    )
    dashboard_absences = list(
        WebUntisAbsence.objects.filter(
            connection__in=webuntis_connections,
            ends_on__gte=day - timedelta(days=14),
        )
        .select_related("connection__student")
        .order_by("-starts_on", "-pk")[:8]
    )
    personal_lessons = _merge_adjacent_lessons(
        list(
            WebUntisLesson.objects.filter(connection__in=webuntis_connections, starts_at__date=day)
            .exclude(status="cancelled")
            .order_by("starts_at")
        )
    )
    adapter_ids = {connection.adapter_id for connection in webuntis_connections if connection.adapter_id}
    subject_aliases = dict(
        WebUntisSubjectMapping.objects.filter(adapter__isnull=True).values_list("code", "label")
    )
    subject_aliases.update(
        WebUntisSubjectMapping.objects.filter(adapter_id__in=adapter_ids).values_list("code", "label")
    )
    teacher_aliases = dict(
        WebUntisTeacherMapping.objects.filter(adapter__isnull=True).values_list("code", "label")
    )
    teacher_aliases.update(
        WebUntisTeacherMapping.objects.filter(adapter_id__in=adapter_ids).values_list("code", "label")
    )
    for lesson in personal_lessons:
        lesson.display_subject = subject_aliases.get(lesson.subject_code, lesson.subject)
        lesson.display_teacher = teacher_aliases.get(lesson.teacher_code, lesson.teacher_label)
    manual_lessons = (
        TimetableEntry.objects.filter(school_class=school_class, weekday=day.isoweekday())
        if school_class
        else TimetableEntry.objects.none()
    )
    calendar_entries = (
        CalendarEntry.objects.filter(
            school_class_id__in=dashboard_class_ids, starts_at__date=day
        ).order_by("starts_at")
        if dashboard_class_ids
        else CalendarEntry.objects.none()
    )
    upcoming_events = list(
        Event.objects.filter(
            school_class_id__in=dashboard_class_ids,
            status=Event.Status.PUBLISHED,
            ends_at__gte=timezone.now(),
        ).order_by("starts_at")
        if dashboard_class_ids
        else []
    )
    posts = list(
        Post.objects.filter(
            school_class_id__in=dashboard_class_ids, status=Post.Status.PUBLISHED
        ).order_by("-important", "-pinned", "-updated_at")[:3]
        if dashboard_class_ids
        else []
    )
    homework = list(
        WebUntisHomework.objects.filter(
            connection__in=webuntis_connections,
            due_on__gte=day,
        )
        .select_related("connection__student")
        .order_by("due_on", "subject")[:12]
    )
    progress = {
        (item.student_id, item.external_fingerprint): item.completed
        for item in HomeworkProgress.objects.filter(
            student_id__in={item.connection.student_id for item in homework},
            external_fingerprint__in={item.external_fingerprint for item in homework},
        )
    }
    for item in homework:
        item.is_completed = progress.get(
            (item.connection.student_id, item.external_fingerprint), False
        )
        item.display_subject = subject_aliases.get(item.subject, item.subject)
    homework.sort(key=lambda item: (item.is_completed, item.due_on, item.subject.casefold()))
    homework = homework[:5]
    context.update(
        {
            "app_version": settings.APP_VERSION,
            "release_channel": settings.APP_RELEASE_CHANNEL,
            "selected_day": day,
            **_dashboard_day_copy(day),
            **(
                {
                    "dashboard_heading": f"Was steht am {day:%d.%m.%Y} an?",
                    "dashboard_schedule_label": f"{day:%d.%m.%Y}",
                    "dashboard_empty_schedule_text": "Für diesen Tag ist kein Unterricht eingetragen.",
                }
                if request.GET.get("tag")
                and day not in (timezone.localdate(), timezone.localdate() + timedelta(days=1))
                else {}
            ),
            "dashboard_week": [
                {
                    "date": week_start + timedelta(days=offset),
                    "selected": week_start + timedelta(days=offset) == day,
                }
                for offset in range(7)
            ],
            "webuntis_last_sync": webuntis_last_sync,
            "dashboard_absences": dashboard_absences,
            "greeting": greeting,
            "lessons": personal_lessons if personal_lessons else manual_lessons,
            "homework": homework,
            "manageable_homework_student_ids": set(
                visible_student_people(request.user).values_list("pk", flat=True)
            ),
            "family_children": family_children,
            "active_child": active_child,
            "family_overview_items": (
                _family_overview_items(family_children, now=timezone.now())
                if not active_child and len(family_children) > 1
                else []
            ),
            "calendar_entries": calendar_entries,
            "events": upcoming_events[:2],
            "daily_meal": daily_meal,
            "meal_week": meal_week,
            "posts": posts,
            "documents": (
                ProtectedDocument.objects.filter(
                    school_class_id__in=dashboard_class_ids,
                    status=ProtectedDocument.Status.PUBLISHED,
                ).order_by("-is_updated", "-created_at")[:2]
                if dashboard_class_ids
                else ProtectedDocument.objects.none()
            ),
            "chat_unread": _unread_count(request.user, school_class),
            "notification_counts": {
                **{
                    row["category"]: row["total"]
                    for row in UserNotification.objects.filter(
                        user=request.user,
                        school_class=school_class,
                        read_at__isnull=True,
                    )
                    .values("category")
                    .annotate(total=Count("id"))
                },
                # The dashboard badges describe the entries currently shown,
                # not stale unread notifications from an older sync.
                "homework": len(homework),
                "news": len(posts),
            },
            "itslearning_entries": ItslearningCalendarItem.objects.filter(
                connection__in=portal_connections, starts_at__date=day
            ).order_by("starts_at")[:5],
            "itslearning_updates": ItslearningUpdate.objects.filter(
                course__connection__in=portal_connections
            ).select_related("course")[:3],
        }
    )
    from klasse5e.webuntis.absences import submission_connections

    context["absences_available"] = bool(submission_connections(request.user))
    return render(request, "ui/dashboard_v2.html", context)


@login_required
@require_POST
def homework_progress(request, homework_id):
    homework = get_object_or_404(
        WebUntisHomework.objects.select_related("connection__student"),
        id=homework_id,
        connection__in=_webuntis_connections(request.user),
        connection__student__in=visible_student_people(request.user),
    )
    completed = request.POST.get("completed", "").lower() in {"1", "true", "yes", "on"}
    progress, _ = HomeworkProgress.objects.update_or_create(
        student=homework.connection.student,
        external_fingerprint=homework.external_fingerprint,
        defaults={
            "completed": completed,
            "completed_by": request.user if completed else None,
            "completed_at": timezone.now() if completed else None,
        },
    )
    return JsonResponse(
        {
            "homework_id": homework.id,
            "completed": progress.completed,
            "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        }
    )


def _unread_count(user, school_class):
    from klasse5e.chat.services import require_room_access

    total = 0
    for room in ChatRoom.objects.filter(school_class=school_class):
        try:
            require_room_access(user, room)
        except PermissionDenied:
            continue
        state = ChatReadState.objects.filter(room=room, user=user).first()
        query = room.messages.exclude(author=user)
        if state:
            query = query.filter(created_at__gt=state.last_read_at)
        total += query.count()
    return total


@login_required
def calendar(request):
    family_children, active_child = active_child_context(request)
    calendar_child = active_child or (family_children[0] if family_children else None)
    school_class = (
        calendar_child.school_class
        if calendar_child and calendar_child.school_class
        else _class_or_404(request.user, request)
    )
    if not may_access_module(request.user, "calendar", school_class):
        raise Http404
    day = _day_from_request(request)
    # A day is the safe, readable default for every viewport and also works
    # without JavaScript.  The explicit week control keeps the full planning
    # matrix available on larger screens without forcing a 52rem canvas on a
    # phone.
    view = request.GET.get("ansicht", "day")
    categories = request.GET.getlist("kategorie") if "filter" in request.GET else None
    context = _shared(request, "Kalender", "calendar")
    context.update(
        build_calendar_context(
            school_class=school_class,
            selected_day=day,
            webuntis_connections=_connections_for_active_child(
                _webuntis_connections(request.user), calendar_child, request.user
            ),
            itslearning_connections=_connections_for_active_child(
                _itslearning_connections(request.user), calendar_child, request.user
            ),
            view=view,
            active_categories=categories,
        )
    )
    active_keys = [item["key"] for item in context["calendar_categories"] if item["active"]]
    context["category_query"] = urlencode(
        [("filter", "1"), *(("kategorie", key) for key in active_keys)]
    )
    context["calendar_week_number"] = day.isocalendar().week
    context["calendar_child"] = calendar_child
    context["webuntis_last_sync"] = (
        _connections_for_active_child(
            _webuntis_connections(request.user), calendar_child, request.user
        )
        .order_by("-last_successful_sync_at")
        .values_list("last_successful_sync_at", flat=True)
        .first()
    )
    return render(request, "ui/calendar_v2.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def chat_overview(request):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "chat", school_class):
        raise Http404
    if request.method == "POST":
        action = request.POST.get("action")
        if action in {"save", "archive", "delete"}:
            target = get_object_or_404(
                ChatRoom, public_id=request.POST.get("room_id"), school_class=school_class,
            )
            required_action = "edit" if action == "save" else "moderate"
            if not may_manage_room(request.user, target, required_action):
                raise Http404
        elif action not in (None, "", "create") or not may_create_room(request.user, school_class):
            raise Http404
        if action == "delete":
            room = get_object_or_404(
                ChatRoom.objects.filter(direct_conversation__isnull=True).prefetch_related(
                    "messages"
                ),
                public_id=request.POST.get("room_id"),
                school_class=school_class,
            )
            for message in room.messages.all():
                if message.attachment:
                    message.attachment.delete(save=False)
            room_id = str(room.public_id)
            room_title = room.title
            room.delete()
            AuditEvent.objects.create(
                actor=request.user,
                action="chat.room.deleted",
                target_type="chat_room",
                target_id=room_id,
                metadata={"title": room_title},
            )
            messages.success(request, "Der Chatraum wurde gelöscht.")
            return redirect("ui-chat")
        if action == "archive":
            room = get_object_or_404(
                ChatRoom.objects.filter(direct_conversation__isnull=True),
                public_id=request.POST.get("room_id"),
                school_class=school_class,
            )
            room.is_open = False
            room.save(update_fields=["is_open"])
            AuditEvent.objects.create(
                actor=request.user,
                action="chat.room.archived",
                target_type="chat_room",
                target_id=str(room.public_id),
                metadata={"title": room.title},
            )
            messages.success(request, "Der Chatraum wurde archiviert.")
            return redirect("ui-chat")
        if action == "save":
            room = get_object_or_404(
                ChatRoom.objects.filter(direct_conversation__isnull=True),
                public_id=request.POST.get("room_id"),
                school_class=school_class,
            )
            title = request.POST.get("title", "").strip()[:120]
            if not title:
                messages.error(request, "Bitte gib einen Namen für den Chatraum an.")
                return redirect("ui-chat")
            retention_id = request.POST.get("retention_category", "").strip()
            retention = ChatRetentionCategory.objects.filter(
                pk=int(retention_id) if retention_id.isascii() and retention_id.isdecimal() else None,
                is_active=True,
                intended_for_events=False,
            ).first() if retention_id else None
            appearance = request.POST.get("appearance", ChatRoom.Appearance.STANDARD)
            audience = request.POST.get("audience", ChatRoom.Audience.GENERAL)
            is_open = request.POST.get("is_open") == "on"
            if is_open != room.is_open and not may_manage_room(request.user, room, "moderate"):
                raise Http404
            if appearance not in ChatRoom.Appearance.values:
                appearance = ChatRoom.Appearance.STANDARD
            if audience not in ChatRoom.Audience.values:
                audience = ChatRoom.Audience.GENERAL
            room.title = title
            room.retention_category = retention
            room.appearance = appearance
            room.audience = audience
            room.is_open = is_open
            room.save(update_fields=["title", "retention_category", "appearance", "audience", "is_open"])
            AuditEvent.objects.create(
                actor=request.user,
                action="chat.room.updated",
                target_type="chat_room",
                target_id=str(room.public_id),
                metadata={"title": room.title, "appearance": room.appearance, "audience": room.audience, "is_open": room.is_open},
            )
            messages.success(request, "Der Chatraum wurde gespeichert.")
            return redirect("ui-chat-room", room_id=room.public_id)
        title = request.POST.get("title", "").strip()[:120]
        if title:
            retention_id = request.POST.get("retention_category", "").strip()
            if retention_id and (
                not retention_id.isascii() or not retention_id.isdecimal() or len(retention_id) > 18
            ):
                messages.error(request, "Bitte wähle eine gültige Aufbewahrungsregel.")
                return redirect("ui-chat")
            retention = ChatRetentionCategory.objects.filter(
                pk=int(retention_id) if retention_id else None,
                is_active=True,
                intended_for_events=False,
            ).first()
            appearance = request.POST.get("appearance", ChatRoom.Appearance.STANDARD)
            if appearance not in ChatRoom.Appearance.values:
                appearance = ChatRoom.Appearance.STANDARD
            audience = request.POST.get("audience", ChatRoom.Audience.GENERAL)
            if audience not in ChatRoom.Audience.values:
                audience = ChatRoom.Audience.GENERAL
            ChatRoom.objects.create(
                school_class=school_class,
                school_year=school_class.school_year,
                title=title,
                is_open=True,
                retention_category=retention,
                appearance=appearance,
                audience=audience,
            )
            messages.success(request, "Der Chatraum wurde angelegt.")
        return redirect("ui-chat")
    room_rows = _chat_room_rows(request.user, school_class)
    context = _shared(request, "Chat", "chat")
    context["can_create_chat"] = may_create_room(request.user, school_class)
    context["room_rows"] = room_rows
    context["retention_categories"] = ChatRetentionCategory.objects.filter(
        is_active=True, intended_for_events=False
    )
    context["appearance_choices"] = ChatRoom.Appearance.choices
    context["audience_choices"] = ChatRoom.Audience.choices
    return render(request, "ui/chat_overview.html", context)


def _chat_room_rows(user, school_class):
    """Build the same accessible conversation list for overview and detail pages."""
    from klasse5e.chat.services import require_room_access, room_title_for_user

    rooms = (
        ChatRoom.objects.filter(school_class=school_class)
        .select_related(
            "direct_conversation__participant_one__person",
            "direct_conversation__participant_two__person",
        )
        .order_by("event_id", "title")
    )
    rows = []
    for room in rooms:
        try:
            require_room_access(user, room)
        except PermissionDenied:
            continue
        state = ChatReadState.objects.filter(room=room, user=user).first()
        visible_messages = room.messages.filter(hidden_at__isnull=True, withdrawn_at__isnull=True)
        unread = visible_messages.exclude(author=user)
        if state:
            unread = unread.filter(created_at__gt=state.last_read_at)
        rows.append(
            {
                "room": room,
                "display_title": room_title_for_user(room, user),
                "is_direct": bool(getattr(room, "direct_conversation", None)),
                "can_edit": may_manage_room(user, room),
                "can_manage": may_manage_room(user, room, "moderate"),
                "unread": unread.count(),
                "last_message": visible_messages.select_related("author__person")
                .order_by("-created_at")
                .first(),
            }
        )
    return rows


@login_required
@require_http_methods(["GET", "POST"])
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, public_id=room_id)
    composer_error = ""
    from klasse5e.chat.services import require_room_access, room_title_for_user

    try:
        require_room_access(request.user, room)
    except PermissionDenied:
        raise Http404 from None
    if request.method == "POST":
        if request.POST.get("action") in {"member_add", "member_remove", "member_role", "member_reset"}:
            if not may_manage_room(request.user, room, "moderate"):
                raise Http404
            from klasse5e.chat.models import ChatRoomMember

            if getattr(room, "direct_conversation", None):
                raise Http404
            if request.POST.get("action") == "member_reset":
                room.members.filter(active=True).update(active=False, updated_at=timezone.now())
                AuditEvent.objects.create(actor=request.user, action="chat.room.members_reset", target_type="chat_room", target_id=str(room.public_id))
                messages.success(request, "Der Raum verwendet wieder seine Zielgruppe statt einer Mitgliederauswahl.")
                return redirect("ui-chat-room", room_id=room.public_id)
            member_user_id = request.POST.get("user_id", "")
            if not member_user_id.isascii() or not member_user_id.isdecimal() or len(member_user_id) > 18:
                raise Http404
            member = ChatRoomMember.objects.filter(room=room, user_id=member_user_id).first()
            if request.POST.get("action") == "member_remove":
                if member and member.active and room.members.filter(active=True).count() == 1:
                    messages.error(request, "Das letzte Mitglied kann nicht einzeln entfernt werden: Das würde den Raum für die ganze Zielgruppe öffnen. Verwende dafür ausdrücklich ‚Mitgliederauswahl aufheben‘.")
                elif member:
                    member.active = False
                    member.save(update_fields=["active", "updated_at"])
                    AuditEvent.objects.create(actor=request.user, action="chat.room.member_removed", target_type="chat_room", target_id=str(room.public_id), metadata={"user_id": str(member.user_id)})
                    messages.success(request, "Das Mitglied wurde aus dem Chatraum entfernt.")
            else:
                candidate = UserAccount.objects.filter(pk=member_user_id).first()
                from klasse5e.chat.services import is_eligible_for_room_audience
                try:
                    if not candidate:
                        raise PermissionDenied
                    is_eligible_for_room_audience(candidate, room)
                    allowed = True
                except PermissionDenied:
                    allowed = False
                if not allowed:
                    messages.error(request, "Dieses Konto gehört nicht zur Zielgruppe dieses Chatraums.")
                else:
                    role = request.POST.get("role", ChatRoomMember.Role.MEMBER)
                    if role not in ChatRoomMember.Role.values:
                        role = ChatRoomMember.Role.MEMBER
                    if member:
                        member.role = role
                        member.active = True
                        member.added_by = request.user
                        member.save(update_fields=["role", "active", "added_by", "updated_at"])
                    else:
                        ChatRoomMember.objects.create(room=room, user_id=member_user_id, role=role, added_by=request.user)
                    AuditEvent.objects.create(actor=request.user, action="chat.room.member_updated", target_type="chat_room", target_id=str(room.public_id), metadata={"user_id": str(member_user_id), "role": role})
                    messages.success(request, "Die Chatraum-Mitglieder wurden gespeichert.")
            return redirect("ui-chat-room", room_id=room.public_id)
        from klasse5e.chat.services import create_message

        try:
            create_message(
                room, request.user, request.POST.get("body", ""), None, request.FILES.get("attachment"),
                request.POST.get("sticker_id"),
            )
        except ValidationError as exc:
            composer_error = {
                "room_closed": "Dieser Raum ist archiviert. Du kannst hier nicht mehr schreiben.",
                "invalid_body": "Bitte eine Nachricht mit höchstens 2000 Zeichen oder einen Anhang auswählen.",
                "invalid_attachment": "Der Anhang ist ungültig. Erlaubt sind Bilder, PDF und Audio bis 8 MB.",
                "invalid_sticker": "Dieser Sticker ist nicht mehr verfügbar. Bitte wähle einen anderen.",
            }.get(exc.messages[0], "Die Nachricht konnte nicht gespeichert werden. Bitte prüfe deine Eingaben.")
        else:
            return redirect("ui-chat-room", room_id=room.public_id)
    ChatReadState.objects.update_or_create(
        room=room, user=request.user, defaults={"last_read_at": timezone.now()}
    )
    chat_messages = list(
        room.messages.select_related("author__person", "reply_to__author__person", "sticker")
        .order_by("created_at")
    )
    direct = getattr(room, "direct_conversation", None)
    mention_names = []
    if not direct:
        mention_names = [
            display or first
            for display, first in Person.objects.filter(
                classmembership__school_class=room.school_class,
                classmembership__status="active",
                user__isnull=False,
            )
            .exclude(user=request.user)
            .values_list("chat_display_name", "first_name")
            .distinct()
        ]
    context = _shared(request, room_title_for_user(room, request.user), "chat")
    from klasse5e.chat.models import ChatRoomMember
    from klasse5e.chat.services import may_moderate
    for message in chat_messages:
        message.can_moderate = may_moderate(request.user, room, owner_id=message.author_id) and (
            not direct or message.reports.filter(resolved_at__isnull=True).exists()
        )
    explicit_members = list(
        room.members.filter(active=True).select_related("user__person")
    ) if not direct else []
    member_candidates = list(
        Person.objects.filter(
            classmembership__school_class=room.school_class,
            classmembership__status="active",
            user__isnull=False,
        ).exclude(user=request.user).select_related("user").distinct().order_by("first_name", "last_name")
    ) if not direct else []
    context.update(
        {
            "room_rows": _chat_room_rows(request.user, room.school_class),
            "retention_categories": ChatRetentionCategory.objects.filter(
                is_active=True, intended_for_events=False
            ),
            "appearance_choices": ChatRoom.Appearance.choices,
            "audience_choices": ChatRoom.Audience.choices,
            "room": room,
            "composer_error": composer_error,
            "composer_body": request.POST.get("body", "") if composer_error else "",
            "room_title": room_title_for_user(room, request.user),
            "is_direct": bool(direct),
            "chat_messages": chat_messages,
            "chat_poll_url": reverse("chat-messages", kwargs={"room_id": room.public_id}),
            "chat_latest_at": chat_messages[-1].created_at if chat_messages else None,
            "chat_assets": ChatAsset.objects.filter(is_active=True),
            "emojis": list(
                ChatAsset.objects.filter(kind=ChatAsset.Kind.EMOJI, is_active=True)
                .order_by("sort_order", "label")
                .values_list("value", flat=True)
            ) or "😀 😄 😂 😊 😍 🥳 😎 🤔 👍 👏 🙌 💪 ❤️ 🎉 🚲 ⚽ 📚 ✏️".split(),
            "mention_names": mention_names,
            "chat_members": explicit_members,
            "chat_member_candidates": member_candidates,
            "chat_member_roles": ChatRoomMember.Role.choices,
            "can_create_chat": may_create_room(request.user, room.school_class),
            "can_manage_chat_members": may_manage_room(request.user, room, "moderate"),
            "can_publish_chat": may_publish_message(request.user, room),
        }
    )
    return render(request, "ui/chat_room.html", context, status=400 if composer_error else 200)


@login_required
@require_POST
def start_direct_conversation(request, person_id):
    school_class = _class_or_404(request.user, request)
    target = get_object_or_404(Person.objects.select_related("user"), pk=person_id)
    from klasse5e.chat.services import get_or_create_direct_conversation

    try:
        conversation = get_or_create_direct_conversation(request.user, target, school_class)
    except PermissionDenied:
        raise Http404 from None
    return redirect("ui-chat-room", room_id=conversation.room.public_id)


@login_required
def chat_attachment(request, message_id):
    from klasse5e.chat.models import ChatMessage

    message = get_object_or_404(ChatMessage.objects.select_related("room"), public_id=message_id)
    from klasse5e.chat.services import require_room_access

    try:
        require_room_access(request.user, message.room)
    except PermissionDenied:
        raise Http404 from None
    if not message.attachment or message.withdrawn_at or message.hidden_at:
        raise Http404
    content_type = message.attachment_content_type or "application/octet-stream"
    response_file = message.attachment.open("rb")
    if content_type.startswith("image/") and message.attachment_safety_status != "approved":
        from io import BytesIO

        from klasse5e.chat.safety import ImagePixelationError, pixelate_image

        try:
            response_file = BytesIO(pixelate_image(response_file.read()))
        except ImagePixelationError:
            raise Http404 from None
        content_type = "image/jpeg"
    response = FileResponse(
        response_file,
        content_type=content_type,
    )
    disposition = (
        "inline"
        if content_type.startswith(("image/", "audio/"))
        else "attachment"
    )
    response["Content-Disposition"] = content_disposition_header(
        disposition == "attachment", message.attachment_name
    )
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def portal_management(request):
    _require_portal_admin(request.user)
    from .role_management import require_role_manager

    context = _shared(request, "Verwaltung", "management")
    try:
        require_role_manager(request.user)
        context["can_manage_roles"] = True
    except PermissionDenied:
        context["can_manage_roles"] = False
    context.update(
        {
            "review_pending": RegistrationApplication.objects.filter(
                status="review_pending"
            ).count(),
            "schools": School.objects.filter(is_active=True).count(),
            "classes": SchoolClass.objects.filter(status="active").count(),
            "pilot_reports": PilotReport.objects.filter(resolved_at__isnull=True).count(),
        }
    )
    return render(request, "ui/portal_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def pilot_reports_management(request):
    """Review pilot feedback within the administrator's school scope."""

    _require_portal_admin(request.user)
    manageable_classes = _manageable_classes(request.user)
    reports = PilotReport.objects.filter(school_class__in=manageable_classes).select_related(
        "reporter", "school_class", "school_class__school"
    )
    if request.method == "POST":
        report = get_object_or_404(reports, pk=request.POST.get("report_id"))
        action = request.POST.get("action")
        if action == "resolve":
            report.resolved_at = timezone.now()
            report.save(update_fields=["resolved_at"])
            messages.success(request, "Meldung als erledigt markiert.")
        elif action == "reopen":
            report.resolved_at = None
            report.save(update_fields=["resolved_at"])
            messages.success(request, "Meldung wieder geöffnet.")
        return redirect("pilot-reports-management")
    status = request.GET.get("status", "open")
    if status == "resolved":
        reports = reports.filter(resolved_at__isnull=False)
    elif status != "all":
        reports = reports.filter(resolved_at__isnull=True)
    context = _shared(request, "Pilotmeldungen", "management")
    context.update(
        {
            "pilot_reports": reports,
            "pilot_report_status": status,
        }
    )
    return render(request, "ui/pilot_reports_management.html", context)


@login_required
def pilot_report_screenshot(request, report_id):
    """Serve a pilot screenshot only to administrators of its school scope."""

    _require_portal_admin(request.user)
    report = get_object_or_404(
        PilotReport.objects.filter(school_class__in=_manageable_classes(request.user)),
        pk=report_id,
    )
    if not report.screenshot:
        raise Http404("Für diese Meldung ist kein Screenshot gespeichert.")
    response = FileResponse(report.screenshot.open("rb"), content_type="image/*")
    response["Content-Disposition"] = content_disposition_header(
        False, Path(report.screenshot.name).name
    )
    return response


@login_required
@require_http_methods(["GET", "POST"])
def chat_assets_settings(request):
    _require_portal_admin(request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            from django.db.models.deletion import ProtectedError

            asset = get_object_or_404(ChatAsset, pk=request.POST.get("asset_id"))
            image_name = asset.image.name
            try:
                asset.delete()
            except ProtectedError:
                messages.error(request, "Dieser Sticker wird bereits in Nachrichten verwendet. Deaktiviere ihn stattdessen.")
            else:
                if image_name:
                    asset.image.storage.delete(image_name)
                messages.success(request, "Das Chat-Element wurde entfernt.")
        elif action == "save":
            asset = get_object_or_404(ChatAsset, pk=request.POST.get("asset_id")) if request.POST.get("asset_id") else ChatAsset()
            previous_image = asset.image.name
            form = ChatAssetForm(request.POST, request.FILES, instance=asset)
            if asset.pk and asset.messages.exists() and request.FILES.get("image"):
                form.add_error("image", "Ein bereits versendeter Grafik-Sticker bleibt unverändert. Lege für ein neues Bild einen neuen Sticker an.")
            if not form.is_valid():
                context = _shared(request, "Chat-Element bearbeiten", "management")
                context.update(asset_form=form, editing_asset=asset)
                return render(request, "ui/chat_asset_form.html", context, status=400)
            saved = form.save()
            if previous_image and previous_image != saved.image.name:
                saved.image.storage.delete(previous_image)
            messages.success(request, "Das Chat-Element wurde gespeichert.")
        else:
            raise Http404
        return redirect("chat-assets-settings")
    context = _shared(request, "Chat-Elemente", "management")
    context["chat_assets"] = ChatAsset.objects.all()
    return render(request, "ui/chat_assets_settings.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def session_timeout_settings(request):
    """Configure one globally enforced timeout, never scoped to an individual class."""

    _require_portal_admin(request.user)
    if request.method == "POST":
        try:
            minutes = int(request.POST.get("idle_timeout_minutes", ""))
        except (TypeError, ValueError):
            minutes = None
        if minutes is None or not MIN_IDLE_TIMEOUT_MINUTES <= minutes <= MAX_IDLE_TIMEOUT_MINUTES:
            messages.error(
                request,
                f"Bitte gib 0 (keine automatische Abmeldung) oder eine ganze Zahl zwischen 1 und {MAX_IDLE_TIMEOUT_MINUTES} Minuten an.",
            )
            return redirect("session-timeout-settings")
        else:
            key = PortalConfigurationKey.objects.get(key=SESSION_IDLE_TIMEOUT_KEY, active=True)
            value = PortalConfigurationValue.objects.filter(
                key=key, school__isnull=True, school_class__isnull=True
            ).first()
            if value is None:
                PortalConfigurationValue.objects.create(
                    key=key, value=minutes, updated_by=request.user
                )
            else:
                value.value = minutes
                value.updated_by = request.user
                value.save(update_fields=["value", "updated_by", "updated_at"])
            AuditEvent.objects.create(
                actor=request.user,
                action="session.idle_timeout.changed",
                target_type="portal_configuration",
                target_id=SESSION_IDLE_TIMEOUT_KEY,
                metadata={"minutes": minutes},
            )
            messages.success(request, "Automatische Abmeldung gespeichert.")
            return redirect("portal-management")
    context = _shared(request, "Automatische Abmeldung", "management")
    context.update(
        {
            "idle_timeout_minutes": idle_timeout_minutes(),
            "default_idle_timeout_minutes": DEFAULT_IDLE_TIMEOUT_MINUTES,
            "minimum_idle_timeout_minutes": MIN_IDLE_TIMEOUT_MINUTES,
            "maximum_idle_timeout_minutes": MAX_IDLE_TIMEOUT_MINUTES,
        }
    )
    return render(request, "ui/session_timeout_settings.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def role_management(request):
    """Assign only the two roles that are intentionally delegated in the portal UI."""

    if not _may_manage_roles(request.user):
        raise Http404
    manageable_classes = _manageable_classes(request.user)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "revoke":
            assignment = get_object_or_404(
                RoleAssignment,
                pk=request.POST.get("assignment_id"),
                role__in=[Role.DEPUTY_ADMIN, Role.PARENT_REPRESENTATIVE],
                active=True,
            )
            assignment.active = False
            assignment.save(update_fields=["active"])
            AuditEvent.objects.create(
                actor=request.user,
                action="role.revoked",
                target_type="role_assignment",
                target_id=str(assignment.pk),
                metadata={"role": assignment.role, "user_id": assignment.user_id},
            )
            messages.success(request, "Die Rolle wurde entzogen.")
            return redirect("role-management")
        if action != "assign":
            raise Http404
        role = request.POST.get("role")
        user = get_object_or_404(UserAccount, pk=request.POST.get("user_id"), is_active=True)
        school_class = None
        if role == Role.PARENT_REPRESENTATIVE:
            school_class = get_object_or_404(
                manageable_classes, pk=request.POST.get("school_class_id")
            )
            today = timezone.localdate()
            eligible = (
                GuardianChildRelationship.objects.filter(
                    guardian_person=user.person,
                    student_person__classmembership__school_class=school_class,
                    student_person__classmembership__status="active",
                    student_person__classmembership__valid_from__lte=today,
                    status="verified",
                    verified_at__isnull=False,
                    may_view_student_profile=True,
                    valid_from__lte=today,
                )
                .filter(
                    Q(valid_until__isnull=True) | Q(valid_until__gte=today),
                    Q(student_person__classmembership__valid_until__isnull=True)
                    | Q(student_person__classmembership__valid_until__gte=today),
                )
                .exists()
            )
            if not eligible:
                messages.error(
                    request,
                    "Elternvertretungen müssen aktive, bestätigte Sorgeberechtigte der Klasse sein.",
                )
                return redirect("role-management")
        elif role != Role.DEPUTY_ADMIN:
            raise Http404
        assignment, created = (
            RoleAssignment.objects.get_or_create(
                user=user,
                school_class=school_class,
                role=role,
                defaults={"assigned_by": request.user, "active": True},
            )
            if school_class
            else RoleAssignment.objects.get_or_create(
                user=user,
                school_class__isnull=True,
                school__isnull=True,
                role=role,
                defaults={
                    "school_class": None,
                    "school": None,
                    "assigned_by": request.user,
                    "active": True,
                },
            )
        )
        if not created and not assignment.active:
            assignment.active = True
            assignment.assigned_by = request.user
            assignment.save(update_fields=["active", "assigned_by"])
        AuditEvent.objects.create(
            actor=request.user,
            action="role.assigned",
            target_type="role_assignment",
            target_id=str(assignment.pk),
            metadata={
                "role": role,
                "user_id": user.pk,
                "school_class_id": school_class.pk if school_class else None,
            },
        )
        messages.success(request, "Die Rolle wurde zugewiesen.")
        return redirect("role-management")
    active_assignments = RoleAssignment.objects.filter(
        active=True, role__in=[Role.DEPUTY_ADMIN, Role.PARENT_REPRESENTATIVE]
    ).select_related("user__person", "school_class__school", "assigned_by")
    guardian_users = (
        UserAccount.objects.filter(
            person__guardian_relationships__status="verified",
            is_active=True,
        )
        .select_related("person")
        .distinct()
        .order_by("person__last_name", "person__first_name")
    )
    context = _shared(request, "Rollen & Elternvertretung", "management")
    context.update(
        {
            "assignments": active_assignments,
            "portal_admin_candidates": UserAccount.objects.filter(is_active=True)
            .select_related("person")
            .order_by("email"),
            "guardian_candidates": guardian_users,
            "manageable_classes": manageable_classes,
        }
    )
    return render(request, "ui/role_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def school_management(request):
    """Manage the small, enabled school set without exposing Django admin first."""

    _require_portal_admin(request.user)
    manageable_schools = _manageable_schools(request.user)
    school_years = SchoolYear.objects.order_by("-is_active", "-starts_on")
    current_year = school_years.filter(is_active=True).first()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "activate_school":
            if not _may_manage_school_catalog(request.user):
                raise Http404
            school = get_object_or_404(School.objects, pk=request.POST.get("school_id"))
            school.is_active = True
            school.save(update_fields=["is_active", "updated_at"])
            AuditEvent.objects.create(
                actor=request.user,
                action="school.activated",
                target_type="school",
                target_id=str(school.pk),
            )
            messages.success(request, f"{school.name} ist jetzt im Portal eingerichtet.")
            return redirect("school-management")

        if action == "add_class":
            school = get_object_or_404(manageable_schools, pk=request.POST.get("school_id"))
            school_year = get_object_or_404(school_years, pk=request.POST.get("school_year_id"))
            grade_level = request.POST.get("grade_level", "").strip()
            label = request.POST.get("class_label", "").strip()[:64]
            code = request.POST.get("class_code", "").strip()[:64]
            if not grade_level.isdigit() or not 1 <= int(grade_level) <= 13:
                messages.error(request, "Bitte wähle einen Jahrgang zwischen 1 und 13.")
            else:
                if not label:
                    label = f"Klasse {grade_level}"
                if not code:
                    code = label.casefold().replace(" ", "-")[:64]
                school_class, created = SchoolClass.objects.get_or_create(
                    school=school,
                    school_year=school_year,
                    code=code,
                    defaults={
                        "name": label,
                        "display_name": label,
                        "grade_level": grade_level,
                        "status": "active",
                        "valid_from": school_year.starts_on,
                        "valid_until": school_year.ends_on,
                    },
                )
                if created:
                    AuditEvent.objects.create(
                        actor=request.user,
                        action="school_class.created",
                        target_type="school_class",
                        target_id=str(school_class.pk),
                        metadata={"school_id": school.pk, "grade_level": grade_level},
                    )
                    messages.success(request, f"{label} wurde für {school.name} angelegt.")
                else:
                    messages.info(
                        request, "Diese Klasse ist für das gewählte Schuljahr bereits vorhanden."
                    )
            return redirect("school-management")

        raise Http404

    query = request.GET.get("q", "").strip()
    candidates = School.objects.none()
    if len(query) >= 2 and _may_manage_school_catalog(request.user):
        candidates = (
            School.objects.filter(is_active=False)
            .filter(
                Q(name__icontains=query)
                | Q(search_name__icontains=query.casefold())
                | Q(city__icontains=query)
                | Q(postal_code__startswith=query)
            )
            .order_by("name")[:50]
        )
    active_schools = manageable_schools.prefetch_related("classes").order_by("name")
    context = _shared(request, "Schulen & Klassen", "management")
    context.update(
        {
            "active_schools": active_schools,
            "candidate_schools": candidates,
            "query": query,
            "school_years": school_years,
            "current_year": current_year,
            "may_manage_school_catalog": _may_manage_school_catalog(request.user),
        }
    )
    return render(request, "ui/school_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def school_detail(request, school_id):
    _require_portal_admin(request.user)
    school = get_object_or_404(_manageable_schools(request.user), pk=school_id)
    tab = request.GET.get("tab", "data")
    if tab not in {"data", "classes", "adapters"}:
        tab = "data"
    if request.method == "POST":
        action = request.POST.get("action")
        if request.POST.get("deactivate_school") == "yes":
            school.is_active = False
            school.save(update_fields=["is_active"])
            messages.success(
                request,
                "Die Schule wurde aus dem Portal entfernt. Historische Zuordnungen bleiben erhalten.",
            )
            return redirect("school-management")
        if action == "save_school":
            for field, limit in {
                "address": 200,
                "postal_code": 10,
                "city": 120,
                "website": 200,
            }.items():
                setattr(school, field, request.POST.get(field, "").strip()[:limit])
            school.save()
        elif action == "add_class":
            year = SchoolYear.objects.filter(pk=request.POST.get("school_year_id")).first()
            if year is None:
                messages.error(request, "Bitte wähle ein vorhandenes Schuljahr aus.")
                return redirect(f"{reverse('school-detail', args=[school.pk])}?tab={tab}")
            label = request.POST.get("class_label", "").strip()[:64]
            if label:
                SchoolClass.objects.get_or_create(
                    school=school,
                    school_year=year,
                    code=(request.POST.get("class_code", "").strip() or label)
                    .casefold()
                    .replace(" ", "-")[:64],
                    defaults={
                        "name": label,
                        "display_name": label,
                        "grade_level": request.POST.get("grade_level", "")[:32],
                        "status": "active",
                        "valid_from": year.starts_on,
                        "valid_until": year.ends_on,
                    },
                )
        elif action == "set_adapters":
            messages.info(
                request,
                "Adapter werden direkt als Schulintegration angelegt und dort konfiguriert.",
            )
        messages.success(request, "Schule gespeichert.")
        return redirect(f"{reverse('school-detail', args=[school.pk])}?tab={tab}")
    context = _shared(request, school.name, "management")
    context.update(
        {
            "school": school,
            "active_tab": tab,
            "classes": SchoolClass.objects.filter(school=school)
            .select_related("school_year")
            .order_by("school_year__starts_on", "display_name", "name"),
            "adapters": PortalAdapter.objects.filter(school=school).order_by("name", "provider"),
            "school_years": SchoolYear.objects.order_by("-is_active", "-starts_on"),
            "map_bounds": {"south": 52.329, "west": 10.623, "north": 52.509, "east": 10.913},
        }
    )
    return render(request, "ui/school_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def school_class_detail(request, class_id):
    """Edit one class and its school-approved module availability."""

    _require_portal_admin(request.user)
    school_class = get_object_or_404(_manageable_classes(request.user), pk=class_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_class":
            school_class.name = request.POST.get("name", "").strip()[:64] or school_class.name
            school_class.display_name = request.POST.get("display_name", "").strip()[:100]
            school_class.code = request.POST.get("code", "").strip()[:64]
            school_class.grade_level = request.POST.get("grade_level", "").strip()[:32]
            school_class.save(update_fields=["name", "display_name", "code", "grade_level"])
            messages.success(request, "Klassenstammdaten gespeichert.")
        elif action == "toggle_module":
            module = get_object_or_404(
                PortalAdapterModule,
                pk=request.POST.get("module_id"),
                adapter__school=school_class.school,
            )
            assigned = module.available_to_classes.filter(pk=school_class.pk).exists()
            if assigned:
                module.available_to_classes.remove(school_class)
            else:
                module.available_to_classes.add(school_class)
            messages.success(
                request,
                f"{module.label} für diese Klasse {'freigegeben' if not assigned else 'entfernt'}.",
            )
        return redirect("school-class-detail", class_id=school_class.pk)
    modules = (
        PortalAdapterModule.objects.filter(adapter__school=school_class.school)
        .select_related("adapter", "adapter__definition")
        .prefetch_related("available_to_classes")
        .order_by("adapter__name", "label")
    )
    module_rows = [
        {"module": module, "assigned": module.available_to_classes.filter(pk=school_class.pk).exists()}
        for module in modules
    ]
    context = _shared(request, school_class.display_name or school_class.name, "management")
    context.update({"school_class": school_class, "module_rows": module_rows})
    return render(request, "ui/school_class_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def school_catalog_import(request):
    """Preview a bounded set of matching CSV records before importing them."""

    _require_portal_admin(request.user)
    if not _may_manage_school_catalog(request.user):
        raise Http404
    context = _shared(request, "Schulliste importieren", "management")
    context.update({"rows": [], "errors": [], "query": ""})

    if request.method == "POST" and request.POST.get("action") == "import_selected":
        selected_rows = request.POST.getlist("selected_row")
        try:
            if not selected_rows:
                raise ValueError("Bitte wähle mindestens eine Schule aus.")
            if len(selected_rows) > 250:
                raise ValueError("Bitte importiere höchstens 250 Schulen pro Auswahl.")
            records = []
            for encoded in selected_rows:
                record = json.loads(base64.urlsafe_b64decode(encoded.encode()).decode("utf-8"))
                records.append({field: record.get(field, "") for field in EXPECTED_FIELDS})
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", encoding="utf-8", newline="", delete=False
            ) as handle:
                temporary_path = Path(handle.name)
                writer = csv.DictWriter(handle, fieldnames=sorted(EXPECTED_FIELDS))
                writer.writeheader()
                writer.writerows(records)
            try:
                _encoding, stats = import_schools(
                    temporary_path, source_name="portal-schulliste.csv"
                )
            finally:
                temporary_path.unlink(missing_ok=True)
            AuditEvent.objects.create(
                actor=request.user,
                action="school.catalog_imported",
                target_type="school_catalog",
                target_id="selection",
                metadata={"created": stats.created, "updated": stats.updated},
            )
            messages.success(
                request,
                f"{stats.created + stats.updated} Schule(n) importiert. Suche sie jetzt und füge die gewünschte Schule zum Portal hinzu.",
            )
            return redirect("school-management")
        except (UnicodeError, ValueError, json.JSONDecodeError, csv.Error) as exc:
            context["errors"] = [str(exc)]

    elif request.method == "POST":
        upload = request.FILES.get("csv_file")
        query = request.POST.get("query", "").strip()
        context["query"] = query
        if upload is None:
            context["errors"] = ["Bitte wähle eine CSV-Datei aus."]
        elif upload.size > 60 * 1024 * 1024:
            context["errors"] = ["Die CSV-Datei darf höchstens 60 MB groß sein."]
        elif len(query) < 2:
            context["errors"] = [
                "Gib mindestens zwei Zeichen ein, damit nur passende Schulen vorgeschlagen werden."
            ]
        else:
            try:
                data = upload.read()
                encoding = detect_encoding(data)
                reader = csv.DictReader(io.StringIO(data.decode(encoding), newline=""))
                if not reader.fieldnames or not EXPECTED_FIELDS.issubset(set(reader.fieldnames)):
                    raise ValueError(
                        "Die CSV-Spalten entsprechen nicht dem erwarteten Schulformat."
                    )
                needle = query.casefold()
                rows = []
                matched = 0
                for row in reader:
                    haystack = " ".join(
                        str(row.get(field) or "")
                        for field in ("name", "city", "zip", "school_type")
                    ).casefold()
                    if needle not in haystack:
                        continue
                    matched += 1
                    if len(rows) >= 250:
                        continue
                    cleaned = {field: str(row.get(field) or "") for field in EXPECTED_FIELDS}
                    if cleaned["id"] and cleaned["name"]:
                        cleaned["encoded"] = base64.urlsafe_b64encode(
                            json.dumps(cleaned, ensure_ascii=False).encode("utf-8")
                        ).decode("ascii")
                        rows.append(cleaned)
                context.update(
                    {
                        "rows": rows,
                        "uploaded_name": upload.name,
                        "matched": matched,
                        "truncated": matched > len(rows),
                    }
                )
                if not rows:
                    context["errors"] = [
                        "Zu dieser Suche wurden keine Schulen in der Datei gefunden."
                    ]
            except (UnicodeError, ValueError, csv.Error) as exc:
                context["errors"] = [str(exc)]

    return render(request, "ui/school_catalog_import.html", context)


@login_required
def school_setup_export(request):
    """Download the current setup as the only supported import template."""

    _require_portal_admin(request.user)
    if not _may_manage_school_catalog(request.user):
        raise Http404
    response = HttpResponse(export_school_setup_csv(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = content_disposition_header(
        True, "klassid-schulen-klassen-adapter.csv"
    )
    return response


@login_required
@require_http_methods(["GET", "POST"])
def school_setup_import(request):
    """Preview then atomically apply a bounded school setup CSV."""

    _require_portal_admin(request.user)
    if not _may_manage_school_catalog(request.user):
        raise Http404
    session_key = "school_setup_import_rows"
    context = _shared(request, "Schulstruktur importieren", "management")
    context.update({"errors": [], "preview_rows": [], "preview_count": 0})
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "preview":
            upload = request.FILES.get("csv_file")
            if upload is None:
                context["errors"] = ["Bitte wähle eine CSV-Datei aus."]
            else:
                try:
                    rows = parse_school_setup_csv(upload.read())
                    request.session[session_key] = rows
                    request.session.modified = True
                    context.update(
                        {
                            "preview_rows": rows[:20],
                            "preview_count": len(rows),
                            "uploaded_name": upload.name,
                        }
                    )
                except ValueError as exc:
                    context["errors"] = [str(exc)]
        elif action == "apply":
            rows = request.session.get(session_key)
            if not rows:
                context["errors"] = [
                    "Die Importvorschau ist abgelaufen. Bitte lade die Datei erneut zur Prüfung hoch."
                ]
            else:
                try:
                    stats = apply_school_setup_rows(rows)
                    request.session.pop(session_key, None)
                    AuditEvent.objects.create(
                        actor=request.user,
                        action="school.setup_imported",
                        target_type="school_setup",
                        target_id="csv",
                        metadata={field: getattr(stats, field) for field in stats.__dataclass_fields__},
                    )
                    messages.success(
                        request,
                        "Import abgeschlossen: "
                        f"{stats.schools_created + stats.schools_updated} Schulen, "
                        f"{stats.classes_created + stats.classes_updated} Klassen, "
                        f"{stats.adapters_created + stats.adapters_updated} Adapter und "
                        f"{stats.modules_created + stats.modules_updated} Module verarbeitet.",
                    )
                    return redirect("school-management")
                except ValueError as exc:
                    context["errors"] = [str(exc)]
    return render(request, "ui/school_setup_import.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def portal_adapter_management(request):
    """Configure reviewed portal connectors without collecting credentials here."""
    _require_portal_admin(request.user)
    if request.method == "POST":
        provider = request.POST.get("provider", "")
        if provider not in ADAPTER_CATALOG:
            messages.error(request, "Bitte wähle einen bekannten Adapter aus.")
            return redirect("portal-adapter-management")
        definition = provider_definition(provider)
        adapter_definition = PortalAdapterDefinition.objects.filter(provider=provider).first()
        name = request.POST.get("name", "").strip()[:120] or definition["label"]
        school = (
            _manageable_schools(request.user).filter(pk=request.POST.get("school_id")).first()
        )
        if school is None:
            messages.error(request, "Bitte wähle die Schule für diese Integration aus.")
            return redirect("portal-adapter-management")
        adapter, created = PortalAdapter.objects.get_or_create(
            provider=provider,
            name=name,
            school=school,
            defaults={
                "definition": adapter_definition,
                "base_url": definition["default_url"],
                "requires_child_credentials": request.POST.get("requires_child_credentials")
                == "on",
                "is_enabled": request.POST.get("is_enabled") == "on",
            },
        )
        if created:
            seed_default_modules(adapter)
            adapter.modules.update(requires_child_credentials=adapter.requires_child_credentials)
            AuditEvent.objects.create(
                actor=request.user,
                action="portal_adapter.created",
                target_type="portal_adapter",
                target_id=str(adapter.pk),
                metadata={"provider": provider},
            )
            messages.success(request, f"{definition['label']} wurde angelegt.")
        else:
            messages.info(request, "Dieser Adapter ist für die Schule bereits vorhanden.")
        return redirect("portal-adapter-detail", adapter_id=adapter.pk)
    adapters = _manageable_portal_adapters(request.user).prefetch_related("modules")
    selected_school_id = request.GET.get("school_id", "").strip()
    selected_school = (
        _manageable_schools(request.user).filter(pk=selected_school_id).first()
        if selected_school_id.isdigit()
        else None
    )
    context = _shared(request, "Schulportal-Adapter", "management")
    context.update(
        {
            "adapters": adapters,
            "adapter_definitions": PortalAdapterDefinition.objects.filter(
                is_published=True
            ).prefetch_related("modules"),
            "adapter_catalog": ADAPTER_CATALOG.items(),
            "manageable_schools": _manageable_schools(request.user),
            "selected_school": selected_school,
        }
    )
    return render(request, "ui/portal_adapter_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def portal_adapter_definition_detail(request, definition_id):
    _require_portal_admin(request.user)
    definition = get_object_or_404(PortalAdapterDefinition, pk=definition_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_definition":
            definition.label = request.POST.get("label", "").strip()[:120] or definition.label
            definition.hint = request.POST.get("hint", "").strip()[:300]
            definition.default_url = request.POST.get("default_url", "").strip()[:200]
            definition.integration_type = request.POST.get(
                "integration_type", definition.integration_type
            )
            definition.is_published = request.POST.get("is_published") == "on"
            definition.is_technically_reviewed = request.POST.get("is_technically_reviewed") == "on"
            definition.save()
            messages.success(request, "Adapterdefinition gespeichert.")
        elif action in {"save_module", "add_module"}:
            module = (
                get_object_or_404(
                    PortalAdapterDefinitionModule,
                    pk=request.POST.get("module_id"),
                    definition=definition,
                )
                if action == "save_module"
                else PortalAdapterDefinitionModule(definition=definition)
            )
            module.key = slugify(request.POST.get("key", "") or request.POST.get("label", ""))[:80]
            module.label = request.POST.get("label", "").strip()[:120]
            module.description = request.POST.get("description", "").strip()[:300]
            module.access_model = request.POST.get(
                "access_model", PortalAdapterDefinitionModule.AccessModel.NONE
            )
            module.is_published = request.POST.get("is_published") == "on"
            if not module.key or not module.label:
                messages.error(request, "Technische Kennung und Bezeichnung sind erforderlich.")
            elif definition.modules.exclude(pk=module.pk).filter(key=module.key).exists():
                messages.error(request, "Diese Modulkennung ist in der Definition bereits vorhanden.")
            else:
                module.save()
                messages.success(request, "Moduldefinition gespeichert.")
        return redirect("portal-adapter-definition-detail", definition_id=definition.pk)
    context = _shared(request, definition.label, "management")
    context.update(
        {
            "adapter_definition": definition,
            "definition_modules": definition.modules.all(),
            "integration_types": PortalAdapterDefinition.IntegrationType.choices,
            "access_models": PortalAdapterDefinitionModule.AccessModel.choices,
        }
    )
    return render(request, "ui/portal_adapter_definition_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def portal_adapter_detail(request, adapter_id):
    _require_portal_admin(request.user)
    adapter = get_object_or_404(
        _manageable_portal_adapters(request.user).prefetch_related("modules"),
        pk=adapter_id,
    )
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_adapter":
            adapter_id = adapter.pk
            adapter.delete()
            AuditEvent.objects.create(
                actor=request.user,
                action="portal_adapter.deleted",
                target_type="portal_adapter",
                target_id=str(adapter_id),
            )
            messages.success(request, "Adapter wurde gelöscht.")
            return redirect("portal-adapter-management")
        if action == "save_adapter":
            adapter.base_url = request.POST.get("base_url", "").strip()[:200]
            if adapter.provider != PortalAdapter.Provider.WEBUNTIS:
                adapter.project_identifier = request.POST.get("project_identifier", "").strip()[:120]
                adapter.institution_identifier = request.POST.get("institution_identifier", "").strip()[
                    :120
                ]
                adapter.school_number = request.POST.get("school_number", "").strip()[:40]
            adapter.configuration_note = request.POST.get("configuration_note", "").strip()[:1200]
            adapter.is_enabled = request.POST.get("is_enabled") == "on"
            adapter.requires_child_credentials = (
                request.POST.get("requires_child_credentials") == "on"
            )
            try:
                adapter.full_clean()
            except ValidationError:
                messages.error(request, "Bitte prüfe die Adresse des Adapters.")
            else:
                adapter.save()
                adapter.modules.update(
                    requires_child_credentials=adapter.requires_child_credentials
                )
                AuditEvent.objects.create(
                    actor=request.user,
                    action="portal_adapter.updated",
                    target_type="portal_adapter",
                    target_id=str(adapter.pk),
                )
                messages.success(request, "Adapter-Konfiguration gespeichert.")
        elif action in {"save_module", "toggle_module"}:
            module = get_object_or_404(adapter.modules, pk=request.POST.get("module_id"))
            module.is_enabled = request.POST.get("is_enabled") == "on"
            if action == "save_module":
                module.requires_child_credentials = (
                    request.POST.get("requires_child_credentials") == "on"
                )
                module.configuration_note = request.POST.get("configuration_note", "").strip()[
                    :1200
                ]
                module.access_model = request.POST.get("access_model", module.access_model)
            if module.is_enabled and module.status == PortalAdapterModule.Status.NOT_CONFIGURED:
                module.status = PortalAdapterModule.Status.READY
            module.save()
            if action == "save_module":
                module.available_to_classes.set(
                    SchoolClass.objects.filter(
                        pk__in=request.POST.getlist("available_to_classes"),
                        school=adapter.school,
                    )
                )
            AuditEvent.objects.create(
                actor=request.user,
                action="portal_adapter.module.updated",
                target_type="portal_adapter_module",
                target_id=str(module.pk),
                metadata={"adapter_id": adapter.pk, "enabled": module.is_enabled},
            )
            messages.success(request, f"Modul „{module.label}“ gespeichert.")
        elif action == "add_module":
            label = request.POST.get("label", "").strip()[:120]
            key = slugify(request.POST.get("key", "") or label)[:80]
            # Stable application key; the German display label must not create
            # ``abwesenheiten`` because feature/consent resolution uses
            # ``absences``.
            if adapter.provider == PortalAdapter.Provider.WEBUNTIS and key in {
                "abwesenheiten",
                "abwesenheit",
            }:
                key = "absences"
            if not label or not key:
                messages.error(request, "Bitte gib für das neue Modul mindestens einen Namen an.")
            elif adapter.modules.filter(key=key).exists():
                messages.error(request, "Diese Modulkennung gibt es bei diesem Adapter bereits.")
            else:
                module = PortalAdapterModule.objects.create(
                    adapter=adapter,
                    key=key,
                    label=label,
                    description=request.POST.get("description", "").strip()[:300],
                )
                AuditEvent.objects.create(
                    actor=request.user,
                    action="portal_adapter.module.created",
                    target_type="portal_adapter_module",
                    target_id=str(module.pk),
                    metadata={"adapter_id": adapter.pk},
                )
                messages.success(request, f"Modul „{module.label}“ angelegt.")
        return redirect("portal-adapter-detail", adapter_id=adapter.pk)
    context = _shared(request, adapter.name, "management")
    context.update(
        {
            "adapter": adapter,
            "provider_definition": provider_definition(adapter.provider),
            "adapter_definition": adapter.definition,
            "school_classes": SchoolClass.objects.filter(
                school=adapter.school, status="active"
            ).order_by("display_name", "name"),
        }
    )
    return render(request, "ui/portal_adapter_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def chat_retention_settings(request):
    """Let portal administrators decide whether chat messages expire at all."""

    _require_portal_admin(request.user)
    if request.method == "POST":
        category = get_object_or_404(ChatRetentionCategory, pk=request.POST.get("category_id"))
        automatic_deletion_enabled = request.POST.get("automatic_deletion_enabled") == "on"
        try:
            retention_days = int(request.POST.get("retention_days", category.retention_days))
        except (TypeError, ValueError):
            retention_days = 0
        if automatic_deletion_enabled and not 1 <= retention_days <= 3650:
            messages.error(request, "Für eine automatische Löschung gib bitte 1 bis 3.650 Tage an.")
        else:
            category.automatic_deletion_enabled = automatic_deletion_enabled
            if retention_days:
                category.retention_days = retention_days
            category.save(update_fields=["automatic_deletion_enabled", "retention_days"])
            AuditEvent.objects.create(
                actor=request.user,
                action="chat.retention.changed",
                target_type="chat_retention_category",
                target_id=str(category.pk),
                metadata={
                    "automatic_deletion_enabled": automatic_deletion_enabled,
                    "days": category.retention_days,
                },
            )
            messages.success(
                request,
                "Automatische Löschung aktiviert."
                if automatic_deletion_enabled
                else "Automatische Löschung deaktiviert. Bestehende Nachrichten bleiben erhalten.",
            )
        return redirect("chat-retention-settings")
    context = _shared(request, "Chat-Aufbewahrung", "management")
    context["retention_categories"] = ChatRetentionCategory.objects.order_by(
        "intended_for_events", "name"
    )
    return render(request, "ui/chat_retention_settings.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def presentation_poll_settings(request):
    """Admin-only storage and restart screen for the presentation poll."""
    _require_portal_admin(request.user)
    school_class = _class_or_404(request.user, request)
    if request.method == "POST":
        action = request.POST.get("action")
        poll = get_object_or_404(
            EventPoll, pk=request.POST.get("poll_id"), school_class=school_class
        )
        meeting_url = request.POST.get("meeting_url", "").strip()[:200]
        if meeting_url and not meeting_url.startswith(("https://", "http://")):
            messages.error(
                request, "Bitte gib einen gültigen Teams- oder Meeting-Link mit https:// ein."
            )
            return redirect("presentation-poll-settings")
        if action == "save_link":
            poll.meeting_url = meeting_url
            poll.save(update_fields=["meeting_url"])
            messages.success(request, "Der aktuelle Teams-Link wurde gespeichert.")
        elif action == "restart":
            try:
                closes_at = timezone.datetime.fromisoformat(request.POST.get("closes_at", ""))
                if timezone.is_naive(closes_at):
                    closes_at = timezone.make_aware(closes_at)
                if closes_at <= timezone.now():
                    raise ValueError
            except (TypeError, ValueError):
                messages.error(request, "Bitte gib ein zukünftiges Ende der Umfrage an.")
                return redirect("presentation-poll-settings")
            new_poll = EventPoll.objects.create(
                school_class=school_class,
                title=poll.title,
                description=poll.description,
                meeting_url=meeting_url,
                closes_at=closes_at,
                created_by=request.user,
            )
            EventPollOption.objects.bulk_create(
                [
                    EventPollOption(
                        poll=new_poll, starts_at=option.starts_at, ends_at=option.ends_at
                    )
                    for option in poll.options.all()
                ]
            )
            poll.closes_at = timezone.now()
            poll.save(update_fields=["closes_at"])
            messages.success(request, "Die Terminumfrage wurde neu gestartet.")
        return redirect("presentation-poll-settings")
    polls = (
        EventPoll.objects.filter(school_class=school_class)
        .prefetch_related("options")
        .select_related("finalized_event")
        .order_by("-created_at")[:12]
    )
    context = _shared(request, "Terminumfrage", "management")
    context.update({"polls": polls, "current_poll": polls[0] if polls else None})
    return render(request, "ui/presentation_poll_settings.html", context)


@login_required
def registration_invitation(request):
    _require_portal_admin(request.user)
    context = _shared(request, "Anmeldung weitergeben", "management")
    context["registration_url"] = request.build_absolute_uri("/registrieren/")
    return render(request, "ui/registration_invitation.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def family_invitations(request):
    _require_portal_admin(request.user)
    classes = _manageable_classes(request.user)
    if request.method == "POST":
        school_class = get_object_or_404(classes, pk=request.POST.get("school_class"))
        try:
            count = int(request.POST.get("count", "1"))
            max_uses = int(request.POST.get("max_uses", "1"))
        except ValueError:
            count = 0
            max_uses = 0
        family_names = [
            line.strip()
            for line in request.POST.get("family_names", "").splitlines()
            if line.strip()
        ]
        if not 1 <= count <= 100:
            messages.error(request, "Bitte wähle zwischen 1 und 100 Einladungen.")
        elif not 1 <= max_uses <= 100:
            messages.error(request, "Bitte wähle zwischen 1 und 100 Verwendungen pro Code.")
        elif len(family_names) > count:
            messages.error(
                request,
                "Es wurden mehr Familiennamen als Einladungen angegeben. Bitte erhöhe die Anzahl.",
            )
        else:
            output, batch_id = create_family_handout(
                school_class=school_class,
                count=count,
                created_by=request.user,
                family_names=family_names,
                max_uses=max_uses,
            )
            class_label = slugify(school_class.display_name or school_class.name) or "klasse"
            response = FileResponse(
                output,
                as_attachment=True,
                filename=f"KlassID-Familieneinladungen-{class_label}.pdf",
                content_type="application/pdf",
            )
            response["X-KlassID-Batch"] = str(batch_id)
            return response
    context = _shared(request, "QR-Familieneinladungen", "management")
    context["school_classes"] = classes
    return render(request, "ui/family_invitations.html", context)


@login_required
def registration_invitation_qr(request):
    _require_portal_admin(request.user)
    import qrcode
    import qrcode.image.svg

    output = BytesIO()
    qrcode.make(
        request.build_absolute_uri("/registrieren/"),
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=12,
        border=2,
    ).save(output)
    response = HttpResponse(output.getvalue(), content_type="image/svg+xml")
    response["Cache-Control"] = "private, max-age=300"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
@require_POST
def pilot_report(request):
    school_class = _class_or_404(request.user, request)
    kind = request.POST.get("kind", "note")
    if kind not in PilotReport.Kind.values:
        kind = PilotReport.Kind.NOTE
    description = request.POST.get("description", "").strip()
    if not description:
        raise Http404
    page_path = request.POST.get("page_path", "/")[:300]
    if not page_path.startswith("/") or page_path.startswith("//"):
        page_path = "/"
    report = PilotReport.objects.create(
        reporter=request.user,
        school_class=school_class,
        kind=kind,
        page_path=page_path,
        description=description[:3000],
    )
    screenshot = request.FILES.get("screenshot")
    if screenshot:
        encoded = sanitized_profile_photo(screenshot)
        report.screenshot.save(
            f"{secrets.token_urlsafe(18)}.webp",
            ContentFile(encoded),
            save=True,
        )
    messages.success(request, "Danke. Deine Meldung wurde an die Pilotverwaltung übermittelt.")
    return redirect(page_path)


@login_required
def more(request):
    context = _shared(request, "Bereiche", "more")
    school_class = _class_or_404(request.user, request)
    catalog = _menu_catalog()
    stored = (
        school_class.visible_menu_items if isinstance(school_class.visible_menu_items, dict) else {}
    )
    configured = stored.get("items") or [
        {"key": key, "group": item[3]} for key, item in catalog.items()
    ]
    configured_keys = {item.get("key") for item in configured}
    configured.extend(
        {"key": key, "group": item[3]}
        for key, item in catalog.items()
        if key not in configured_keys
    )
    labels = {
        "class": "Klassenleben",
        "communication": "Kommunikation",
        "account": "Mein Konto",
        "beta": "Beta",
    }
    labels.update(stored.get("group_labels") or {})
    # These features remain available, but are deliberately kept outside the
    # active production navigation until their final UX is approved.
    for row in configured:
        if row.get("key") in {"tutorial", "mobility"}:
            row["group"] = "beta"
    groups = []
    # Personal settings are the most frequent entry point, so they lead the
    # menu and are the only group opened initially in the template.
    for group_key in ("account", "communication", "class", "beta"):
        entries = []
        for row in configured:
            if (
                row.get("group") != group_key
                or row.get("key") not in catalog
                or row.get("visible", True) is False
            ):
                continue
            label, url, icon, _default_group = catalog[row["key"]]
            entries.append(
                {"key": row["key"], "label": row.get("label") or label, "url": url, "icon": icon}
            )
        groups.append({"key": group_key, "label": labels[group_key], "items": entries})
    if _can_manage_portal(request.user):
        groups.append(
            {
                "key": "settings",
                "label": "Einstellungen",
                "open": request.GET.get("bereich") == "einstellungen",
                "sections": [
                    {
                        "key": "portal-management",
                        "label": "Portalverwaltung",
                        "items": [
                            {
                                "key": "model-visualizer",
                                "label": "Django-Modellvisualisierung",
                                "url": reverse("model-visualizer"),
                                "icon": "document",
                            },
                            {
                                "key": "pilot-reports",
                                "label": "Pilotmeldungen",
                                "url": reverse("portal-management") + "#pilotmeldungen",
                                "icon": "news",
                            },
                            {
                                "key": "session-timeout",
                                "label": "Automatische Abmeldung",
                                "url": reverse("session-timeout-settings"),
                                "icon": "consent",
                            },
                            {
                                "key": "system-status",
                                "label": "Systemstatus",
                                "url": reverse("monitoring-dashboard"),
                                "icon": "home",
                            },
                            {
                                "key": "menu-structure",
                                "label": "Menüstruktur",
                                "url": reverse("menu-management"),
                                "icon": "more",
                            },
                            {
                                "key": "family-invitations",
                                "label": "Registrierungen & Einladungen",
                                "url": reverse("family-invitations"),
                                "icon": "document",
                            },
                        ],
                    },
                    {
                        "key": "chat-settings",
                        "label": "Chat",
                        "items": [
                            {
                                "key": "chat-retention",
                                "label": "Chat-Aufbewahrung",
                                "url": reverse("chat-retention-settings"),
                                "icon": "chat",
                            },
                            {
                                "key": "chat-assets",
                                "label": "Chat-Emojis & Sticker",
                                "url": reverse("chat-assets-settings"),
                                "icon": "chat",
                            },
                        ],
                    },
                    {
                        "key": "design-settings",
                        "label": "Design",
                        "items": [
                            {
                                "key": "themes",
                                "label": "Themes",
                                "url": reverse("theme-management"),
                                "icon": "photo",
                            },
                            {
                                "key": "design-system",
                                "label": "Designsystem & CSS-Tokens",
                                "url": reverse("design-system"),
                                "icon": "photo",
                            },
                        ],
                    },
                    {
                        "key": "school-settings",
                        "label": "Schulverwaltung",
                        "items": [
                            {
                                "key": "schools",
                                "label": "Schulen",
                                "url": reverse("school-management"),
                                "icon": "teacher",
                            },
                            {
                                "key": "classes",
                                "label": "Klassen",
                                "url": reverse("school-management") + "#klassen",
                                "icon": "teacher",
                            },
                            {
                                "key": "adapters",
                                "label": "Adapter",
                                "url": reverse("portal-adapter-management"),
                                "icon": "calendar",
                            },
                            {
                                "key": "modules",
                                "label": "Module",
                                "url": reverse("portal-adapter-management") + "#module",
                                "icon": "document",
                            },
                        ],
                    },
                    {
                        "key": "permission-settings",
                        "label": "Berechtigungen",
                        "items": [
                            {
                                "key": "role-permissions",
                                "label": "Rollenberechtigungen",
                                "url": reverse("role-permissions"),
                                "icon": "consent",
                            },
                            {
                                "key": "roles",
                                "label": "Rollenverwaltung",
                                "url": reverse("role-management"),
                                "icon": "people",
                            },
                            {
                                "key": "people",
                                "label": "Personenverwaltung",
                                "url": reverse("role-people"),
                                "icon": "people",
                            },
                        ],
                    },
                ],
            }
        )
    context["menu_groups"] = groups
    return render(request, "ui/more.html", context)


@login_required
def learning_portals(request):
    school_class = _class_or_404(request.user, request)
    adapters = (
        PortalAdapter.objects.filter(
            provider__in=(
                PortalAdapter.Provider.MUNDO,
                PortalAdapter.Provider.WIR_LERNEN_ONLINE,
            ),
            is_enabled=True,
            modules__is_enabled=True,
        )
        .filter(school=school_class.school)
        .prefetch_related("modules__available_to_classes")
        .distinct()
        .order_by("name")
    )
    portal_rows = []
    for adapter in adapters:
        modules = [
            module
            for module in adapter.modules.all()
            if module.is_enabled
            and (
                not module.available_to_classes.all()
                or school_class in module.available_to_classes.all()
            )
        ]
        if not modules:
            continue
        portal_rows.append(
            {
                "adapter": adapter,
                "hint": provider_definition(adapter.provider)["hint"],
                "modules": modules,
            }
        )
    context = _shared(request, "Lernportale", "more")
    context["portal_rows"] = portal_rows
    return render(request, "ui/learning_portals.html", context)


def _menu_catalog():
    return {
        "events": ("Veranstaltungen & Mitbringen", "/mehr/veranstaltungen/", "event", "class"),
        "mobility": ("Fahrgemeinschaft", "/mehr/mobilitaet/", "people", "class"),
        "news": ("Aktuelles", "/mehr/aktuelles/", "news", "class"),
        "gallery": ("Fotos & Galerie", "/mehr/fotos/", "photo", "class"),
        "meals": ("Speiseplan", "/mehr/speiseplan/", "event", "class"),
        "learning_portals": ("Lernportale", "/mehr/lernportale/", "document", "class"),
        "school_data": ("Schulzugänge", "/mehr/familie/?tab=overview", "calendar", "account"),
        "contacts": ("Adressliste", "/kontakte/", "people", "communication"),
        "profile": ("Mein Konto", "/einstellungen/profil/", "people", "account"),
        "family": ("Familien-Zentrale", "/mehr/familie/", "people", "account"),
        "tutorial": ("Einführung", "/tutorial/", "home", "account"),
    }


@login_required
@require_http_methods(["GET", "POST"])
def menu_management(request):
    _require_portal_admin(request.user)
    school_class = _class_or_404(request.user, request)
    catalog = _menu_catalog()
    stored = (
        school_class.visible_menu_items if isinstance(school_class.visible_menu_items, dict) else {}
    )
    existing = {item.get("key"): item for item in stored.get("items", [])}
    if request.method == "POST":
        items = []
        for key in catalog:
            group = request.POST.get(f"group_{key}", catalog[key][3])
            if group not in {"class", "communication", "account", "beta"}:
                group = catalog[key][3]
            try:
                position = int(request.POST.get(f"position_{key}", "99"))
            except ValueError:
                position = 99
            label = request.POST.get(f"label_{key}", "").strip()[:80]
            items.append(
                {
                    "key": key,
                    "group": group,
                    "position": position,
                    "visible": request.POST.get(f"visible_{key}") == "on",
                    "label": label,
                }
            )
        items.sort(key=lambda item: (item["group"], item["position"], item["key"]))
        school_class.visible_menu_items = {
            "group_labels": {
                "class": request.POST.get("label_class", "Klassenleben")[:60],
                "communication": request.POST.get("label_communication", "Kommunikation")[:60],
                "account": request.POST.get("label_account", "Mein Konto")[:60],
                "beta": request.POST.get("label_beta", "Beta")[:60],
            },
            "items": items,
        }
        school_class.save(update_fields=["visible_menu_items"])
        messages.success(request, "Menüstruktur gespeichert.")
        return redirect("menu-management")
    rows = []
    for index, (key, (label, _url, _icon, default_group)) in enumerate(catalog.items(), 1):
        item = existing.get(key, {})
        rows.append(
            {
                "key": key,
                "label": label,
                "label_override": item.get("label", ""),
                "visible": item.get("visible", True),
                "group": item.get("group", default_group),
                "position": item.get("position", index),
            }
        )
    context = _shared(request, "Menü verwalten", "management")
    context.update({"rows": rows, "stored": stored})
    return render(request, "ui/menu_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def theme_settings(request):
    return redirect(f"{reverse('personal-profile')}?tab=themes")


@login_required
def portal_theme_preview(request, theme_id, page):
    from .theme_policy import available_themes, can_manage_themes as may_manage_themes

    page_labels = {"uebersicht": "Übersicht", "kalender": "Kalender"}
    if page not in page_labels:
        raise Http404
    can_manage_themes = may_manage_themes(request.user)
    if not can_manage_themes:
        _class_or_404(request.user, request)
    themes = available_themes(request.user, include_drafts=True)
    preview_theme = get_object_or_404(themes, pk=theme_id)
    back_to_management = can_manage_themes and request.GET.get("zurueck") == "verwaltung"
    context = _shared(
        request,
        f"{preview_theme.name} · {page_labels[page]}",
        "management" if back_to_management else "more",
    )
    context.update(
        {
            "preview_theme": preview_theme,
            "preview_name": preview_theme.name,
            "preview_description": preview_theme.description,
            "preview_page": page,
            "preview_page_label": page_labels[page],
            "preview_back_url": "/verwaltung/themes/"
            if back_to_management
            else "/einstellungen/design/",
            "preview_back_label": "Zurück zur Verwaltung"
            if back_to_management
            else "Zurück zu deinen Themes",
            "preview_management_query": "?zurueck=verwaltung" if back_to_management else "",
        }
    )
    return render(request, "ui/template_preview.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def theme_management(request):
    if not (
        request.user.is_superuser
        or request.user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    ):
        raise Http404
    if request.method == "POST":
        action = request.POST.get("action", "create")
        if action == "toggle":
            item = get_object_or_404(PortalTheme, pk=request.POST.get("theme_id"))
            item.is_active = not item.is_active
            item.save(update_fields=["is_active", "updated_at"])
            messages.success(
                request, f"„{item.name}“ wurde {'aktiviert' if item.is_active else 'deaktiviert'}."
            )
            return redirect("theme-management")
        if action not in {"create", "update"}:
            raise Http404
        from .theme_views import ThemeForm

        item = get_object_or_404(PortalTheme, pk=request.POST.get("theme_id")) if action == "update" else None
        form = ThemeForm(request.POST, instance=item)
        if not form.is_valid():
            context = _shared(request, "Theme bearbeiten", "management")
            context.update({"theme_form": form, "editing_theme": item})
            return render(request, "ui/theme_form.html", context, status=400)
        item = form.save(commit=False)
        if action == "create":
            base_key = slugify(item.name)[:45] or "theme"
            key = base_key
            suffix = 2
            while PortalTheme.objects.filter(key=key).exists():
                key, suffix = f"{base_key}-{suffix}", suffix + 1
            item.key = key
            item.is_active = False
        item.save()
        messages.success(request, f"„{item.name}“ wurde aktualisiert." if action == "update" else
                         "Das neue Theme wurde als Entwurf angelegt. Prüfe es vor der Freigabe.")
        return redirect("theme-management")
    context = _shared(request, "Themes verwalten", "management")
    context.update(
        {
            "themes": PortalTheme.objects.all(),
            "audiences": PortalTheme.Audience.choices,
        }
    )
    return render(request, "ui/theme_management.html", context)


@login_required
def documents(request):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "pdf_forms", school_class):
        raise Http404
    query = ProtectedDocument.objects.filter(
        school_class=school_class, status=ProtectedDocument.Status.PUBLISHED
    )
    search = request.GET.get("q", "").strip()
    if search:
        query = query.filter(Q(title__icontains=search) | Q(description__icontains=search))
    context = _shared(request, "Dokumente", "more")
    context.update({"documents": query.order_by("category", "-document_date"), "search": search})
    return render(request, "ui/documents.html", context)


@login_required
def posts(request):
    school_class = _class_or_404(request.user, request)
    context = _shared(request, "Aktuelles", "more")
    context["posts"] = Post.objects.filter(
        school_class=school_class, status=Post.Status.PUBLISHED
    ).order_by("-important", "-pinned", "-updated_at")
    return render(request, "ui/posts.html", context)


@login_required
def post_detail(request, post_id):
    school_class = _class_or_404(request.user, request)
    post = get_object_or_404(Post, id=post_id, school_class=school_class, status="published")
    context = _shared(request, post.title, "more")
    context.update({"post": post, "comments": post.comments.select_related("author__person")})
    return render(request, "ui/post_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def events(request):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "events", school_class):
        raise Http404
    if request.method == "POST":
        if not may_create_event(request.user, school_class):
            raise Http404
        event_times = _event_times_from_request(request)
        if not event_times:
            messages.error(request, "Bitte prüfe Beginn und Ende.")
            return redirect("ui-events")
        starts_at, ends_at = event_times
        title = request.POST.get("title", "").strip()[:200]
        if not title:
            messages.error(request, "Bitte gib einen Titel ein.")
            return redirect("ui-events")
        description = request.POST.get("description", "").strip()
        location = request.POST.get("location", "").strip()[:200]
        meeting_url = request.POST.get("meeting_url", "").strip()[:200]
        if not description or not location:
            messages.error(request, "Bitte gib Beschreibung und Ort an.")
            return redirect("ui-events")
        if meeting_url:
            try:
                URLValidator(schemes=["http", "https"])(meeting_url)
            except ValidationError:
                messages.error(request, "Bitte gib einen gültigen Teams-Meeting-Link an.")
                return redirect("ui-events")
        item = Event.objects.create(
            school_class=school_class,
            school_year=school_class.school_year,
            title=title,
            description=description,
            starts_at=starts_at,
            ends_at=ends_at,
            location=location,
            meeting_url=meeting_url,
            change_deadline=ends_at,
            status=Event.Status.PUBLISHED,
        )
        item.organizers.add(request.user)
        ChatRoom.objects.create(
            school_class=school_class,
            school_year=school_class.school_year,
            event=item,
            title=item.title,
            retention_category=ChatRetentionCategory.objects.filter(
                is_active=True,
                intended_for_events=True,
                automatic_deletion_enabled=True,
            )
            .order_by("-retention_days")
            .first(),
        )
        requested_items = (
            _contribution_items_from_request(request)
            if request.POST.get("create_bring_list") == "on"
            else []
        )
        if requested_items:
            category = ContributionCategory.objects.create(
                event=item,
                name=request.POST.get("bring_list_name", "").strip()[:100] or "Mitbringliste",
            )
            ContributionItem.objects.bulk_create(
                [
                    ContributionItem(
                        category=category, label=label, desired_quantity=amount, unit=unit
                    )
                    for label, amount, unit in requested_items
                ]
            )
        messages.success(request, "Die Veranstaltung wurde veröffentlicht.")
        return redirect("ui-event", event_id=item.pk)
    context = _shared(request, "Veranstaltungen", "more")
    context["can_create_event"] = may_create_event(request.user, school_class)
    context["events"] = Event.objects.filter(
        school_class=school_class, status=Event.Status.PUBLISHED
    ).order_by("starts_at")
    return render(request, "ui/events.html", context)


def _event_times_from_request(request):
    try:
        starts_at = timezone.datetime.fromisoformat(request.POST.get("starts_at", ""))
        ends_at = timezone.datetime.fromisoformat(request.POST.get("ends_at", ""))
        if timezone.is_naive(starts_at):
            starts_at = timezone.make_aware(starts_at)
        if timezone.is_naive(ends_at):
            ends_at = timezone.make_aware(ends_at)
        if ends_at <= starts_at:
            raise ValueError
    except (TypeError, ValueError):
        return None
    return starts_at, ends_at


def _owned_event_or_404(request, event_id):
    school_class = _class_or_404(request.user, request)
    item = get_object_or_404(
        Event, id=event_id, school_class=school_class, status=Event.Status.PUBLISHED
    )
    if not may_manage_event(request.user, item):
        raise Http404
    return item


@login_required
@require_POST
def edit_event(request, event_id):
    item = _owned_event_or_404(request, event_id)
    event_times = _event_times_from_request(request)
    title = request.POST.get("title", "").strip()[:200]
    if not event_times or not title:
        return redirect(f"/mehr/veranstaltungen/{item.pk}/?status=edit-invalid")
    starts_at, ends_at = event_times
    item.title = title
    item.description = request.POST.get("description", "").strip()
    item.location = request.POST.get("location", "").strip()[:200]
    item.meeting_url = request.POST.get("meeting_url", "").strip()[:200]
    item.starts_at = starts_at
    item.ends_at = ends_at
    item.change_deadline = ends_at
    try:
        item.full_clean()
    except ValidationError:
        return redirect(f"/mehr/veranstaltungen/{item.pk}/?status=edit-invalid")
    item.save()
    ChatRoom.objects.filter(event=item).update(title=item.title)
    AuditEvent.objects.create(
        actor=request.user,
        action="event.updated",
        target_type="event",
        target_id=str(item.pk),
    )
    return redirect(f"/mehr/veranstaltungen/{item.pk}/?status=updated")


@login_required
@require_POST
def delete_event(request, event_id):
    item = _owned_event_or_404(request, event_id)
    item_id = item.pk
    from .presentation import remove_event_notifications

    with transaction.atomic():
        # A notification must never survive the event it opens, regardless of
        # whether it has already been read by a family member.
        remove_event_notifications(item)
        item.delete()
        AuditEvent.objects.create(
            actor=request.user,
            action="event.deleted",
            target_type="event",
            target_id=str(item_id),
        )
    messages.success(request, "Die Veranstaltung wurde gelöscht.")
    return redirect("ui-events")


@login_required
@require_POST
def set_event_attendance(request, event_id):
    school_class = _class_or_404(request.user, request)
    item = get_object_or_404(
        Event, id=event_id, school_class=school_class, status=Event.Status.PUBLISHED
    )
    participating = request.POST.get("participating") == "yes"
    try:
        _participation, changed = set_event_participation(
            event=item, user=request.user, participating=participating
        )
    except PermissionDenied:
        raise Http404 from None
    status = "participating" if participating else "not-participating"
    return redirect(f"/mehr/veranstaltungen/{item.pk}/?status={status}")


def _contribution_items_from_request(request):
    requested_items = []
    labels = request.POST.getlist("bring_label")
    quantities = request.POST.getlist("bring_quantity")
    units = request.POST.getlist("bring_unit")
    for index, raw_label in enumerate(labels[:30]):
        label = raw_label.strip()[:160]
        if not label:
            continue
        try:
            amount = Decimal(quantities[index] if index < len(quantities) else "1")
            if amount <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            amount = Decimal("1")
        unit = (units[index] if index < len(units) else "Stück").strip()[:40] or "Stück"
        requested_items.append((label, amount, unit))
    return requested_items


@login_required
@require_POST
def create_event_poll(request):
    school_class = _class_or_404(request.user, request)
    if not may_create_event(request.user, school_class):
        raise Http404
    try:
        closes_at = timezone.datetime.fromisoformat(request.POST.get("closes_at", ""))
        if timezone.is_naive(closes_at):
            closes_at = timezone.make_aware(closes_at)
        if closes_at <= timezone.now():
            raise ValueError
        options = []
        for index in range(1, 7):
            raw = request.POST.get(f"option_{index}", "")
            if not raw:
                continue
            starts_at = timezone.datetime.fromisoformat(raw)
            if timezone.is_naive(starts_at):
                starts_at = timezone.make_aware(starts_at)
            options.append(starts_at)
        if len(options) < 2:
            raise ValueError
    except (TypeError, ValueError):
        messages.error(
            request, "Bitte gib mindestens zwei gültige Termine und ein Schlussdatum an."
        )
        return redirect("ui-events")
    poll = EventPoll.objects.create(
        school_class=school_class,
        title=request.POST.get("title", "").strip()[:200],
        description=request.POST.get("description", "").strip(),
        closes_at=closes_at,
        created_by=request.user,
    )
    EventPollOption.objects.bulk_create(
        [
            EventPollOption(poll=poll, starts_at=start, ends_at=start + timedelta(hours=1))
            for start in options
        ]
    )
    return redirect("ui-event-poll", poll_id=poll.id)


@login_required
@require_http_methods(["GET", "POST"])
def event_poll(request, poll_id):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "events", school_class):
        raise Http404
    poll = get_object_or_404(EventPoll, id=poll_id, school_class=school_class)
    options = poll.options.annotate(vote_count=Count("votes")).order_by("starts_at")
    if request.method == "POST" and poll.is_open:
        selected = set(request.POST.getlist("options"))
        EventPollVote.objects.filter(option__poll=poll, user=request.user).exclude(
            option_id__in=selected
        ).delete()
        for option in options.filter(id__in=selected):
            EventPollVote.objects.get_or_create(option=option, user=request.user)
        messages.success(request, "Deine möglichen Termine wurden gespeichert.")
        return redirect("ui-event-poll", poll_id=poll.id)
    context = _shared(request, poll.title, "more")
    context.update(
        {
            "poll": poll,
            "poll_options": options,
            "my_votes": set(
                EventPollVote.objects.filter(option__poll=poll, user=request.user).values_list(
                    "option_id", flat=True
                )
            ),
            "is_organizer": may_create_event(request.user, school_class),
        }
    )
    return render(request, "ui/event_poll.html", context)


@login_required
@require_POST
def finalize_event_poll(request, poll_id):
    school_class = _class_or_404(request.user, request)
    if not may_create_event(request.user, school_class):
        raise Http404
    poll = get_object_or_404(
        EventPoll, id=poll_id, school_class=school_class, finalized_event__isnull=True
    )
    option = get_object_or_404(EventPollOption, id=request.POST.get("option_id"), poll=poll)
    meeting_url = request.POST.get("meeting_url", "").strip()[:200]
    poll.meeting_url = meeting_url
    poll.save(update_fields=["meeting_url"])
    event_item = Event.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        title=poll.title,
        description=poll.description,
        starts_at=option.starts_at,
        ends_at=option.ends_at,
        location=meeting_url or "Wird bekannt gegeben",
        meeting_url=meeting_url,
        change_deadline=option.ends_at,
        status=Event.Status.PUBLISHED,
    )
    event_item.organizers.add(request.user)
    poll.finalized_event = event_item
    poll.save(update_fields=["finalized_event"])
    ChatRoom.objects.create(
        school_class=school_class,
        school_year=school_class.school_year,
        event=event_item,
        title=event_item.title,
        retention_category=ChatRetentionCategory.objects.filter(
            is_active=True,
            intended_for_events=True,
            automatic_deletion_enabled=True,
        )
        .order_by("-retention_days")
        .first(),
    )
    return redirect("ui-event", event_id=event_item.id)


@login_required
def event(request, event_id):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "events", school_class):
        raise Http404
    item = get_object_or_404(Event, id=event_id, school_class=school_class, status="published")
    categories = list(item.categories.prefetch_related("items__reservations__user__person"))
    reservations = Reservation.objects.filter(
        item__category__event=item, user=request.user, status=Reservation.Status.ACTIVE
    )
    food_query = request.GET.get("food_q", "").strip()
    food_results = []
    food_error = ""
    is_organizer = may_manage_event(request.user, item)
    attendee_names = sorted(
        set(item.participations.order_by("family_name").values_list("family_name", flat=True)),
        key=str.casefold,
    )
    contribution_items = []
    contribution_lists = []
    for category in categories:
        category.open_items = []
        category.claimed_items = []
        category_items = list(category.items.all())
        for entry in category_items:
            contribution_items.append(entry)
            entry.active_reservations = [
                reservation
                for reservation in entry.reservations.all()
                if reservation.status == Reservation.Status.ACTIVE
            ]
            for reservation in entry.active_reservations:
                person = reservation.user.person
                child = (
                    person.guardian_relationships.filter(status="verified")
                    .select_related("student_person")
                    .first()
                )
                reservation.display_name = (
                    child.student_person.first_name
                    if person.contribution_name_mode == "child" and child
                    else (person.chat_display_name or person.first_name)
                    if person.contribution_name_mode == "personal"
                    else f"Familie {child.student_person.last_name if child else person.last_name}"
                )
            entry.my_reservation = next(
                (
                    reservation
                    for reservation in entry.active_reservations
                    if reservation.user_id == request.user.id
                ),
                None,
            )
            entry.needs_quantity_choice = entry.desired_quantity > 1
            entry.reserve_quantity_default = min(Decimal("1"), entry.remaining)
            if entry.active_reservations:
                category.claimed_items.append(entry)
            if entry.remaining > 0 and not entry.my_reservation:
                category.open_items.append(entry)
        if category_items:
            contribution_lists.append(category)
    if food_query and is_organizer:
        try:
            food_results = search_food_items(food_query)
        except SpoonacularUnavailable:
            food_error = "Die Lebensmittelsuche ist gerade nicht erreichbar. Du kannst den Eintrag weiterhin frei anlegen."
    context = _shared(request, item.title, "more")
    context.update(
        {
            "event": item,
            "categories": categories,
            "my_reservation_ids": set(reservations.values_list("item_id", flat=True)),
            "my_reservations": reservations,
            "idempotency_key": secrets.token_urlsafe(18),
            "status": request.GET.get("status", ""),
            "is_organizer": is_organizer,
            "edit_mode": request.GET.get("bearbeiten") == "1",
            "is_participating": EventParticipation.objects.filter(event=item, user=request.user).exists(),
            "attendee_names": attendee_names,
            "food_query": food_query,
            "food_results": food_results,
            "food_error": food_error,
            "food_status": request.GET.get("food_status", ""),
            "contribution_items": contribution_items,
            "contribution_lists": contribution_lists,
        }
    )
    return render(request, "ui/event_detail.html", context)


@login_required
@require_POST
def add_contribution_list(request, event_id):
    school_class = _class_or_404(request.user, request)
    item_event = get_object_or_404(
        Event, id=event_id, school_class=school_class, status=Event.Status.PUBLISHED
    )
    if not may_manage_event(request.user, item_event):
        raise Http404
    name = request.POST.get("bring_list_name", "").strip()[:100]
    requested_items = _contribution_items_from_request(request)
    if not name or not requested_items:
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=list-invalid")
    category = ContributionCategory.objects.create(event=item_event, name=name)
    ContributionItem.objects.bulk_create(
        [
            ContributionItem(category=category, label=label, desired_quantity=amount, unit=unit)
            for label, amount, unit in requested_items
        ]
    )
    AuditEvent.objects.create(
        actor=request.user,
        action="event.contribution_list.created",
        target_type="contribution_category",
        target_id=str(category.id),
        metadata={"event_id": item_event.id, "item_count": len(requested_items)},
    )
    return redirect(f"/mehr/veranstaltungen/{event_id}/?status=list-added")


@login_required
@require_POST
def reserve(request, item_id):
    item = get_object_or_404(ContributionItem.objects.select_related("category__event"), id=item_id)
    try:
        reservation, _ = create_reservation(
            item_id=item.id,
            user=request.user,
            quantity=request.POST.get("quantity", "1"),
            note=request.POST.get("note", ""),
            idempotency_key=request.POST.get("idempotency_key", "")[:80],
        )
        # A single requested item is complete as soon as the user takes it.
        if reservation.quantity >= item.desired_quantity:
            reservation.fulfilled_at = timezone.now()
            reservation.save(update_fields=["fulfilled_at"])
    except (ValidationError, PermissionDenied):
        return redirect(f"/mehr/veranstaltungen/{item.category.event_id}/?status=conflict")
    return redirect(f"/mehr/veranstaltungen/{item.category.event_id}/?status=reserved")


@login_required
@require_POST
def free_contribution(request, event_id):
    school_class = _class_or_404(request.user, request)
    item_event = get_object_or_404(Event, id=event_id, school_class=school_class)
    label = request.POST.get("label", "").strip()[:160]
    if not label:
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=invalid")
    try:
        quantity = Decimal(request.POST.get("quantity", "1"))
        if quantity <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=invalid")
    category, _ = ContributionCategory.objects.get_or_create(
        event=item_event, name="Eigene Beiträge"
    )
    item = ContributionItem.objects.create(
        category=category,
        label=label,
        desired_quantity=quantity,
        unit=request.POST.get("unit", "Stück")[:40],
        is_free_entry=True,
        moderated=False,
    )
    request.POST = request.POST.copy()
    request.POST["quantity"] = str(quantity)
    request.POST["idempotency_key"] = request.POST.get("idempotency_key") or secrets.token_urlsafe(
        18
    )
    return reserve(request, item.id)


@login_required
@require_POST
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    event_id = reservation.item.category.event_id
    try:
        cancel_reservation_for_user(reservation, request.user)
    except (ValidationError, PermissionDenied):
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=cancel-failed")
    return redirect(f"/mehr/veranstaltungen/{event_id}/?status=cancelled")


@login_required
@require_POST
def fulfill_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation.objects.select_related("item__category__event"),
        id=reservation_id,
        status=Reservation.Status.ACTIVE,
    )
    event_item = reservation.item.category.event
    if (
        reservation.user_id != request.user.id
        and not may_manage_event(request.user, event_item)
    ):
        raise Http404
    reservation.fulfilled_at = timezone.now() if not reservation.fulfilled_at else None
    reservation.save(update_fields=["fulfilled_at"])
    return redirect("ui-event", event_id=event_item.id)


@login_required
def teachers(request):
    school_class = _class_or_404(request.user, request)
    context = _shared(request, "Lehrkräfte", "more")
    context["teachers"] = TeacherProfile.objects.filter(school_class=school_class).select_related(
        "person"
    )
    return render(request, "ui/teachers.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def galleries(request):
    school_class = _class_or_404(request.user, request)
    if not may_access_module(request.user, "gallery", school_class):
        raise Http404
    can_create = may_create_gallery(request.user, school_class)
    if request.method == "POST":
        if not can_create:
            raise Http404
        title = request.POST.get("title", "").strip()[:200]
        event_category = request.POST.get("event_category", Gallery.EventCategory.OTHER)
        if event_category not in Gallery.EventCategory.values:
            event_category = Gallery.EventCategory.OTHER
        if not title:
            messages.error(request, "Bitte gib der Galerie einen Namen.")
        else:
            gallery = Gallery.objects.create(
                school_class=school_class,
                school_year=school_class.school_year,
                title=title,
                description=request.POST.get("description", "").strip(),
                event_category=event_category,
                status=Gallery.Status.PUBLISHED,
                upload_allowed=True,
                moderation_required=True,
                created_by=request.user,
                published_at=timezone.now(),
            )
            messages.success(request, f"Galerie „{gallery.title}“ wurde angelegt.")
            return redirect("gallery-detail", gallery_id=gallery.id)
    visible = [
        gallery
        for gallery in Gallery.objects.filter(school_class=school_class).order_by("-created_at")
        if may_access_gallery(request.user, gallery) or may_manage_gallery(request.user, gallery)
    ]
    context = _shared(request, "Fotos", "more")
    context.update(
        {
            "galleries": visible,
            "can_create": can_create,
            "gallery_event_categories": Gallery.EventCategory.choices,
        }
    )
    return render(request, "ui/galleries.html", context)


def _active_student_membership(student):
    today = timezone.localdate()
    return (
        ClassMembership.objects.filter(
            person=student,
            status="active",
            valid_from__lte=today,
        )
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=today))
        .select_related("school_class", "school_class__school")
        .order_by("school_class__school_year__starts_on", "id")
        .last()
    )


def _school_modules_for_student(student):
    membership = _active_student_membership(student)
    if membership is None:
        return membership, PortalAdapterModule.objects.none()
    class_links = PortalAdapterModule.available_to_classes.through.objects.filter(
        portaladaptermodule_id=OuterRef("pk")
    )
    modules = (
        PortalAdapterModule.objects.filter(
            adapter__is_enabled=True,
            adapter__school=membership.school_class.school,
            is_enabled=True,
        )
        .filter(Q(available_to_classes=membership.school_class) | ~Exists(class_links))
        .select_related("adapter")
        .distinct()
        .order_by("label")
    )
    return membership, modules


def _module_connection_url(module, student):
    """Keep provider names out of the parent-facing family area."""

    if module.adapter.provider == PortalAdapter.Provider.WEBUNTIS:
        return f"{reverse('webuntis-connection')}?student={student.pk}"
    if module.adapter.provider == PortalAdapter.Provider.ITSLEARNING:
        return reverse("itslearning-portal")
    if module.adapter.base_url:
        return module.adapter.base_url
    return ""


@login_required
@require_http_methods(["GET", "POST"])
def family(request):
    school_class = _class_or_404(request.user, request)
    from .avatar_designer import avatar_designer_context
    from .family_settings import (
        available_classes,
        person_card,
        request_child,
        save_consent,
        save_consents,
        save_person,
    )
    from .models import ChildJoinRequest
    from .onboarding import active_decision, may_decide, record_decision

    relationships = list(
        GuardianChildRelationship.objects.filter(guardian_person=request.user.person)
        .select_related("student_person")
        .order_by("student_person__first_name", "student_person__last_name")
    )
    photo_households = Household.objects.filter(members=request.user.person).distinct()
    active_tab = request.GET.get("tab", "overview")
    if active_tab not in {"overview", "data", "privacy", "modules", "add-child"}:
        active_tab = "overview"
    requested_child = request.GET.get("child", "")
    active_relationship = next(
        (item for item in relationships if str(item.pk) == requested_child and item.is_current()),
        relationships[0] if relationships else None,
    )
    form_error = ""
    bound_person_id = ""
    bound_form_data = None
    if request.method == "POST" and request.POST.get("action") in {
        "profile",
        "consent",
        "consents",
        "add_child",
        "invite_adult",
        "family_photo",
        "schoolmanager_credentials",
    }:
        try:
            action = request.POST["action"]
            if action == "add_child":
                request_child(request)
                messages.success(request, "Die Zuordnung wurde zur Prüfung eingereicht.")
            elif action == "invite_adult":
                relationship = next(
                    (
                        item
                        for item in relationships
                        if str(item.pk) == request.POST.get("relationship_id")
                        and item.is_current()
                        and item.may_manage_profile
                    ),
                    None,
                )
                if relationship is None:
                    raise PermissionDenied
                first_name = request.POST.get("first_name", "").strip()[:100]
                last_name = request.POST.get("last_name", "").strip()[:100]
                email = normalize_email_address(request.POST.get("email", ""))
                if not first_name or not last_name:
                    raise ValidationError("Bitte gib Vor- und Nachnamen ein.")
                if UserAccount.objects.filter(email__iexact=email).exists():
                    raise ValidationError(
                        "Für diese E-Mail-Adresse besteht bereits ein KlassID-Zugang."
                    )
                households = Household.objects.filter(members=request.user.person).filter(
                    members=relationship.student_person
                )
                household = households.first()
                if household is None:
                    raise ValidationError(
                        "Für dieses Kind besteht noch keine gemeinsame Familienzuordnung."
                    )
                if Invitation.objects.filter(
                    email__iexact=email,
                    household=household,
                    school_class=school_class,
                    used_at__isnull=True,
                    expires_at__gt=timezone.now(),
                ).exists():
                    raise ValidationError(
                        "Für diese E-Mail-Adresse wurde bereits ein gültiger Bestätigungslink gesendet."
                    )
                with transaction.atomic():
                    invitation, token = Invitation.issue(
                        email,
                        request.user,
                        first_name=first_name,
                        last_name=last_name,
                        school_class=school_class,
                        household=household,
                    )
                    link = f"{settings.WAGTAILADMIN_BASE_URL.rstrip('/')}/invitation/{token}/"
                    sent = send_mail(
                        "Dein persönlicher KlassID-Familienzugang",
                        (
                            "Du wurdest als zweite erwachsene Person zu einer KlassID-Familie "
                            f"eingeladen. Lege über diesen einmaligen Link innerhalb von 7 Tagen "
                            f"dein eigenes Passwort fest: {link}"
                        ),
                        settings.DEFAULT_FROM_EMAIL,
                        [invitation.email],
                        fail_silently=False,
                    )
                    if sent != 1:
                        raise ValidationError(
                            "Der Bestätigungslink konnte nicht versendet werden. Bitte versuche es später erneut."
                        )
                    AuditEvent.objects.create(
                        actor=request.user,
                        action="family.adult_invited",
                        target_type="invitation",
                        target_id=str(invitation.pk),
                    )
                messages.success(request, "Der Bestätigungslink wurde versendet.")
            elif action == "family_photo":
                household = get_object_or_404(photo_households, pk=request.POST.get("household_id"))
                from .family_photos import remove_family_photo, save_family_photo

                photo = FamilyPhoto.objects.filter(
                    household=household, school_class=school_class
                ).first()
                if request.POST.get("remove") == "yes":
                    if not photo:
                        raise ValidationError("Für diese Familie ist kein Bild hinterlegt.")
                    remove_family_photo(user=request.user, photo=photo)
                    messages.success(request, "Das Familienbild wurde entfernt.")
                else:
                    save_family_photo(
                        user=request.user,
                        household=household,
                        school_class=school_class,
                        upload=request.FILES.get("family_photo"),
                        subject_ids=request.POST.getlist("subject_ids"),
                    )
                    messages.success(request, "Das Familienbild wurde gespeichert.")
            elif action == "schoolmanager_credentials":
                relation = next((r for r in relationships if str(r.pk) == request.POST.get("relationship_id")), None)
                if not relation or not relation.is_current() or not relation.may_manage_profile:
                    raise PermissionDenied
                username = request.POST.get("username", "").strip()
                password = request.POST.get("password", "")
                if not username or not password:
                    raise ValidationError("Benutzername und Passwort sind erforderlich.")
                SchoolmanagerConnection.objects.update_or_create(
                    user=request.user,
                    student=relation.student_person,
                    defaults={"username_encrypted": encrypt_schoolmanager(username), "password_encrypted": encrypt_schoolmanager(password)},
                )
                messages.success(request, "Schulmanager-Zugang wurde verschlüsselt gespeichert.")
            else:
                person_id = request.POST.get("person_id")
                person = request.user.person if person_id == str(request.user.person.pk) else None
                if person is None:
                    relation = next(
                        (
                            r
                            for r in relationships
                            if str(r.student_person_id) == person_id
                            and r.is_current()
                            and (action in {"consent", "consents"} or r.may_manage_profile)
                        ),
                        None,
                    )
                    if not relation:
                        raise PermissionDenied
                    person = relation.student_person
                if action == "profile":
                    save_person(request, person)
                    if person.pk != request.user.person.pk:
                        school_class = (
                            available_classes().filter(pk=request.POST.get("school_class")).first()
                        )
                        if school_class is None:
                            raise ValidationError("Bitte eine Schule und Klasse auswählen.")
                        today = timezone.localdate()
                        ClassMembership.objects.filter(person=person, status="active").exclude(
                            school_class=school_class
                        ).update(status="ended", valid_until=today)
                        ClassMembership.objects.update_or_create(
                            person=person,
                            school_class=school_class,
                            defaults={"status": "active", "valid_from": today, "valid_until": None},
                        )
                elif action == "consents":
                    save_consents(request, person)
                else:
                    save_consent(request, person)
                messages.success(request, "Die Änderungen wurden gespeichert.")
        except ValidationError as error:
            form_error = " ".join(error.messages)
            bound_person_id = request.POST.get("person_id", "")
            bound_form_data = request.POST
            active_tab = request.POST.get("tab", active_tab)
            requested_child = request.POST.get("child", "")
            active_relationship = next(
                (
                    item
                    for item in relationships
                    if str(item.pk) == requested_child and item.is_current()
                ),
                active_relationship,
            )
        else:
            tab = request.POST.get("tab", "overview")
            child = request.POST.get("child", "")
            suffix = f"?tab={tab}" + (f"&child={child}" if child else "")
            return redirect(f"{reverse('ui-family')}{suffix}")
    if request.method == "POST" and request.POST.get("relationship_id") and request.POST.get("module_id"):
        relationship = get_object_or_404(
            GuardianChildRelationship,
            pk=request.POST.get("relationship_id"),
            guardian_person=request.user.person,
        )
        if not relationship.is_current() or not relationship.may_manage_profile:
            raise PermissionDenied
        _membership, allowed_modules = _school_modules_for_student(relationship.student_person)
        module = get_object_or_404(allowed_modules, pk=request.POST.get("module_id"))
        enabled = request.POST.get("enabled") == "on"
        state = ChildModuleConnection.ConnectionState.NOT_CONNECTED
        if enabled and module.requires_child_credentials:
            state = ChildModuleConnection.ConnectionState.CREDENTIALS_NEEDED
        elif enabled and module.adapter.base_url:
            state = ChildModuleConnection.ConnectionState.EXTERNAL
        elif enabled:
            state = ChildModuleConnection.ConnectionState.CONNECTED
        connection, _created = ChildModuleConnection.objects.update_or_create(
            student=relationship.student_person,
            module=module,
            defaults={
                "is_enabled": enabled,
                "connection_state": state,
                "configured_by": request.user,
            },
        )
        if module.adapter.provider == PortalAdapter.Provider.WEBUNTIS:
            consent_type = ConsentType.objects.filter(key=f"webuntis_{module.key}").first()
            if consent_type and may_decide(request.user, relationship.student_person, consent_type):
                record_decision(
                    user=request.user,
                    subject=relationship.student_person,
                    key=consent_type.key,
                    decision=(
                        ConsentDecision.Decision.GRANTED
                        if enabled
                        else ConsentDecision.Decision.DENIED
                    ),
                    source="family-module",
                )
        AuditEvent.objects.create(
            actor=request.user,
            action="family.module_connection.changed",
            target_type="child_module_connection",
            target_id=str(connection.pk),
            metadata={"module_id": module.pk, "enabled": enabled, "state": state},
        )
        messages.success(
            request,
            f"{module.label} wurde {'für dieses Kind aktiviert' if enabled else 'für dieses Kind ausgeschaltet'}.",
        )
        return redirect(f"{reverse('ui-family')}?tab=modules&child={relationship.pk}")

    module_connections = {
        (item.student_id, item.module_id): item
        for item in ChildModuleConnection.objects.filter(
            student__in=[relationship.student_person for relationship in relationships]
        )
    }
    webuntis_connections = {
        item.student_id: item
        for item in WebUntisConnection.objects.filter(
            user=request.user,
            student__in=[relationship.student_person for relationship in relationships],
        )
    }
    relationship_rows = []
    for relationship in relationships:
        membership, modules = _school_modules_for_student(relationship.student_person)
        module_rows = []
        adapter_rows = {}
        for module in modules:
            connection = module_connections.get((relationship.student_person_id, module.pk))
            module_row = {
                "module": module,
                "connection": connection,
                "connection_url": _module_connection_url(module, relationship.student_person),
                "school_consent_enabled": bool(
                    (consent_type := ConsentType.objects.filter(key=f"webuntis_{module.key}").first())
                    and may_decide(request.user, relationship.student_person, consent_type)
                    and (
                        active_decision(consent_type, relationship.student_person, request.user.person)
                        and active_decision(consent_type, relationship.student_person, request.user.person).decision
                        == ConsentDecision.Decision.GRANTED
                    )
                )
                if module.adapter.provider == PortalAdapter.Provider.WEBUNTIS
                else True,
            }
            module_rows.append(module_row)
            adapter_row = adapter_rows.setdefault(
                module.adapter_id,
                {
                    "adapter": module.adapter,
                    "modules": [],
                    "connection_url": module_row["connection_url"],
                    "requires_child_credentials": False,
                    "has_enabled_connection": False,
                    "credential_connection": None,
                },
            )
            adapter_row["modules"].append(module_row)
            adapter_row["requires_child_credentials"] = (
                adapter_row["requires_child_credentials"]
                or module.requires_child_credentials
            )
            adapter_row["has_enabled_connection"] = (
                adapter_row["has_enabled_connection"]
                or bool(connection and connection.is_enabled)
            )
            if module.adapter.provider == PortalAdapter.Provider.WEBUNTIS:
                adapter_row["credential_connection"] = webuntis_connections.get(
                    relationship.student_person_id
                )
        relationship_rows.append(
            {
                "relationship": relationship,
                "membership": membership,
                "modules": module_rows,
                "adapters": list(adapter_rows.values()),
                "school_classes": available_classes(),
                "card": person_card(
                    relationship.student_person,
                    request.user,
                    relationship.is_current() and relationship.may_manage_profile,
                    data=(
                        bound_form_data
                        if str(relationship.student_person_id) == bound_person_id
                        else None
                    ),
                ),
            }
        )
    context = _shared(request, "Familien-Zentrale", "more")
    context["relationship_rows"] = relationship_rows
    context["active_tab"] = active_tab
    context["active_relationship"] = active_relationship
    context["active_row"] = next(
        (
            row
            for row in relationship_rows
            if active_relationship and row["relationship"].pk == active_relationship.pk
        ),
        None,
    )
    child_ids = [
        r.student_person_id for r in relationships if r.is_current() and r.may_view_student_profile
    ]
    other_parents = GuardianChildRelationship.objects.filter(
        student_person_id__in=child_ids
    ).select_related("guardian_person")
    parent_map = {request.user.person.pk: request.user.person}
    for relation in other_parents:
        if relation.is_current():
            parent_map[relation.guardian_person_id] = relation.guardian_person
    context["parent_cards"] = [
        person_card(
            p,
            request.user,
            p.pk == request.user.person.pk,
            data=bound_form_data if str(p.pk) == bound_person_id else None,
        )
        for p in parent_map.values()
    ]
    context["join_requests"] = ChildJoinRequest.objects.filter(
        guardian=request.user.person
    ).select_related("school_class__school")
    context["available_classes"] = available_classes()
    context["avatar_designer"] = avatar_designer_context()
    context["family_form_error"] = form_error
    from .family_photos import family_photo_is_visible, family_photo_people, may_manage_family_photo

    photo_consent = ConsentType.objects.filter(key="photo_gallery").first()
    context["family_photo_rows"] = []
    for household in photo_households.prefetch_related("members", "photos__subjects"):
        if not may_manage_family_photo(request.user, household, school_class):
            continue
        photo = next(
            (item for item in household.photos.all() if item.school_class_id == school_class.pk), None
        )
        people = list(family_photo_people(household, school_class))
        context["family_photo_rows"].append(
            {
                "household": household,
                "stored_photo": photo,
                "photo": photo if photo and family_photo_is_visible(photo) else None,
                "people": [
                    {
                        "person": person,
                        "photo_allowed": bool(
                            photo_consent and consent_state(photo_consent, person) == "allowed"
                        ),
                    }
                    for person in people
                ],
                "may_upload": bool(
                    photo_consent
                    and any(consent_state(photo_consent, person) == "allowed" for person in people)
                ),
            }
        )
    # Keep overview, child details and add-child in one shell so the same
    # context switcher and navigation are used throughout the family flow.
    return render(request, "ui/family.html", context)


@login_required
def contacts(request):
    school_class = _class_or_404(request.user, request)
    today = timezone.localdate()
    relationships = list(
        GuardianChildRelationship.objects.filter(
            status="verified",
            verified_at__isnull=False,
            may_view_student_profile=True,
            valid_from__lte=today,
            student_person__classmembership__school_class=school_class,
            student_person__classmembership__status="active",
            student_person__classmembership__valid_from__lte=today,
            guardian_person__user__isnull=False,
        )
        .filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=today),
            Q(student_person__classmembership__valid_until__isnull=True)
            | Q(student_person__classmembership__valid_until__gte=today),
        )
        .select_related("guardian_person__user", "student_person__user")
    )
    guardians = {
        relationship.guardian_person_id: relationship.guardian_person
        for relationship in relationships
    }
    children_by_guardian = {}
    for relationship in relationships:
        children_by_guardian.setdefault(relationship.guardian_person_id, []).append(
            relationship.student_person
        )

    from klasse5e.chat.services import may_start_direct_conversation

    from .family_photos import family_photo_is_visible

    def normalized_family_name(value):
        name = " ".join((value or "").split())
        if name.casefold().startswith("familie "):
            return name[8:].strip()
        return name

    def family_initials(value):
        words = normalized_family_name(value).split()
        return "".join(word[0] for word in words[:2]).upper() or "?"

    def shared_address(person):
        fields = ("street", "postal_code", "city")
        if not all(person.field_visibility.get(field, True) for field in fields):
            return ""
        return " · ".join(
            part for part in (person.street, " ".join((person.postal_code, person.city)).strip()) if part
        )

    def contact_person(person, role):
        email = ""
        if person.email_visibility == "members":
            email = person.contact_email or (person.user.email if person.user_id else "")
        phone = person.phone if person.phone_visibility == "members" else ""
        return {
            "person": person,
            "role": role,
            "email": email,
            "phone": phone,
            "phone_display": format_phone_number(phone),
            "address": shared_address(person),
            "may_message": may_start_direct_conversation(request.user, person, school_class),
            "is_self": person.user_id == request.user.pk,
        }

    rows = []
    assigned_guardians = set()
    households = (
        Household.objects.filter(members__in=guardians)
        .prefetch_related("members__user", "photos__subjects")
        .distinct()
    )
    for household in households:
        adults = [member for member in household.members.all() if member.pk in guardians]
        if not adults:
            continue
        assigned_guardians.update(person.pk for person in adults)
        children = []
        for adult in adults:
            children.extend(children_by_guardian.get(adult.pk, []))
        children = list({child.pk: child for child in children}.values())
        children.sort(key=lambda child: (child.last_name.casefold(), child.first_name.casefold()))
        adults.sort(key=lambda person: (person.last_name.casefold(), person.first_name.casefold()))
        family_name = normalized_family_name(household.label) or (
            children[0].last_name if children else adults[0].last_name
        )
        family_photo = next(
            (item for item in household.photos.all() if item.school_class_id == school_class.pk), None
        )
        people = [contact_person(person, "Erwachsene Person") for person in adults]
        people.extend(contact_person(person, "Kind") for person in children)
        emails = [item["email"] for item in people if item["email"]]
        phones = [item["phone"] for item in people if item["phone"]]
        phone_displays = [item["phone_display"] for item in people if item["phone_display"]]
        addresses = [item["address"] for item in people if item["address"]]
        rows.append(
            {
                "family_name": family_name,
                "family_initials": family_initials(family_name),
                "family_photo": family_photo if family_photo and family_photo_is_visible(family_photo) else None,
                "adults": adults,
                "children": children,
                "people": people,
                "emails": list(dict.fromkeys(emails)),
                "phones": list(dict.fromkeys(phones)),
                "phone_displays": list(dict.fromkeys(phone_displays)),
                "addresses": list(dict.fromkeys(addresses)),
            }
        )
    for guardian_id, guardian in guardians.items():
        if guardian_id in assigned_guardians:
            continue
        children = children_by_guardian.get(guardian_id, [])
        children.sort(key=lambda child: (child.last_name.casefold(), child.first_name.casefold()))
        people = [contact_person(guardian, "Erwachsene Person")]
        people.extend(contact_person(person, "Kind") for person in children)
        rows.append(
            {
                "family_name": guardian.last_name,
                "family_initials": family_initials(guardian.last_name),
                "family_photo": None,
                "adults": [guardian],
                "children": children,
                "people": people,
                "emails": [item["email"] for item in people if item["email"]],
                "phones": [item["phone"] for item in people if item["phone"]],
                "phone_displays": [
                    item["phone_display"] for item in people if item["phone_display"]
                ],
                "addresses": [item["address"] for item in people if item["address"]],
            }
        )
    rows.sort(
        key=lambda row: (row["family_name"].casefold(), row["adults"][0].first_name.casefold())
    )
    context = _shared(request, "Adressliste", "contacts")
    context["contacts"] = rows
    return render(request, "ui/contacts.html", context)


@login_required
def students(request):
    school_class = _class_or_404(request.user, request)
    students = (
        Person.objects.filter(
            studentprofile__isnull=False,
            classmembership__school_class=school_class,
            classmembership__status="active",
        )
        .distinct()
        .order_by("last_name", "first_name")
    )
    context = _shared(request, "Schülerübersicht", "contacts")
    context["students"] = students
    return render(request, "ui/students.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def consents(request):
    # The old global school-data switchboard is intentionally no longer a
    # second editing surface. School-data choices are managed with the child
    # module toggles in the family centre; keep this route as a compatibility
    # redirect for bookmarks and old onboarding links.
    return redirect(f"{reverse('ui-family')}?tab=overview")


@login_required
def notifications(request):
    _class_or_404(request.user, request)
    context = _shared(request, "Benachrichtigungen", "more")
    context["push_active"] = PushSubscription.objects.filter(
        user=request.user, enabled=True
    ).exists()
    context["push_subscriptions"] = PushSubscription.objects.filter(user=request.user, enabled=True)
    context["vapid_configured"] = bool(settings.VAPID_PUBLIC_KEY)
    context["mention_push_enabled"] = PushPreference.objects.filter(
        user=request.user, key="push_chat_mentions", enabled=True
    ).exists()
    return render(request, "ui/notifications.html", context)


@login_required
@require_POST
def notification_preference(request):
    key = request.POST.get("key")
    if key != "push_chat_mentions":
        raise Http404
    PushPreference.objects.update_or_create(
        user=request.user, key=key, defaults={"enabled": request.POST.get("enabled") == "on"}
    )
    messages.success(request, "Push-Einstellung gespeichert.")
    return redirect("ui-notifications")


@login_required
def demo_states(request):
    if not active_roles(request.user) & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN}:
        raise Http404
    context = _shared(request, "UI-Zustände", "more")
    return render(request, "ui/demo_states.html", context)


@login_required
def system_status(request):
    if not active_roles(request.user) & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN}:
        raise Http404
    from django.db import connection

    database_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        database_ok = False
    spaces = list(WebDavSpace.objects.select_related("student__person"))
    context = _shared(request, "Systemstatus", "more")
    context.update(
        {
            "database_ok": database_ok,
            "spaces": [{"space": space, "used": used_bytes(space)} for space in spaces],
            "connections": ItslearningConnection.objects.select_related("student__person"),
            "portal_modules": PortalModule.objects.order_by("label"),
        }
    )
    return render(request, "ui/system_status.html", context)
