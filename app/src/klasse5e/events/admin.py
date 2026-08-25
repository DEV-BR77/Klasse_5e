from django.contrib import admin
from wagtail.snippets.models import register_snippet

from .models import ContributionCategory, ContributionItem, Event, ReminderDelivery, Reservation

register_snippet(Event)
for model in [Event, ContributionCategory, ContributionItem, Reservation, ReminderDelivery]:
    admin.site.register(model)
