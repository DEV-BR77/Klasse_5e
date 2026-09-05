import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.base import ContentFile
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import content_disposition_header
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods, require_POST

from klasse5e.chat.models import ChatReadState, ChatRetentionCategory, ChatRoom
from klasse5e.content.models import Post, ProtectedDocument, TeacherProfile
from klasse5e.events.models import (
    ContributionCategory,
    ContributionItem,
    Event,
    EventPoll,
    EventPollOption,
    EventPollVote,
    Reservation,
)
from klasse5e.events.services import cancel_reservation_for_user, create_reservation
from klasse5e.events.spoonacular import SpoonacularUnavailable, search_food_items
from klasse5e.itslearning.models import (
    ItslearningCalendarItem,
    ItslearningConnection,
    ItslearningUpdate,
    WebDavSpace,
)
from klasse5e.itslearning.webdav import used_bytes
from klasse5e.meals.models import MealDay, MealPlan
from klasse5e.media.models import Gallery
from klasse5e.media.policies import may_access_gallery, may_manage_gallery
from klasse5e.portal_adapters.catalog import (
    ADAPTER_CATALOG,
    provider_definition,
    seed_default_modules,
)
from klasse5e.portal_adapters.models import PortalAdapter, PortalAdapterModule
from klasse5e.schedule.models import CalendarEntry, TimetableEntry
from klasse5e.webuntis.models import (
    HomeworkProgress,
    WebUntisConnection,
    WebUntisHomework,
    WebUntisLesson,
)

from .calendar_presenter import build_calendar_context
from .family_context import active_child_context
from .family_handouts import create_family_handout
from .models import (
    AuditEvent,
    ClassMembership,
    ConsentDecision,
    ConsentType,
    GuardianChildRelationship,
    Person,
    PilotReport,
    PortalModule,
    PortalTheme,
    PushPreference,
    PushSubscription,
    RegistrationApplication,
    Role,
    School,
    SchoolClass,
    StudentProfile,
    UserNotification,
)
from .policies import active_roles, family_label, has_active_membership
from .registration import sanitized_profile_photo

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
        school_class = SchoolClass.objects.filter(status="active").order_by("id").first()
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


def _shared(request, title, section):
    school_class = _membership(request.user, request)
    return {
        "page_title": title,
        "active_section": section,
        "membership": school_class,
        "roles": active_roles(request.user, school_class.school_class if school_class else None),
        "family_name": family_label(request.user),
    }


def _connections_for_active_child(connections, child):
    """Keep personal school data in the child area, never mixed by accident."""

    return connections.filter(student_id=child.student.id) if child else connections.none()


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
def select_active_child(request, student_id=None):
    """Persist the selected child in the browser session after access validation."""

    children, _selected = active_child_context(request)
    if student_id is None:
        request.session.pop("active_child_person_id", None)
    elif any(item.student.id == student_id for item in children):
        request.session["active_child_person_id"] = student_id
    else:
        raise Http404
    target = request.GET.get("next", "")
    if not target.startswith("/") or target.startswith("//"):
        target = "/"
    return redirect(target)


def _itslearning_connections(user):
    student_ids = GuardianChildRelationship.objects.filter(
        guardian_person=user.person,
        status="verified",
        verified_at__isnull=False,
        may_view_student_profile=True,
    ).values("student_person__studentprofile")
    return ItslearningConnection.objects.filter(owner=user, student_id__in=student_ids, active=True)


def _webuntis_connections(user):
    if not hasattr(user, "person"):
        return WebUntisConnection.objects.none()
    student_ids = GuardianChildRelationship.objects.filter(
        guardian_person=user.person,
        status="verified",
        verified_at__isnull=False,
        may_view_student_profile=True,
    ).values("student_person")
    return WebUntisConnection.objects.filter(user=user, student_id__in=student_ids)


