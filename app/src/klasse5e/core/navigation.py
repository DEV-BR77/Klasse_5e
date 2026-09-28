"""Deterministic parent navigation; never redirect to an untrusted Referer."""

import re

from django.urls import reverse


def parent_navigation(request):
    path = request.path
    if path == "/":
        return None
    if path == "/verwaltung/":
        return {"url": "/mehr/?bereich=einstellungen", "label": "Einstellungen"}
    if path.startswith("/verwaltung/rollen/personen/") and (request.GET.get("user") or request.POST.get("user_id")):
        from urllib.parse import urlencode
        filters = {key: request.GET[key] for key in ("q", "school", "class", "role", "status") if request.GET.get(key)}
        suffix = "?" + urlencode(filters) if filters else ""
        return {"url": "/verwaltung/rollen/personen/" + suffix, "label": "Personenübersicht"}
    class_match = re.fullmatch(r"/verwaltung/klassen/(\d+)/", path)
    if class_match:
        from .models import SchoolClass

        school_id = SchoolClass.objects.filter(pk=class_match.group(1)).values_list(
            "school_id", flat=True
        ).first()
        if school_id:
            return {
                "url": f"{reverse('school-detail', args=[school_id])}?tab=classes",
                "label": "Klassen der Schule",
            }
        return {"url": reverse("school-management"), "label": "Schulen & Klassen"}
    parents = (
        ("/verwaltung/designsystem/", "/verwaltung/themes/", "Themes"),
        ("/verwaltung/adapter-definition/", "/verwaltung/adapter/", "Adapter"),
        ("/verwaltung/schulen/", "/verwaltung/schulen/", "Schulen & Klassen"),
        ("/verwaltung/adapter/", "/verwaltung/adapter/", "Adapter"),
        ("/verwaltung/", "/verwaltung/", "Portalverwaltung"),
        ("/chat/", "/chat/", "Unterhaltungen"),
        ("/itslearning/", "/itslearning/", "itslearning"),
        ("/mehr/familie/", "/mehr/familie/?tab=overview", "Familienübersicht"),
        ("/accounts/", "/einstellungen/profil/?tab=account", "Sicherheit & Konto"),
        ("/mehr/veranstaltungen/", "/mehr/veranstaltungen/", "Veranstaltungen"),
        ("/mehr/", "/mehr/", "Bereiche"),
        ("/einstellungen/", "/mehr/", "Bereiche"),
    )
    for prefix, url, label in parents:
        if path.startswith(prefix) and request.get_full_path() != url:
            return {"url": url, "label": label}
    return {"url": "/", "label": "Start"}
