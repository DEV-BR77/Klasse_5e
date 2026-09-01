import secrets
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from klasse5e.chat.models import ChatReadState, ChatRoom
from klasse5e.content.models import Post, ProtectedDocument, TeacherProfile
from klasse5e.events.models import ContributionCategory, ContributionItem, Event, Reservation
from klasse5e.events.services import cancel_reservation_for_user, create_reservation
from klasse5e.itslearning.models import (
    ItslearningCalendarItem,
    ItslearningConnection,
    ItslearningUpdate,
    WebDavSpace,
)
from klasse5e.itslearning.webdav import used_bytes
from klasse5e.media.models import Gallery
from klasse5e.media.policies import may_access_gallery
from klasse5e.schedule.models import CalendarEntry, TimetableEntry

from .models import (
    ClassMembership,
    ConsentDecision,
    GuardianChildRelationship,
    PushSubscription,
    Role,
)
from .policies import active_roles, family_label, has_active_membership


def _membership(user):
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


def _class_or_404(user):
    membership = _membership(user)
    if not membership:
        raise Http404
    return membership.school_class


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
    school_class = _membership(request.user)
    return {
        "page_title": title,
        "active_section": section,
        "membership": school_class,
        "roles": active_roles(request.user, school_class.school_class if school_class else None),
        "family_name": family_label(request.user),
    }


def _itslearning_connections(user):
    student_ids = GuardianChildRelationship.objects.filter(
        guardian_person=user.person,
        status="verified",
        verified_at__isnull=False,
        may_view_student_profile=True,
    ).values("student_person__studentprofile")
    return ItslearningConnection.objects.filter(owner=user, student_id__in=student_ids, active=True)


@login_required
def dashboard(request):
    school_class = _class_or_404(request.user)
    day = _day_from_request(request)
    context = _shared(request, "Start", "start")
    portal_connections = _itslearning_connections(request.user)
    context.update(
        {
            "selected_day": day,
            "lessons": TimetableEntry.objects.filter(
                school_class=school_class, weekday=day.isoweekday()
            ),
            "calendar_entries": CalendarEntry.objects.filter(
                school_class=school_class, starts_at__date=day
            ).order_by("starts_at")[:5],
            "events": Event.objects.filter(
                school_class=school_class,
                status=Event.Status.PUBLISHED,
                ends_at__gte=timezone.now(),
            ).order_by("starts_at")[:2],
            "posts": Post.objects.filter(
                school_class=school_class, status=Post.Status.PUBLISHED
            ).order_by("-important", "-pinned", "-updated_at")[:3],
            "documents": ProtectedDocument.objects.filter(
                school_class=school_class, status=ProtectedDocument.Status.PUBLISHED
            ).order_by("-is_updated", "-created_at")[:2],
            "chat_unread": _unread_count(request.user, school_class),
            "itslearning_entries": ItslearningCalendarItem.objects.filter(
                connection__in=portal_connections, starts_at__date=day
            ).order_by("starts_at")[:5],
            "itslearning_updates": ItslearningUpdate.objects.filter(
                course__connection__in=portal_connections
            ).select_related("course")[:3],
        }
    )
    return render(request, "ui/dashboard_v2.html", context)


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
    school_class = _class_or_404(request.user)
    day = _day_from_request(request)
    week_start = day - timedelta(days=day.weekday())
    context = _shared(request, "Kalender", "calendar")
    portal_connections = _itslearning_connections(request.user)
    context.update(
        {
            "selected_day": day,
            "previous_day": day - timedelta(days=1),
            "next_day": day + timedelta(days=1),
            "lessons": TimetableEntry.objects.filter(
                school_class=school_class, weekday=day.isoweekday()
            ),
            "day_entries": CalendarEntry.objects.filter(
                school_class=school_class, starts_at__date=day
            ).order_by("starts_at"),
            "week_days": [week_start + timedelta(days=index) for index in range(5)],
            "week_entries": CalendarEntry.objects.filter(
                school_class=school_class,
                starts_at__date__gte=week_start,
                starts_at__date__lt=week_start + timedelta(days=7),
            ),
            "itslearning_entries": ItslearningCalendarItem.objects.filter(
                connection__in=portal_connections, starts_at__date=day
            ).order_by("starts_at"),
        }
    )
    return render(request, "ui/calendar_v2.html", context)


@login_required
def chat_overview(request):
    school_class = _class_or_404(request.user)
    rooms = ChatRoom.objects.filter(school_class=school_class).order_by("event_id", "title")
    context = _shared(request, "Chat", "chat")
    context["rooms"] = rooms
    return render(request, "ui/chat_overview.html", context)


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, public_id=room_id)
    if not has_active_membership(request.user, room.school_class):
        raise Http404
    context = _shared(request, room.title, "chat")
    context.update(
        {
            "room": room,
            "messages": room.messages.select_related("author__person", "reply_to").order_by(
                "created_at"
            )[:200],
        }
    )
    return render(request, "ui/chat_room.html", context)


