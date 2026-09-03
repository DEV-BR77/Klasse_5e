from django import forms
from django.utils import timezone

from .models import MeetingPoint, MobilityListing

WEEKDAYS = [("mo", "Mo"), ("tu", "Di"), ("we", "Mi"), ("th", "Do"), ("fr", "Fr")]


class MobilityListingForm(forms.ModelForm):
    start_latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    start_longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    weekdays = forms.MultipleChoiceField(
        choices=WEEKDAYS, widget=forms.CheckboxSelectMultiple, label="Wochentage"
    )
    safety_confirmed = forms.BooleanField(
        label=(
            "Ich bestätige: Das Portal vermittelt Kontakte. Aufsicht, Versicherung, "
            "Fahrerlaubnis und Kindersitze klären die beteiligten Erwachsenen."
        )
    )

    class Meta:
        model = MobilityListing
        fields = [
            "kind",
            "transport",
            "direction",
            "title",
            "approximate_area",
            "start_latitude",
            "start_longitude",
            "weekdays",
            "time_from",
            "time_until",
            "seats",
            "max_detour_km",
            "max_detour_minutes",
            "valid_until",
            "notes",
            "safety_confirmed",
        ]
        widgets = {
            "time_from": forms.TimeInput(attrs={"type": "time"}),
            "time_until": forms.TimeInput(attrs={"type": "time"}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "kind": "Art",
            "transport": "Verkehrsmittel",
            "direction": "Fahrtrichtung",
            "title": "Kurzer Titel",
            "approximate_area": "Grober Bereich",
            "time_from": "Frühestens",
            "time_until": "Spätestens",
            "seats": "Freie Plätze",
            "max_detour_km": "Maximaler Umweg (km)",
            "max_detour_minutes": "Maximaler Umweg (Minuten)",
            "valid_until": "Gültig bis",
            "notes": "Hinweise",
        }

    def clean(self):
        cleaned = super().clean()
        if (
            cleaned.get("time_from")
            and cleaned.get("time_until")
            and cleaned["time_until"] <= cleaned["time_from"]
        ):
            self.add_error("time_until", "Das Ende muss nach dem Beginn liegen.")
        if cleaned.get("valid_until") and cleaned["valid_until"] < timezone.localdate():
            self.add_error("valid_until", "Die Gültigkeit darf nicht in der Vergangenheit liegen.")
        if cleaned.get("transport") != MobilityListing.Transport.CAR:
            cleaned["seats"] = 0
            cleaned["max_detour_km"] = None
            cleaned["max_detour_minutes"] = None
        return cleaned


class MeetingPointForm(forms.ModelForm):
    class Meta:
        model = MeetingPoint
        fields = ["name", "description", "meeting_time", "latitude", "longitude"]
        widgets = {
            "meeting_time": forms.TimeInput(attrs={"type": "time"}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }
        labels = {
            "name": "Öffentlicher Treffpunkt",
            "description": "Beschreibung",
            "meeting_time": "Treffzeit",
            "latitude": "Position auf der Karte",
            "longitude": "Position auf der Karte",
        }
