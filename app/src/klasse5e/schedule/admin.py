from django.contrib import admin

from .models import (
    CalendarChange,
    CalendarEntry,
    ICalSubscription,
    LessonPeriod,
    SchoolBreak,
    TimeGrid,
    TimetableEntry,
)

admin.site.register(
    [
        TimetableEntry,
        CalendarEntry,
        CalendarChange,
        ICalSubscription,
        TimeGrid,
        LessonPeriod,
        SchoolBreak,
    ]
)