@login_required
def more(request):
    context = _shared(request, "Mehr", "more")
    return render(request, "ui/more.html", context)


@login_required
def documents(request):
    school_class = _class_or_404(request.user)
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
    school_class = _class_or_404(request.user)
    context = _shared(request, "Aktuelles", "more")
    context["posts"] = Post.objects.filter(
        school_class=school_class, status=Post.Status.PUBLISHED
    ).order_by("-important", "-pinned", "-updated_at")
    return render(request, "ui/posts.html", context)


@login_required
def post_detail(request, post_id):
    school_class = _class_or_404(request.user)
    post = get_object_or_404(Post, id=post_id, school_class=school_class, status="published")
    context = _shared(request, post.title, "more")
    context.update({"post": post, "comments": post.comments.select_related("author__person")})
    return render(request, "ui/post_detail.html", context)


@login_required
def events(request):
    school_class = _class_or_404(request.user)
    context = _shared(request, "Veranstaltungen", "more")
    context["events"] = Event.objects.filter(
        school_class=school_class, status=Event.Status.PUBLISHED
    ).order_by("starts_at")
    return render(request, "ui/events.html", context)


@login_required
def event(request, event_id):
    school_class = _class_or_404(request.user)
    item = get_object_or_404(Event, id=event_id, school_class=school_class, status="published")
    categories = item.categories.prefetch_related("items__reservations")
    reservations = Reservation.objects.filter(
        item__category__event=item, user=request.user, status=Reservation.Status.ACTIVE
    )
    context = _shared(request, item.title, "more")
    context.update(
        {
            "event": item,
            "categories": categories,
            "my_reservation_ids": set(reservations.values_list("item_id", flat=True)),
            "my_reservations": reservations,
            "idempotency_key": secrets.token_urlsafe(18),
            "status": request.GET.get("status", ""),
        }
    )
    return render(request, "ui/event_detail.html", context)


@login_required
@require_POST
def reserve(request, item_id):
    item = get_object_or_404(ContributionItem.objects.select_related("category__event"), id=item_id)
    try:
        create_reservation(
            item_id=item.id,
            user=request.user,
            quantity=request.POST.get("quantity", "1"),
            note=request.POST.get("note", ""),
            idempotency_key=request.POST.get("idempotency_key", "")[:80],
        )
    except (ValidationError, PermissionDenied):
        return redirect(f"/mehr/veranstaltungen/{item.category.event_id}/?status=conflict")
    return redirect(f"/mehr/veranstaltungen/{item.category.event_id}/?status=reserved")


@login_required
@require_POST
def free_contribution(request, event_id):
    school_class = _class_or_404(request.user)
    item_event = get_object_or_404(Event, id=event_id, school_class=school_class)
    if timezone.now() > item_event.change_deadline:
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=deadline")
    label = request.POST.get("label", "").strip()[:160]
    if not label:
        return redirect(f"/mehr/veranstaltungen/{event_id}/?status=invalid")
    category, _ = ContributionCategory.objects.get_or_create(
        event=item_event, name="Eigene Beiträge"
    )
    item = ContributionItem.objects.create(
        category=category,
        label=label,
        desired_quantity=1,
        unit=request.POST.get("unit", "Stück")[:40],
        is_free_entry=True,
        moderated=False,
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
def teachers(request):
    school_class = _class_or_404(request.user)
    context = _shared(request, "Lehrkräfte", "more")
    context["teachers"] = TeacherProfile.objects.filter(school_class=school_class).select_related(
        "person"
    )
    return render(request, "ui/teachers.html", context)


@login_required
def galleries(request):
    school_class = _class_or_404(request.user)
    visible = [
        gallery
        for gallery in Gallery.objects.filter(school_class=school_class).order_by("-created_at")
        if may_access_gallery(request.user, gallery)
    ]
    context = _shared(request, "Fotos", "more")
    context["galleries"] = visible
    return render(request, "ui/galleries.html", context)


@login_required
def family(request):
    _class_or_404(request.user)
    relationships = GuardianChildRelationship.objects.filter(
        guardian_person=request.user.person
    ).select_related("student_person")
    context = _shared(request, "Familie & Profile", "more")
    context["relationships"] = relationships
    return render(request, "ui/family.html", context)


@login_required
def consents(request):
    _class_or_404(request.user)
    context = _shared(request, "Einwilligungen", "more")
    context["decisions"] = ConsentDecision.objects.filter(
        deciding_person=request.user.person
    ).select_related("consent_type", "subject_person", "text_version")
    return render(request, "ui/consents_v2.html", context)


@login_required
def notifications(request):
    _class_or_404(request.user)
    context = _shared(request, "Benachrichtigungen", "more")
    context["push_active"] = PushSubscription.objects.filter(
        user=request.user, enabled=True
    ).exists()
    return render(request, "ui/notifications.html", context)


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
        }
    )
    return render(request, "ui/system_status.html", context)
