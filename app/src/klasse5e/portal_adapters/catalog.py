"""The small, reviewed catalogue of portal adapters and their import modules."""

from .models import PortalAdapter, PortalAdapterModule

ADAPTER_CATALOG = {
    PortalAdapter.Provider.WEBUNTIS: {
        "label": "Schuldaten-Zugang",
        "default_url": "",
        "hint": "Stundenplan und Schulorganisation werden erst nach der Freigabe einzelner Funktionen für die Schule angezeigt.",
        "modules": (
            (
                "timetable",
                "Stundenplan",
                "Unterrichtszeiten und Fächer des Kindes im persönlichen Überblick.",
                True,
            ),
            (
                "substitutions",
                "Vertretungen",
                "Ausfälle, Vertretungen sowie Raum- und Lehreränderungen anzeigen.",
                True,
            ),
            (
                "homework",
                "Hausaufgaben",
                "Aufgaben, Fälligkeiten und Fachzuordnung abrufen.",
                True,
            ),
            (
                "exams",
                "Prüfungen",
                "Angekündigte Arbeiten und Prüfungstermine anzeigen.",
                True,
            ),
        ),
    },
    PortalAdapter.Provider.ITSLEARNING: {
        "label": "Lernplattform-Zugang",
        "default_url": "",
        "hint": "Lernmaterialien und Termine werden nur nach Freigabe der einzelnen Funktionen bereitgestellt.",
        "modules": (
            (
                "learning-material",
                "Lernmaterial",
                "Kurse, Materialien und Hinweise der Lernplattform anzeigen.",
                True,
            ),
            (
                "calendar",
                "Schulkalender",
                "Termine der Lernplattform zum persönlichen Kalender ergänzen.",
                True,
            ),
        ),
    },
    PortalAdapter.Provider.MENSAMAX: {
        "label": "MensaMax",
        "default_url": "https://app.mensamax.de/",
        "hint": "Projekt und Einrichtung werden aus den Zugangsdaten der Schule übernommen.",
        "modules": (
            (
                "weekly-meal-plan",
                "Speiseplan der Woche",
                "Menüs, Allergene und Zusatzstoffe für die aktuelle Woche abrufen.",
            ),
        ),
    },
    PortalAdapter.Provider.DSBMOBILE: {
        "label": "DSBmobile",
        "default_url": "https://www.dsbmobile.de/",
        "hint": "Die Schulnummer und das jeweilige DSBmobile-Zugangsformat werden erst beim Adaptertest hinterlegt.",
        "modules": (
            (
                "substitutions",
                "Vertretungen",
                "Entfälle, Vertretungen sowie Raum- und Lehreränderungen abrufen.",
            ),
            (
                "notices",
                "Aushänge",
                "Veröffentlichte Aushänge und ergänzende Hinweise abrufen.",
            ),
        ),
    },
    PortalAdapter.Provider.MUNDO: {
        "label": "MUNDO Schule",
        "default_url": "https://mundo.schule/",
        "hint": "Öffentliche OER-Materialien. Die spätere Suche nutzt nur freigegebene Metadaten und öffnet das Material beim Anbieter.",
        "modules": (
            (
                "material-search",
                "Materialsuche",
                "Offene Bildungsmaterialien nach Fach, Jahrgang und Thema finden.",
            ),
        ),
    },
    PortalAdapter.Provider.WIR_LERNEN_ONLINE: {
        "label": "WirLernenOnline",
        "default_url": "https://wirlernenonline.de/",
        "hint": "Öffentliche Lernmaterialien. Vor einer integrierten Suche werden Lizenz, Metadaten und Suchweg geprüft.",
        "modules": (
            (
                "material-search",
                "Materialsuche",
                "Lernmaterialien und OER-Angebote nach Thema und Jahrgang finden.",
            ),
        ),
    },
    PortalAdapter.Provider.WOBILA_BBB: {
        "label": "BBB Wobila",
        "default_url": "https://bbb.wobila.de/b",
        "hint": "Der Wobila-Schüleraccount wird im externen Meeting-Portal verwendet. KlassID speichert keine Zugangsdaten.",
        "modules": (
            (
                "meeting-launcher",
                "Meetings öffnen",
                "Freigegebenen BBB-Zugang als externes Meeting-Portal bereitstellen.",
            ),
        ),
    },
    PortalAdapter.Provider.WOBILA_MAIL: {
        "label": "Mail Wobila",
        "default_url": "https://mail.wobila.de/webmail/",
        "hint": "Der Wobila-Schüleraccount wird im externen Webmail-Portal verwendet. E-Mail-Inhalte bleiben außerhalb von KlassID.",
        "modules": (
            (
                "webmail-launcher",
                "Schul-E-Mail öffnen",
                "Freigegebenen Webmail-Zugang als externes Portal bereitstellen.",
            ),
        ),
    },
    PortalAdapter.Provider.CUSTOM: {
        "label": "Eigenes Portal",
        "default_url": "",
        "hint": "Verbindungsweg und Module werden nach einer technischen Prüfung ergänzt.",
        "modules": (),
    },
}


def provider_definition(provider):
    return ADAPTER_CATALOG[provider]


def seed_default_modules(adapter):
    for key, label, description, *credential_requirement in provider_definition(adapter.provider)[
        "modules"
    ]:
        PortalAdapterModule.objects.get_or_create(
            adapter=adapter,
            key=key,
            defaults={
                "label": label,
                "description": description,
                "requires_child_credentials": bool(credential_requirement and credential_requirement[0]),
            },
        )
