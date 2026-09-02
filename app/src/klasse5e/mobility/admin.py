from django.contrib import admin

from .models import MeetingPoint, MobilityListing, MobilityReaction, MobilityReport

# Exact pickup disclosures are intentionally excluded from general admin views.
for model in [MobilityListing, MeetingPoint, MobilityReaction, MobilityReport]:
    admin.site.register(model)
