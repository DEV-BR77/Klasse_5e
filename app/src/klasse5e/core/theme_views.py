"""Safe, explicitly persisted design-token editing for portal administrators."""

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import PortalTheme, Role


COLOR_FIELDS = {
    "primary": "Primärfarbe", "primary_dark": "Primärfarbe – Hover",
    "primary_light": "Primärfarbe – dezente Flächen", "accent": "Akzentfarbe",
    "background": "Seitenhintergrund", "surface": "Karten und Eingabefelder",
    "text": "Text", "text_muted": "Ergänzende Texte", "border": "Linien und Rahmen",
    "success": "Erfolg", "warning": "Warnung", "danger": "Fehler und Gefahr",
}
EXTENDED_COLOR_FIELDS = {"border", "success", "warning", "danger"}


def _relative_luminance(value):
    channels = [int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(first, second):
    lighter, darker = sorted((_relative_luminance(first), _relative_luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class DesignTokenForm(forms.ModelForm):
    radius = forms.ChoiceField(label="Rundungen", choices=[
        (".7rem", "Klar"), ("1rem", "Modern"), ("1.15rem", "Standard"),
        ("1.35rem", "Weich"), ("1.7rem", "Verspielt"),
    ])
    shadow_strength = forms.IntegerField(label="Schattenstärke", min_value=0, max_value=30,
                                        widget=forms.NumberInput(attrs={"min": 0, "max": 30}))

    class Meta:
        model = PortalTheme
        fields = [
            *COLOR_FIELDS, "typography", "density", "radius", "shadow_strength", "is_dark"
        ]
        labels = {
            **COLOR_FIELDS,
            "typography": "Typografie",
            "density": "Abstände und Steuerelemente",
            "is_dark": "Dunkles Erscheinungsbild",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in COLOR_FIELDS:
            self.fields[name] = forms.RegexField(
                r"^#[0-9a-fA-F]{6}$", label=COLOR_FIELDS[name],
                widget=forms.TextInput(attrs={"type": "color"}),
                required=name not in EXTENDED_COLOR_FIELDS,
                error_messages={"invalid": "Bitte einen vollständigen HEX-Farbwert angeben."},
            )
        self.fields["typography"].required = False
        self.fields["density"].required = False

    def clean(self):
        cleaned = super().clean()
        for field_name in (*EXTENDED_COLOR_FIELDS, "typography", "density"):
            if not cleaned.get(field_name):
                cleaned[field_name] = getattr(self.instance, field_name)
        surface = cleaned.get("surface")
        if not surface:
            return cleaned
        contrast_requirements = {
            "text": (4.5, "Text benötigt mindestens 4,5:1 Kontrast zur Kartenfarbe."),
            "text_muted": (3.0, "Ergänzende Texte benötigen mindestens 3:1 Kontrast zur Kartenfarbe."),
            "success": (3.0, "Erfolgszustände benötigen mindestens 3:1 Kontrast zur Kartenfarbe."),
            "warning": (3.0, "Warnzustände benötigen mindestens 3:1 Kontrast zur Kartenfarbe."),
            "danger": (3.0, "Fehlerzustände benötigen mindestens 3:1 Kontrast zur Kartenfarbe."),
        }
        for field_name, (minimum, message) in contrast_requirements.items():
            value = cleaned.get(field_name)
            if value and _contrast_ratio(value, surface) < minimum:
                self.add_error(field_name, message)
        return cleaned


class ThemeForm(DesignTokenForm):
    class Meta(DesignTokenForm.Meta):
        fields = ["name", "description", "audience", *DesignTokenForm.Meta.fields]
        labels = {**DesignTokenForm.Meta.labels, "name": "Name", "description": "Beschreibung", "audience": "Zielgruppe"}


@login_required
@require_http_methods(["GET", "POST"])
def design_system(request):
    from .ui_views import _shared

    if not (request.user.is_superuser or request.user.roleassignment_set.filter(
        active=True, role__in=[Role.PRIMARY_ADMIN, Role.DEPUTY_ADMIN]
    ).exists()):
        raise Http404
    themes = PortalTheme.objects.all()
    theme_id = request.POST.get("theme_id") if request.method == "POST" else request.GET.get("theme")
    if theme_id:
        if not theme_id.isdecimal():
            raise Http404
        theme = get_object_or_404(themes, pk=theme_id)
    else:
        theme = themes.filter(pk=request.user.selected_theme_id).first() or themes.first()
    form = DesignTokenForm(request.POST or None, instance=theme) if theme else None
    if request.method == "POST" and form and form.is_valid():
        form.save()
        messages.success(request, f"Design-Tokens für „{theme.name}“ gespeichert. Die Theme-Auswahl bleibt unverändert.")
        return redirect(f"{reverse('design-system')}?theme={theme.pk}")
    context = _shared(request, "Designsystem & CSS-Tokens", "management")
    context.update({"token_form": form, "editing_theme": theme, "themes": themes})
    return render(request, "ui/design_system.html", context)
