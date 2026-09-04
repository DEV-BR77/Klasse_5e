"""The small, reviewed catalogue of portal adapters and their import modules."""

from .models import PortalAdapter, PortalAdapterModule

ADAPTER_CATALOG = {
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
    for key, label, description in provider_definition(adapter.provider)["modules"]:
        PortalAdapterModule.objects.get_or_create(
            adapter=adapter,
            key=key,
            defaults={"label": label, "description": description},
        )