@login_required
def dashboard(request):
    family_children, active_child = active_child_context(request)
    dashboard_child = active_child or (family_children[0] if family_children else None)
    school_class = dashboard_child.school_class if dashboard_child else None
    if school_class is None and not family_children:
        school_class = _class_or_404(request.user, request)
    # The due scheduler is deliberately request-assisted: after a login the first
    # dashboard request claims at most one due schedule transactionally. This keeps
    # homework current without requiring a separate worker or a hidden manual click.
    try:
        from klasse5e.webuntis.scheduler import run_due_schedules

        run_due_schedules()
    except Exception:
        # A school provider outage must not make the portal or login unavailable.
        pass
    try:
        from django.core.cache import cache

        from klasse5e.chat.retention import cleanup_expired_messages

        if cache.add("chat-retention-cleanup", True, 6 * 60 * 60):
            cleanup_expired_messages()
    except Exception:
        pass
    try:
        from django.core.cache import cache

        from klasse5e.meals.source import sync_plans

        if (
            settings.MEAL_PLAN_SYNC_ENABLED
            and not settings.DEBUG
            and cache.add("meal-plan-sync", True, 12 * 60 * 60)
        ):
            sync_plans()
    except Exception:
        pass
    day = _day_from_request(request)
    meal_reference_day = day
    if day == timezone.localdate() and timezone.localtime().hour >= 15:
        meal_reference_day += timedelta(days=1)
    next_meal = (
        MealDay.objects.filter(
            plan__status=MealPlan.Status.READY,
            date__gte=meal_reference_day,
        )
        .select_related("plan")
        .prefetch_related("options")
        .order_by("date")
        .first()
    )
    context = _shared(request, "Start", "start")
    portal_connections = _connections_for_active_child(
        _itslearning_connections(request.user), dashboard_child
    )
    webuntis_connections = _connections_for_active_child(
        _webuntis_connections(request.user), dashboard_child
    )
    webuntis_last_sync = (
        webuntis_connections.order_by("-last_successful_sync_at")
        .values_list("last_successful_sync_at", flat=True)
        .first()
    )
    personal_lessons = _merge_adjacent_lessons(
        list(
            WebUntisLesson.objects.filter(connection__in=webuntis_connections, starts_at__date=day)
            .exclude(status="cancelled")
            .order_by("starts_at")
        )
    )
    manual_lessons = (
        TimetableEntry.objects.filter(school_class=school_class, weekday=day.isoweekday())
        if school_class
        else TimetableEntry.objects.none()
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
    homework.sort(key=lambda item: (item.is_completed, item.due_on, item.subject.casefold()))
    homework = homework[:5]
    context.update(
        {
            "app_version": settings.APP_VERSION,
            "release_channel": settings.APP_RELEASE_CHANNEL,
            "selected_day": day,
            "dashboard_week": [
                {"date": day + timedelta(days=offset), "selected": offset == 0}
                for offset in range(7)
            ],
            "webuntis_last_sync": webuntis_last_sync,
            "lessons": personal_lessons if personal_lessons else manual_lessons,
            "homework": homework,
            "family_children": family_children,
            "active_child": active_child,
            "calendar_entries": (
                CalendarEntry.objects.filter(school_class=school_class, starts_at__date=day)
                .order_by("starts_at")[:5]
                if school_class
                else CalendarEntry.objects.none()
            ),
            "events": (
                Event.objects.filter(
                    school_class=school_class,
                    status=Event.Status.PUBLISHED,
                    ends_at__gte=timezone.now(),
                ).order_by("starts_at")[:2]
                if school_class
                else Event.objects.none()
            ),
            "next_meal": next_meal,
            "posts": (
                Post.objects.filter(school_class=school_class, status=Post.Status.PUBLISHED)
                .order_by("-important", "-pinned", "-updated_at")[:3]
                if school_class
                else Post.objects.none()
            ),
            "documents": (
                ProtectedDocument.objects.filter(
                    school_class=school_class, status=ProtectedDocument.Status.PUBLISHED
                ).order_by("-is_updated", "-created_at")[:2]
                if school_class
                else ProtectedDocument.objects.none()
            ),
            "chat_unread": _unread_count(request.user, school_class),
            "notification_counts": {
                row["category"]: row["total"]
                for row in UserNotification.objects.filter(
                    user=request.user,
                    school_class=school_class,
                    read_at__isnull=True,
                )
                .values("category")
                .annotate(total=Count("id"))
            },
            "itslearning_entries": ItslearningCalendarItem.objects.filter(
                connection__in=portal_connections, starts_at__date=day
            ).order_by("starts_at")[:5],
            "itslearning_updates": ItslearningUpdate.objects.filter(
                course__connection__in=portal_connections
            ).select_related("course")[:3],
        }
    )
    return render(request, "ui/dashboard_v2.html", context)


@login_required
@require_POST
def homework_progress(request, homework_id):
    homework = get_object_or_404(
        WebUntisHomework.objects.select_related("connection__student"),
        id=homework_id,
        connection__in=_webuntis_connections(request.user),
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
    total = 0
    for room in ChatRoom.objects.filter(school_class=school_class):
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
    day = _day_from_request(request)
    view = request.GET.get("ansicht", "week")
    categories = request.GET.getlist("kategorie") if "filter" in request.GET else None
    context = _shared(request, "Kalender", "calendar")
    context.update(
        build_calendar_context(
            school_class=school_class,
            selected_day=day,
            webuntis_connections=_connections_for_active_child(
                _webuntis_connections(request.user), calendar_child
            ),
            itslearning_connections=_connections_for_active_child(
                _itslearning_connections(request.user), calendar_child
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
        _connections_for_active_child(_webuntis_connections(request.user), calendar_child)
        .order_by("-last_successful_sync_at")
        .values_list("last_successful_sync_at", flat=True)
        .first()
    )
    return render(request, "ui/calendar_v2.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def chat_overview(request):
    school_class = _class_or_404(request.user, request)
    if request.method == "POST":
        _require_portal_admin(request.user)
        title = request.POST.get("title", "").strip()[:120]
        if title:
            retention = ChatRetentionCategory.objects.filter(
                pk=request.POST.get("retention_category"), is_active=True, intended_for_events=False
            ).first()
            ChatRoom.objects.create(
                school_class=school_class,
                school_year=school_class.school_year,
                title=title,
                is_open=True,
                retention_category=retention
                or ChatRetentionCategory.objects.filter(is_active=True, intended_for_events=False)
                .order_by("retention_days")
                .first(),
            )
            messages.success(request, "Der Chatraum wurde angelegt.")
        return redirect("ui-chat")
    rooms = ChatRoom.objects.filter(school_class=school_class).order_by("event_id", "title")
    room_rows = []
    for room in rooms:
        state = ChatReadState.objects.filter(room=room, user=request.user).first()
        unread = room.messages.exclude(author=request.user)
        if state:
            unread = unread.filter(created_at__gt=state.last_read_at)
        room_rows.append(
            {
                "room": room,
                "unread": unread.count(),
                "last_message": room.messages.select_related("author__person")
                .order_by("-created_at")
                .first(),
            }
        )
    context = _shared(request, "Chat", "chat")
    context["room_rows"] = room_rows
    context["retention_categories"] = ChatRetentionCategory.objects.filter(
        is_active=True, intended_for_events=False
    )
    return render(request, "ui/chat_overview.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, public_id=room_id)
    if not has_active_membership(request.user, room.school_class):
        raise Http404
    if request.method == "POST":
        from klasse5e.chat.services import create_message

        create_message(
            room, request.user, request.POST.get("body", ""), None, request.FILES.get("attachment")
        )
        return redirect("ui-chat-room", room_id=room.public_id)
    ChatReadState.objects.update_or_create(
        room=room, user=request.user, defaults={"last_read_at": timezone.now()}
    )
    context = _shared(request, room.title, "chat")
    context.update(
        {
            "room": room,
            "chat_messages": room.messages.select_related("author__person", "reply_to").order_by(
                "created_at"
            )[:200],
            "emojis": "😀 😄 😂 😊 😍 🥳 😎 🤔 👍 👏 🙌 💪 ❤️ 🎉 🚲 ⚽ 📚 ✏️".split(),
            "mention_names": [
                display or first
                for display, first in Person.objects.filter(
                    classmembership__school_class=room.school_class,
                    classmembership__status="active",
                    user__isnull=False,
                )
                .exclude(user=request.user)
                .values_list("chat_display_name", "first_name")
                .distinct()
            ],
        }
    )
    return render(request, "ui/chat_room.html", context)


@login_required
def chat_attachment(request, message_id):
    from klasse5e.chat.models import ChatMessage

    message = get_object_or_404(ChatMessage.objects.select_related("room"), public_id=message_id)
    if not has_active_membership(request.user, message.room.school_class) or not message.attachment:
        raise Http404
    if (
        message.attachment_content_type.startswith("image/")
        and message.attachment_safety_status != "approved"
    ):
        raise Http404
    response = FileResponse(
        message.attachment.open("rb"),
        content_type=message.attachment_content_type or "application/octet-stream",
    )
    disposition = (
        "inline"
        if message.attachment_content_type.startswith(("image/", "audio/"))
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
    context = _shared(request, "Verwaltung", "management")
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
def portal_adapter_management(request):
    """Configure reviewed portal connectors without collecting credentials here."""
    _require_portal_admin(request.user)
    schools = _manageable_schools(request.user)
    if request.method == "POST":
        provider = request.POST.get("provider", "")
        if provider not in ADAPTER_CATALOG:
            messages.error(request, "Bitte wähle einen bekannten Adapter aus.")
            return redirect("portal-adapter-management")
        school = get_object_or_404(schools, pk=request.POST.get("school_id"))
        definition = provider_definition(provider)
        name = request.POST.get("name", "").strip()[:120] or definition["label"]
        adapter, created = PortalAdapter.objects.get_or_create(
            school=school,
            provider=provider,
            name=name,
            defaults={"base_url": definition["default_url"]},
        )
        if created:
            seed_default_modules(adapter)
            AuditEvent.objects.create(
                actor=request.user,
                action="portal_adapter.created",
                target_type="portal_adapter",
                target_id=str(adapter.pk),
                metadata={"provider": provider, "school_id": school.pk},
            )
            messages.success(request, f"{definition['label']} wurde für {school} angelegt.")
        else:
            messages.info(request, "Dieser Adapter ist für die Schule bereits vorhanden.")
        return redirect("portal-adapter-detail", adapter_id=adapter.pk)
    adapters = PortalAdapter.objects.filter(school__in=schools).select_related("school").prefetch_related(
        "modules"
    )
    context = _shared(request, "Schulportal-Adapter", "management")
    context.update({"schools": schools, "adapters": adapters, "adapter_catalog": ADAPTER_CATALOG.items()})
    return render(request, "ui/portal_adapter_management.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def portal_adapter_detail(request, adapter_id):
    _require_portal_admin(request.user)
    schools = _manageable_schools(request.user)
    adapter = get_object_or_404(
        PortalAdapter.objects.select_related("school").prefetch_related("modules"),
        pk=adapter_id,
        school__in=schools,
    )
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_adapter":
            adapter.base_url = request.POST.get("base_url", "").strip()[:200]
            adapter.project_identifier = request.POST.get("project_identifier", "").strip()[:120]
            adapter.institution_identifier = request.POST.get("institution_identifier", "").strip()[:120]
            adapter.school_number = request.POST.get("school_number", "").strip()[:40]
            adapter.configuration_note = request.POST.get("configuration_note", "").strip()[:1200]
            adapter.is_enabled = request.POST.get("is_enabled") == "on"
            try:
                adapter.full_clean()
            except ValidationError:
                messages.error(request, "Bitte prüfe die Adresse des Adapters.")
            else:
                adapter.save()
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
                module.configuration_note = request.POST.get("configuration_note", "").strip()[:1200]
                if module.is_enabled and module.status == PortalAdapterModule.Status.NOT_CONFIGURED:
                    module.status = PortalAdapterModule.Status.READY
            module.save()
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
    context.update({"adapter": adapter, "provider_definition": provider_definition(adapter.provider)})
    return render(request, "ui/portal_adapter_detail.html", context)


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
def presentation(request):
    _class_or_404(request.user, request)
    return render(
        request,
        "ui/presentation.html",
        _shared(request, "KlassID kennenlernen", "more"),
    )


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
    context = _shared(request, "Mehr", "more")
    school_class = _class_or_404(request.user, request)
    catalog = _menu_catalog()
    stored = (
        school_class.visible_menu_items if isinstance(school_class.visible_menu_items, dict) else {}
    )
    configured = stored.get("items") or [
        {"key": key, "group": item[3]} for key, item in catalog.items()
    ]
    labels = {"class": "Klassenleben", "communication": "Kommunikation", "account": "Mein Konto"}
    labels.update(stored.get("group_labels") or {})
    groups = []
    for group_key in ("class", "communication", "account"):
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
                "key": "management",
                "label": "Portalverwaltung",
                "items": [
                    {
                        "key": "management_overview",
                        "label": "Verwaltungsübersicht",
                        "url": "/verwaltung/",
                        "icon": "home",
                    },
                    {
                        "key": "schools",
                        "label": "Schulen verwalten",
                        "url": "/admin/core/school/",
                        "icon": "teacher",
                    },
                    {
                        "key": "classes",
                        "label": "Klassen verwalten",
                        "url": "/admin/core/schoolclass/",
                        "icon": "people",
                    },
                    {
                        "key": "family_invitations",
                        "label": "QR-Familieneinladungen",
                        "url": "/verwaltung/familien-einladungen/",
                        "icon": "document",
                    },
                    {
                        "key": "registrations",
                        "label": "Neue Registrierungen",
                        "url": "/admin/core/registrationapplication/",
                        "icon": "consent",
                    },
                ],
            }
        )
    context["menu_groups"] = groups
    return render(request, "ui/more.html", context)


def _menu_catalog():
    return {
        "events": ("Veranstaltungen & Mitbringen", "/mehr/veranstaltungen/", "event", "class"),
        "mobility": ("Wir fahren zusammen", "/mehr/mobilitaet/", "people", "class"),
        "news": ("Aktuelles", "/mehr/aktuelles/", "news", "class"),
        "gallery": ("Fotos & Galerie", "/mehr/fotos/", "photo", "class"),
        "meals": ("Speiseplan", "/mehr/speiseplan/", "event", "class"),
        "school_data": ("Kalender-Synchronisation", "/mehr/webuntis/", "calendar", "communication"),
        "profile": ("Meine Daten", "/einstellungen/profil/", "people", "account"),
        "family": ("Familie & Kinder", "/mehr/familie/", "people", "account"),
        "themes": ("Design & Themes", "/einstellungen/design/", "consent", "account"),
        "consents": ("Datenschutz & Einwilligungen", "/mehr/einwilligungen/", "consent", "account"),
        "notifications": (
            "Benachrichtigungen & App",
            "/mehr/benachrichtigungen/",
            "bell",
            "account",
        ),
        "security": ("Zwei-Faktor-Anmeldung", "/accounts/2fa/", "consent", "account"),
        "tutorial": ("Einführung", "/tutorial/", "home", "account"),
        "delete_account": (
            "Konto und Daten löschen",
            "/einstellungen/konto-loeschen/",
            "consent",
            "account",
        ),
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
            if group not in {"class", "communication", "account"}:
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
    _class_or_404(request.user, request)
    audience = (
        PortalTheme.Audience.CHILDREN
        if hasattr(request.user, "person")
        and StudentProfile.objects.filter(person=request.user.person).exists()
        else PortalTheme.Audience.ADULTS
    )
    themes = PortalTheme.objects.filter(is_active=True).filter(
        Q(audience=PortalTheme.Audience.ALL) | Q(audience=audience)
    )
    if request.method == "POST":
        selected = get_object_or_404(themes, pk=request.POST.get("theme_id"))
        request.user.selected_theme = selected
        request.user.save(update_fields=["selected_theme"])
        messages.success(request, f"Theme „{selected.name}“ ist jetzt aktiv.")
        return redirect("theme-settings")
    context = _shared(request, "Design & Themes", "more")
    context.update({"themes": themes, "audience": audience})
    return render(request, "ui/theme_settings.html", context)


@login_required
def portal_theme_preview(request, theme_id, page):
    page_labels = {"uebersicht": "Übersicht", "kalender": "Kalender"}
    if page not in page_labels:
        raise Http404
    can_manage_themes = request.user.is_superuser or request.user.roleassignment_set.filter(
        active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
    ).exists()
    if can_manage_themes:
        themes = PortalTheme.objects.all()
    else:
        _class_or_404(request.user, request)
        audience = (
            PortalTheme.Audience.CHILDREN
            if hasattr(request.user, "person")
            and StudentProfile.objects.filter(person=request.user.person).exists()
            else PortalTheme.Audience.ADULTS
        )
        themes = PortalTheme.objects.filter(is_active=True).filter(
            Q(audience=PortalTheme.Audience.ALL) | Q(audience=audience)
        )
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
        import re

        colors = {
            field: request.POST.get(field, "").strip().upper()
            for field in (
                "primary",
                "primary_dark",
                "primary_light",
                "accent",
                "background",
                "surface",
                "text",
                "text_muted",
            )
        }
        if not all(re.fullmatch(r"#[0-9A-F]{6}", value) for value in colors.values()):
            messages.error(request, "Bitte für jede Farbe einen vollständigen HEX-Wert angeben.")
        else:
            base_key = slugify(request.POST.get("name", ""))[:45] or "theme"
            key = base_key
            suffix = 2
            while PortalTheme.objects.filter(key=key).exists():
                key, suffix = f"{base_key}-{suffix}", suffix + 1
            try:
                shadow_strength = min(
                    30, max(0, int(request.POST.get("shadow_strength", "10") or 10))
                )
            except ValueError:
                shadow_strength = 10
            PortalTheme.objects.create(
                key=key,
                name=request.POST.get("name", "Neues Theme").strip()[:80],
                description=request.POST.get("description", "").strip()[:180],
                audience=request.POST.get("audience")
                if request.POST.get("audience") in PortalTheme.Audience.values
                else PortalTheme.Audience.ALL,
                is_dark=request.POST.get("is_dark") == "on",
                radius=request.POST.get("radius")
                if request.POST.get("radius") in {".7rem", "1rem", "1.35rem", "1.7rem"}
                else "1rem",
                shadow_strength=shadow_strength,
                **colors,
            )
            messages.success(request, "Das neue Theme ist sofort zur Auswahl verfügbar.")
            return redirect("theme-management")
    context = _shared(request, "Themes verwalten", "management")
    context.update(
        {
            "themes": PortalTheme.objects.all(),
            "audiences": PortalTheme.Audience.choices,
            "template_catalog": TEMPLATE_PREVIEW_CATALOG,
        }
    )
    return render(request, "ui/theme_management.html", context)


@login_required
def template_preview(request, template_key, page):
    if not (
        request.user.is_superuser
        or request.user.roleassignment_set.filter(
            active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
        ).exists()
    ):
        raise Http404
    page_labels = {"uebersicht": "Übersicht", "kalender": "Kalender"}
    if page not in page_labels:
        raise Http404
    catalog_item = next(
        (item for item in TEMPLATE_PREVIEW_CATALOG if item["key"] == template_key), None
    )
    if catalog_item is None:
        raise Http404
    context = _shared(
        request,
        f"{catalog_item['name']} · {page_labels[page]}",
        "management",
    )
    context.update(
        {
            "catalog_item": catalog_item,
            "preview_name": catalog_item["name"],
            "preview_description": catalog_item["style_note"],
            "preview_page": page,
            "preview_page_label": page_labels[page],
            "preview_back_url": "/verwaltung/themes/",
            "preview_back_label": "Zurück zu allen Vorlagen",
        }
    )
    return render(request, "ui/template_preview.html", context)


@login_required
def documents(request):
    school_class = _class_or_404(request.user, request)
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
    if request.method == "POST":
        _require_portal_admin(request.user)
        try:
            starts_at = timezone.datetime.fromisoformat(request.POST.get("starts_at", ""))
            ends_at = timezone.datetime.fromisoformat(request.POST.get("ends_at", ""))
            if timezone.is_naive(starts_at):
                starts_at = timezone.make_aware(starts_at)
                ends_at = timezone.make_aware(ends_at)
            if ends_at <= starts_at:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Bitte prüfe Beginn und Ende.")
            return redirect("ui-events")
        item = Event.objects.create(
            school_class=school_class,
            school_year=school_class.school_year,
            title=request.POST.get("title", "").strip()[:200],
            description=request.POST.get("description", "").strip(),
            starts_at=starts_at,
            ends_at=ends_at,
            location=request.POST.get("location", "").strip()[:200],
            change_deadline=starts_at,
            status=Event.Status.PUBLISHED,
        )
        item.organizers.add(request.user)
        ChatRoom.objects.create(
            school_class=school_class,
            school_year=school_class.school_year,
            event=item,
            title=item.title,
            retention_category=ChatRetentionCategory.objects.filter(
                is_active=True, intended_for_events=True
            )
            .order_by("-retention_days")
            .first(),
        )
        requested_items = []
        for line in request.POST.get("bring_items", "").splitlines()[:30]:
            parts = [part.strip() for part in line.split("|")]
            if not parts[0]:
                continue
            try:
                amount = Decimal(parts[1]) if len(parts) > 1 else Decimal("1")
                if amount <= 0:
                    raise ValueError
            except (InvalidOperation, ValueError):
                amount = Decimal("1")
            requested_items.append(
                (parts[0][:160], amount, (parts[2] if len(parts) > 2 else "Stück")[:40])
            )
        if requested_items:
            category = ContributionCategory.objects.create(event=item, name="Mitbringliste")
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
    context["events"] = Event.objects.filter(
        school_class=school_class, status=Event.Status.PUBLISHED
    ).order_by("starts_at")
    context["event_polls"] = (
        EventPoll.objects.filter(school_class=school_class, finalized_event__isnull=True)
        .prefetch_related("options__votes")
        .order_by("closes_at")
    )
    return render(request, "ui/events.html", context)


@login_required
@require_POST
def create_event_poll(request):
    school_class = _class_or_404(request.user, request)
    _require_portal_admin(request.user)
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
            "is_organizer": poll.created_by_id == request.user.id or request.user.is_superuser,
        }
    )
    return render(request, "ui/event_poll.html", context)


@login_required
@require_POST
def finalize_event_poll(request, poll_id):
    school_class = _class_or_404(request.user, request)
    _require_portal_admin(request.user)
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
        change_deadline=option.starts_at,
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
            is_active=True, intended_for_events=True
        )
        .order_by("-retention_days")
        .first(),
    )
    return redirect("ui-event", event_id=event_item.id)


@login_required
def event(request, event_id):
    school_class = _class_or_404(request.user, request)
    item = get_object_or_404(Event, id=event_id, school_class=school_class, status="published")
    categories = item.categories.prefetch_related("items__reservations__user__person")
    reservations = Reservation.objects.filter(
        item__category__event=item, user=request.user, status=Reservation.Status.ACTIVE
    )
    food_query = request.GET.get("food_q", "").strip()
    food_results = []
    food_error = ""
    is_organizer = item.organizers.filter(id=request.user.id).exists()
    contribution_items = [entry for category in categories for entry in category.items.all()]
    for entry in contribution_items:
        entry.active_reservations = [
            reservation
            for reservation in entry.reservations.all()
            if reservation.status == "active"
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
            (reservation for reservation in entry.active_reservations if reservation.user_id == request.user.id),
            None,
        )
        entry.needs_quantity_choice = entry.desired_quantity > 1
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
            "food_query": food_query,
            "food_results": food_results,
            "food_error": food_error,
            "food_status": request.GET.get("food_status", ""),
            "contribution_items": contribution_items,
        }
    )
    return render(request, "ui/event_detail.html", context)


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
    if timezone.now() > item_event.change_deadline:
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=deadline")
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
        and not event_item.organizers.filter(id=request.user.id).exists()
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
    roles = active_roles(request.user, school_class)
    can_create = bool(
        request.user.is_superuser
        or roles & {Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN, Role.CLASS_ADMIN, Role.EDITOR}
    )
    if request.method == "POST":
        if not can_create:
            raise Http404
        title = request.POST.get("title", "").strip()[:200]
        if not title:
            messages.error(request, "Bitte gib der Galerie einen Namen.")
        else:
            gallery = Gallery.objects.create(
                school_class=school_class,
                school_year=school_class.school_year,
                title=title,
                description=request.POST.get("description", "").strip(),
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
    context.update({"galleries": visible, "can_create": can_create})
    return render(request, "ui/galleries.html", context)


@login_required
def family(request):
    _class_or_404(request.user, request)
    relationships = GuardianChildRelationship.objects.filter(
        guardian_person=request.user.person
    ).select_related("student_person")
    context = _shared(request, "Familie & Profile", "more")
    context["relationships"] = relationships
    return render(request, "ui/family.html", context)


@login_required
def contacts(request):
    school_class = _class_or_404(request.user, request)
    memberships = ClassMembership.objects.filter(
        school_class=school_class, status="active", person__user__isnull=False
    ).select_related("person__user")
    rows = []
    for membership in memberships:
        person = membership.person
        children = GuardianChildRelationship.objects.filter(
            guardian_person=person,
            status="verified",
            student_person__classmembership__school_class=school_class,
            student_person__classmembership__status="active",
        ).select_related("student_person")
        rows.append(
            {
                "person": person,
                "children": [relationship.student_person for relationship in children],
                "email": person.user.email if person.email_visibility == "members" else "",
                "phone": person.phone if person.phone_visibility == "members" else "",
            }
        )
    context = _shared(request, "Kontakte", "contacts")
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
    _class_or_404(request.user, request)
    from klasse5e.webuntis.services import eligible_students

    from .onboarding import active_decision, may_decide, record_decision

    feature_options = (
        ("timetable", "Stundenplan", "Unterricht und Zeiten im persönlichen Überblick."),
        ("substitutions", "Vertretungen", "Ausfälle und Änderungen am Unterricht."),
        ("absences", "Abwesenheiten", "Persönliche Fehlzeiten und Statusmeldungen."),
        ("homework", "Hausaufgaben", "Aufgaben, Fälligkeiten und Fachzuordnung."),
        ("exams", "Prüfungen", "Angekündigte Arbeiten und Prüfungstermine."),
    )
    subjects = list(eligible_students(request.user).order_by("first_name", "last_name"))
    option_keys = {key for key, _label, _description in feature_options}
    if request.method == "POST":
        try:
            subject = next(item for item in subjects if str(item.pk) == request.POST.get("subject"))
        except StopIteration:
            raise PermissionDenied from None
        feature = request.POST.get("feature", "")
        if feature not in option_keys:
            raise Http404
        decision = (
            ConsentDecision.Decision.GRANTED
            if request.POST.get("enabled") == "on"
            else ConsentDecision.Decision.DENIED
        )
        record_decision(
            user=request.user,
            subject=subject,
            key=f"webuntis_{feature}",
            decision=decision,
            source="settings",
        )
        messages.success(
            request,
            f"{dict((key, label) for key, label, _description in feature_options)[feature]} wurde {'aktiviert' if decision == ConsentDecision.Decision.GRANTED else 'ausgeschaltet'}.",
        )
        return redirect("ui-consents")

    rows = []
    for subject in subjects:
        options = []
        for feature, label, description in feature_options:
            consent_type = ConsentType.objects.filter(key=f"webuntis_{feature}").first()
            decision = (
                active_decision(consent_type, subject, request.user.person)
                if consent_type
                else None
            )
            options.append(
                {
                    "key": feature,
                    "label": label,
                    "description": description,
                    "allowed": bool(
                        consent_type and may_decide(request.user, subject, consent_type)
                    ),
                    "enabled": bool(
                        decision and decision.decision == ConsentDecision.Decision.GRANTED
                    ),
                }
            )
        rows.append({"student": subject, "options": options})
    context = _shared(request, "Synchronisation", "more")
    context["sync_rows"] = rows
    return render(request, "ui/consents_v2.html", context)


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
