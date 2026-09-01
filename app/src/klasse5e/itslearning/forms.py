from urllib.parse import urlparse

from django import forms

ALLOWED_HOST = "wob.itslearning.com"


def _is_allowed_https_url(value):
    parsed = urlparse(value)
    return parsed.scheme == "https" and parsed.hostname == ALLOWED_HOST


class ConnectionForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.HiddenInput)
    username = forms.CharField(
        label="Wobila-Benutzername",
        max_length=160,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Wobila-Passwort",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    calendar_url = forms.CharField(
        label="itslearning-Kalender (iCal)",
        required=False,
        max_length=1000,
        help_text="https:// oder webcal://",
    )

    def clean_calendar_url(self):
        value = self.cleaned_data["calendar_url"].strip()
        normalized = "https://" + value[9:] if value.startswith("webcal://") else value
        if value and not _is_allowed_https_url(normalized):
            raise forms.ValidationError(
                "Nur ein itslearning-Kalender von wob.itslearning.com ist erlaubt."
            )
        return value


class CourseForm(forms.Form):
    external_id = forms.CharField(label="Kurs-ID", max_length=32)
    title = forms.CharField(label="Kursname", max_length=180)
    course_url = forms.URLField(
        label="Kurs-Link", max_length=500, assume_scheme="https"
    )
    rss_url = forms.URLField(
        label="RSS-Feed", required=False, max_length=1000, assume_scheme="https"
    )
    report_360_url = forms.URLField(
        label="360\N{DEGREE SIGN}-Bericht",
        required=False,
        max_length=500,
        assume_scheme="https",
    )
    learning_objectives_url = forms.URLField(
        label="Lernzielbeurteilung",
        required=False,
        max_length=500,
        assume_scheme="https",
    )

    def clean(self):
        cleaned = super().clean()
        for field in ("course_url", "rss_url", "report_360_url", "learning_objectives_url"):
            value = cleaned.get(field)
            if value and not _is_allowed_https_url(value):
                self.add_error(field, "Nur HTTPS-Links von wob.itslearning.com sind erlaubt.")
        return cleaned


class WebDavForm(forms.Form):
    student_id = forms.IntegerField(widget=forms.HiddenInput)
    username = forms.RegexField(
        label="WebDAV-Benutzername", regex=r"^[a-z0-9._-]{3,64}$", max_length=64
    )
    password = forms.CharField(
        label="Neues WebDAV-Passwort",
        min_length=12,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
