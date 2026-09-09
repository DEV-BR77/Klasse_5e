from django import forms
from django.utils import timezone


class AbsenceSubmissionForm(forms.Form):
    student = forms.TypedChoiceField(label="Kind", coerce=int, choices=())
    starts_on = forms.DateField(label="Von", initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    ends_on = forms.DateField(label="Bis", initial=timezone.localdate, widget=forms.DateInput(attrs={"type": "date"}))
    starts_time = forms.TimeField(label="Uhrzeit von", initial="08:00", widget=forms.TimeInput(attrs={"type": "time"}))
    ends_time = forms.TimeField(label="Uhrzeit bis", initial="17:00", widget=forms.TimeInput(attrs={"type": "time"}))
    note = forms.CharField(label="Anmerkung (optional)", max_length=500, required=False, widget=forms.Textarea(attrs={"rows": 3}))
    token = forms.UUIDField(widget=forms.HiddenInput)

    def __init__(self, *args, children, selected_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = {item.student.pk: item for item in children}
        self.fields["student"].choices = [
            (item.student.pk, " ".join(part for part in (item.student.first_name, item.student.last_name) if part))
            for item in children
        ]
        if not self.is_bound and selected_id in self.children:
            self.initial["student"] = selected_id

    def clean(self):
        data = super().clean()
        student = data.get("student")
        start, end = data.get("starts_on"), data.get("ends_on")
        start_time, end_time = data.get("starts_time"), data.get("ends_time")
        if student not in self.children:
            self.add_error("student", "Das ausgewählte Kind ist nicht berechtigt.")
        if start and end and start_time and end_time and (end < start or (end == start and end_time <= start_time)):
            raise forms.ValidationError("Das Ende muss nach dem Beginn liegen.")
        return data


class WebUntisCredentialForm(forms.Form):
    username = forms.CharField(
        label="Benutzername für den Schuldaten-Zugang",
        max_length=160,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Passwort für den Schuldaten-Zugang",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
