from django.contrib import admin

from .models import CalendarChange, CalendarEntry, ICalSubscription, TimetableEntry

admin.site.register([TimetableEntry, CalendarEntry, CalendarChange, ICalSubscription])
