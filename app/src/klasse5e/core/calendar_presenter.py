from collections import defaultdict
from datetime import datetime, timedelta

from django.utils import timezone

from klasse5e.events.models import Event
from klasse5e.itslearning.models import ItslearningCalendarItem
from klasse5e.schedule.models import CalendarEntry, TimetableEntry
from klasse5e.webuntis.models import WebUntisHomework, WebUntisLesson


def _item(kind, label, title, *, starts_at=None, meta="", url=""):
    local_start = timezone.localtime(starts_at) if starts_at else None
    return {
        "kind": kind,
        "kind_label": label,
        "title": title,
        "time": local_start.strftime("%H:%M") if local_start else "",
        "sort": local_start.strftime("%H:%M") if local_start else "23:59",
        "meta": meta,
        "url": url,
    }


def build_calendar_context(
    *,
    school_class,
    selected_day,
    webuntis_connections,
    itslearning_connections,
):
    month_start = selected_day.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    grid_start = month_start - timedelta(days=month_start.weekday())
    grid_end = grid_start + timedelta(days=42)
    items = defaultdict(list)

    lessons = list(
        WebUntisLesson.objects.filter(
            connection__in=webuntis_connections,
            starts_at__date__gte=grid_start,
            starts_at__date__lt=grid_end,
        ).order_by("starts_at")
    )
    personal_days = {timezone.localtime(lesson.starts_at).date() for lesson in lessons}
    for lesson in lessons:
        starts_at = timezone.localtime(lesson.starts_at)
        meta = " - ".join(
            value
            for value in (
                f"bei {lesson.teacher_label}" if lesson.teacher_label else "",
                f"Raum {lesson.room}" if lesson.room else "",
            )
            if value
        )
        items[starts_at.date()].append(
            _item(
                "lesson",
                "Unterricht",
                lesson.subject or "Unterricht",
                starts_at=lesson.starts_at,
                meta=meta,
            )
        )

    manual_lessons = list(TimetableEntry.objects.filter(school_class=school_class))
    for offset in range(42):
        day = grid_start + timedelta(days=offset)
        if day in personal_days or day.isoweekday() > 5:
            continue
        for lesson in manual_lessons:
            if lesson.weekday != day.isoweekday():
                continue
            starts_at = timezone.make_aware(
                datetime.combine(day, lesson.starts_at),
                timezone.get_current_timezone(),
            )
            meta = " - ".join(
                value
                for value in (
                    f"bei {lesson.teacher_label}" if lesson.teacher_label else "",
                    f"Raum {lesson.room}" if lesson.room else "",
                )
                if value
            )
            items[day].append(
                _item(
                    "lesson",
                    "Unterricht",
                    lesson.subject,
                    starts_at=starts_at,
                    meta=meta,
                )
            )

    for homework in WebUntisHomework.objects.filter(
        connection__in=webuntis_connections,
        due_on__gte=grid_start,
        due_on__lt=grid_end,
    ).order_by("due_on"):
        items[homework.due_on].append(
            _item(
                "homework",
                "Hausaufgabe",
                homework.subject or "Hausaufgabe",
                meta=homework.text,
            )
        )

    for entry in CalendarEntry.objects.filter(
        school_class=school_class,
        starts_at__date__gte=grid_start,
        starts_at__date__lt=grid_end,
    ).order_by("starts_at"):
        day = timezone.localtime(entry.starts_at).date()
        items[day].append(
            _item(
                "appointment",
                entry.get_kind_display(),
                entry.title,
                starts_at=entry.starts_at,
                meta=entry.room or entry.details,
            )
        )

    for entry in ItslearningCalendarItem.objects.filter(
        connection__in=itslearning_connections,
        starts_at__date__gte=grid_start,
        starts_at__date__lt=grid_end,
    ).order_by("starts_at"):
        day = timezone.localtime(entry.starts_at).date()
        items[day].append(
            _item(
                "learning",
                "Lernplattform",
                entry.title,
                starts_at=entry.starts_at,
                meta=entry.description,
                url=entry.url,
            )
        )

    for event in Event.objects.filter(
        school_class=school_class,
        status=Event.Status.PUBLISHED,
        starts_at__date__gte=grid_start,
        starts_at__date__lt=grid_end,
    ).order_by("starts_at"):
        day = timezone.localtime(event.starts_at).date()
        items[day].append(
            _item(
                "appointment",
                "Veranstaltung",
                event.title,
                starts_at=event.starts_at,
                meta=event.location,
                url=f"/mehr/veranstaltungen/{event.pk}/",
            )
        )

    days = []
    for offset in range(42):
        day = grid_start + timedelta(days=offset)
        day_items = sorted(items[day], key=lambda value: (value["sort"], value["title"]))
        days.append(
            {
                "date": day,
                "in_month": day.month == month_start.month,
                "selected": day == selected_day,
                "today": day == timezone.localdate(),
                "items": day_items,
            }
        )

    return {
        "selected_day": selected_day,
        "month_start": month_start,
        "previous_month": previous_month,
        "next_month": next_month,
        "calendar_days": days,
        "agenda": sorted(items[selected_day], key=lambda value: (value["sort"], value["title"])),
    }
