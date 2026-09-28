"""The small, reviewed catalogue of portal adapters and their import modules."""

from .models import (
    PortalAdapter,
    PortalAdapterDefinition,
    PortalAdapterModule,
)

ADAPTER_CATALOG = {
    PortalAdapter.Provider.WEBUNTIS: {
        "label": "WebUntis",
        "default_url": "",
        "hint": "Schulplattform für Stundenplan, Vertretungen, Hausaufgaben, Prüfungen und Abwesenheiten.",
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
            (
                "absences",
                "Abwesenheiten",
                "Abwesenheiten aus WebUntis anzeigen und über den persönlichen Zugang melden.",
                True,
            ),
        ),
    },
    PortalAdapter.Provider.ITSLEARNING: {
        "label": "itslearning",
        "default_url": "",
        "hint": "Lernplattform für Materialien und schulische Termine.",
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
    PortalAdapter.Provider.SCHULMANAGER: {
        "label": "Schulmanager Online",
        "default_url": "https://login.schulmanager-online.de/",
        "hint": "Nachrichten und Elternbriefe werden ausschließlich lesend und kindbezogen abgerufen.",
        "modules": (
            (
                "messages",
                "Nachrichten",
                "Neue Schulmanager-Nachrichten als neutrale Benachrichtigung anzeigen.",
                True,
            ),
            (
                "letters",
                "Elternbriefe",
                "Neue Elternbriefe als neutrale Benachrichtigung anzeigen.",
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
        "label": "Individuelle Schnittstelle",
        "default_url": "",
        "hint": "Individuelle Schulplattform; Verbindungsweg und Module werden vor Freigabe technisch geprüft.",
        "modules": (),
    },
}


def provider_definition(provider):
    return ADAPTER_CATALOG[provider]


def seed_default_modules(adapter):
    definition = adapter.definition or PortalAdapterDefinition.objects.filter(
        provider=adapter.provider
    ).first()
    if definition and adapter.definition_id != definition.pk:
        adapter.definition = definition
        adapter.save(update_fields=["definition"])
    for key, label, description, *credential_requirement in provider_definition(adapter.provider)[
        "modules"
    ]:
        definition_module = (
            definition.modules.filter(key=key).first() if definition else None
        )
        access_model = (
            definition_module.access_model
            if definition_module
            else (
                "child"
                if credential_requirement and credential_requirement[0]
                else "none"
            )
        )
        PortalAdapterModule.objects.get_or_create(
            adapter=adapter,
            key=key,
            defaults={
                "label": label,
                "description": description,
                "requires_child_credentials": bool(credential_requirement and credential_requirement[0]),
                "definition_module": definition_module,
                "access_model": access_model,
            },
        )
