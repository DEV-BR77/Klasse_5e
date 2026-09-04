from collections import defaultdict
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from klasse5e.events.models import Event
from klasse5e.itslearning.models import ItslearningCalendarItem
from klasse5e.schedule.models import CalendarEntry, TimeGrid, TimetableEntry
from klasse5e.webuntis.models import WebUntisHomework, WebUntisLesson

CALENDAR_CATEGORIES = (
    ("appointment", "Termine"),
    ("homework", "Hausaufgaben"),
    ("lesson", "Unterricht"),
    ("learning", "Lernplattform"),
)


def _merge_adjacent_lessons(lessons):
    merged = []
    for lesson in lessons:
        if merged:
            previous = merged[-1]
            if (previous.subject == lesson.subject and previous.room == lesson.room
                    and previous.teacher_label == lesson.teacher_label
                    and previous.ends_at == lesson.starts_at):
                previous.ends_at = lesson.ends_at
                continue
        merged.append(lesson)
    return merged


def _item(kind, label, title, *, starts_at=None, ends_at=None, meta="", url=""):
    local_start = timezone.localtime(starts_at) if starts_at else None
    local_end = timezone.localtime(ends_at) if ends_at else None
    return {
        "kind": kind,
        "kind_label": label,
        "title": title,
        "time": local_start.strftime("%H:%M") if local_start else "",
        "sort": local_start.strftime("%H:%M") if local_start else "23:59",
        "starts_at": local_start,
        "ends_at": local_end,
        "end_time": local_end.strftime("%H:%M") if local_end else "",
        "duration_minutes": (
            max(1, int((local_end - local_start).total_seconds() // 60))
            if local_start and local_end
            else None
        ),
        "meta": meta,
        "url": url,
        "lesson_count": 1,
        "is_double": False,
    }


def _merge_consecutive_lessons(day_items):
    merged = []
    for item in sorted(day_items, key=lambda value: (value["sort"], value["title"])):
        previous = merged[-1] if merged else None
        same_lesson = (
            previous
            and item["kind"] == previous["kind"] == "lesson"
            and item["title"] == previous["title"]
            and item["meta"] == previous["meta"]
            and previous["ends_at"]
            and item["starts_at"]
            and timedelta(0) <= item["starts_at"] - previous["ends_at"] <= timedelta(minutes=15)
        )
        if not same_lesson:
            merged.append(item.copy())
            continue
        previous["ends_at"] = item["ends_at"]
        previous["end_time"] = item["end_time"]
        previous["duration_minutes"] = max(
            1, int((previous["ends_at"] - previous["starts_at"]).total_seconds() // 60)
        )
        previous["lesson_count"] += 1
        previous["is_double"] = previous["lesson_count"] == 2
    return merged


def _minutes(value):
    return value.hour * 60 + value.minute


def build_calendar_context(
    *,
    school_class,
    selected_day,
    webuntis_connections,
    itslearning_connections,
    view="month",
    active_categories=None,
):
    if view not in {"month", "week", "day"}:
        view = "month"
    active_categories = set(dict(CALENDAR_CATEGORIES) if active_categories is None else active_categories)
    month_start = selected_day.replace(day=1)
    next_month = (month_start + timedelta(days=32)).replace(day=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    month_grid_start = month_start - timedelta(days=month_start.weekday())
    week_start = selected_day - timedelta(days=selected_day.weekday())
    if view == "month":
        grid_start, grid_end = month_grid_start, month_grid_start + timedelta(days=42)
        previous_date, next_date = previous_month, next_month
        period_title = month_start.strftime("%B %Y")
    elif view == "week":
        grid_start, grid_end = week_start, week_start + timedelta(days=7)
        previous_date, next_date = week_start - timedelta(days=7), week_start + timedelta(days=7)
        period_title = f"{week_start:%d.%m.}–{(grid_end - timedelta(days=1)):%d.%m.%Y}"
    else:
        grid_start, grid_end = selected_day, selected_day + timedelta(days=1)
        previous_date, next_date = selected_day - timedelta(days=1), selected_day + timedelta(days=1)
        period_title = selected_day.strftime("%d.%m.%Y")
    items = defaultdict(list)

    lessons = _merge_adjacent_lessons(list(
        WebUntisLesson.objects.filter(
            connection__in=webuntis_connections,
            starts_at__date__gte=grid_start,
            starts_at__date__lt=grid_end,
        ).order_by("starts_at")
    ))
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
                ends_at=lesson.ends_at,
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
                    ends_at=timezone.make_aware(
                        datetime.combine(day, lesson.ends_at),
                        timezone.get_current_timezone(),
                    ),
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
                ends_at=entry.ends_at,
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
                ends_at=entry.ends_at,
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
                ends_at=event.ends_at,
                meta=event.location,
                url=f"/mehr/veranstaltungen/{event.pk}/",
            )
        )

    for day in list(items):
        items[day] = [item for item in _merge_consecutive_lessons(items[day]) if item["kind"] in active_categories]

    days = []
    for offset in range(42):
        day = month_grid_start + timedelta(days=offset)
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
        "view": view,
        "previous_date": previous_date,
        "next_date": next_date,
        "period_title": period_title,
        "calendar_categories": [
            {"key": key, "label": label, "active": key in active_categories}
            for key, label in CALENDAR_CATEGORIES
        ],
        "calendar_days": days,
        "agenda": sorted(items[selected_day], key=lambda value: (value["sort"], value["title"])),
        **_timeline_context(
            school_class=school_class,
            selected_day=selected_day,
            week_start=week_start,
            view=view,
            items=items,
        ),
    }


def _timeline_context(*, school_class, selected_day, week_start, view, items):
    visible_dates = [selected_day] if view == "day" else [week_start + timedelta(days=i) for i in range(7)]
    timed_items = [item for day in visible_dates for item in items[day] if item["starts_at"]]
    grid = (
        TimeGrid.objects.filter(school=school_class.school, valid_from__lte=selected_day)
        .filter(Q(valid_until__isnull=True) | Q(valid_until__gte=selected_day))
        .order_by("-valid_from")
        .first()
    )
    periods = list(grid.periods.all()) if grid else []
    starts = [_minutes(period.starts_at) for period in periods]
    starts.extend(_minutes(item["starts_at"].time()) for item in timed_items)
    ends = [_minutes(period.ends_at) for period in periods]
    ends.extend(_minutes((item["ends_at"] or item["starts_at"] + timedelta(minutes=45)).time()) for item in timed_items)
    timeline_start = min(starts or [7 * 60 + 30])
    timeline_end = max(ends or [16 * 60])
    timeline_start = (timeline_start // 15) * 15
    timeline_end = max(timeline_start + 60, ((timeline_end + 14) // 15) * 15)
    if not periods:
        timeline_start = (timeline_start // 60) * 60
        timeline_end = max(timeline_start + 60, ((timeline_end + 59) // 60) * 60)
    span = timeline_end - timeline_start
    timeline_days = []
    for day in visible_dates:
        positioned = []
        all_day = []
        for item in items[day]:
            if not item["starts_at"]:
                all_day.append(item)
                continue
            start = _minutes(item["starts_at"].time())
            end = _minutes((item["ends_at"] or item["starts_at"] + timedelta(minutes=45)).time())
            positioned.append(
                {
                    **item,
                    "top_percent": round((start - timeline_start) * 100 / span, 3),
                    "height_percent": round(max(30, end - start) * 100 / span, 3),
                }
            )
        timeline_days.append({"date": day, "items": positioned, "all_day": all_day})
    if periods:
        timeline_periods = [
            {
                "number": period.number,
                "label": f"{period.number}. Stunde",
                "start": period.starts_at.strftime("%H:%M"),
                "end": period.ends_at.strftime("%H:%M"),
                "duration": int(
                    (datetime.combine(selected_day, period.ends_at) - datetime.combine(selected_day, period.starts_at)).total_seconds()
                    // 60
                ),
                "top_percent": round((_minutes(period.starts_at) - timeline_start) * 100 / span, 3),
            }
            for period in periods
        ]
    else:
        # Imported lessons already contain authoritative start/end times.  A missing
        # locally maintained TimeGrid must therefore never collapse the day view.
        # Quarter-hour rounded markers keep irregular and substituted lessons useful.
        marker_start = (timeline_start // 60) * 60
        marker_end = ((timeline_end + 59) // 60) * 60
        timeline_periods = []
        for minute in range(marker_start, marker_end + 1, 60):
            if minute < timeline_start or minute > timeline_end:
                continue
            clock = f"{minute // 60:02d}:{minute % 60:02d}"
            timeline_periods.append(
                {
                    "number": None,
                    "label": f"{clock} Uhr",
                    "start": clock,
                    "end": "",
                    "duration": None,
                    "top_percent": round((minute - timeline_start) * 100 / span, 3),
                }
            )
    return {
        "timeline_days": timeline_days,
        "timeline_height": max(540, int(span * 1.25)),
        "timeline_periods": timeline_periods,
        "timeline_uses_school_grid": bool(periods),
    }
