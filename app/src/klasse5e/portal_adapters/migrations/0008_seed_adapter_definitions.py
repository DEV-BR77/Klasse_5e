from django.db import migrations

DEFINITIONS = {
    "webuntis": {
        "label": "WebUntis",
        "hint": "Stundenplan, Vertretungen, Hausaufgaben, Prüfungen und Abwesenheiten.",
        "integration_type": "import",
        "modules": {
            "timetable": ("Stundenplan", "Unterrichtszeiten und Fächer.", "child"),
            "substitutions": ("Vertretungen", "Ausfälle und Raumänderungen.", "child"),
            "homework": ("Hausaufgaben", "Aufgaben und Fälligkeiten.", "child"),
            "exams": ("Prüfungen", "Angekündigte Arbeiten.", "child"),
            "absences": ("Abwesenheiten", "Abwesenheiten anzeigen und melden.", "child"),
        },
    },
    "itslearning": {
        "label": "itslearning",
        "hint": "Materialien und schulische Termine.",
        "integration_type": "import",
        "modules": {
            "learning-material": ("Lernmaterial", "Kurse und Materialien.", "child"),
            "calendar": ("Schulkalender", "Termine der Lernplattform.", "child"),
        },
    },
    "schulmanager": {
        "label": "Schulmanager Online",
        "hint": "Kindbezogene Nachrichten und Elternbriefe.",
        "integration_type": "import",
        "modules": {
            "messages": ("Nachrichten", "Schulische Nachrichten.", "child"),
            "letters": ("Elternbriefe", "Elternbriefe anzeigen.", "child"),
        },
    },
    "mensamax": {
        "label": "MensaMax",
        "hint": "Speiseplan und Allergene.",
        "integration_type": "import",
        "modules": {"weekly-meal-plan": ("Speiseplan der Woche", "Menüs der Woche.", "child")},
    },
    "dsbmobile": {
        "label": "DSBmobile",
        "hint": "Vertretungen und Aushänge.",
        "integration_type": "import",
        "modules": {
            "substitutions": ("Vertretungen", "Entfälle und Vertretungen.", "child"),
            "notices": ("Aushänge", "Veröffentlichte Aushänge.", "child"),
        },
    },
    "mundo": {
        "label": "MUNDO Schule",
        "hint": "Öffentliche OER-Materialien.",
        "integration_type": "external",
        "modules": {"material-search": ("Materialsuche", "Offene Bildungsmaterialien.", "none")},
    },
    "wirlernenonline": {
        "label": "WirLernenOnline",
        "hint": "Öffentliche Lernmaterialien.",
        "integration_type": "external",
        "modules": {"material-search": ("Materialsuche", "Lernmaterialien und OER-Angebote.", "none")},
    },
    "wobila-bbb": {
        "label": "BBB Wobila",
        "hint": "Freigegebene externe Meetings.",
        "integration_type": "external",
        "modules": {"meeting-launcher": ("Meetings öffnen", "Externes Meeting-Portal.", "external")},
    },
    "wobila-mail": {
        "label": "Mail Wobila",
        "hint": "Freigegebenes externes Webmail-Portal.",
        "integration_type": "external",
        "modules": {"webmail-launcher": ("Schul-E-Mail öffnen", "Externes Webmail-Portal.", "external")},
    },
    "custom": {
        "label": "Individuelle Schnittstelle",
        "hint": "Technisch geprüfte individuelle Schulplattform.",
        "integration_type": "custom",
        "modules": {},
    },
}


def seed_definitions(apps, schema_editor):
    Definition = apps.get_model("portal_adapters", "PortalAdapterDefinition")
    DefinitionModule = apps.get_model("portal_adapters", "PortalAdapterDefinitionModule")
    Adapter = apps.get_model("portal_adapters", "PortalAdapter")
    Module = apps.get_model("portal_adapters", "PortalAdapterModule")
    for provider, values in DEFINITIONS.items():
        definition, _ = Definition.objects.update_or_create(
            provider=provider,
            defaults={
                "label": values["label"],
                "hint": values["hint"],
                "integration_type": values["integration_type"],
                "is_published": provider != "custom",
                "is_technically_reviewed": provider != "custom",
            },
        )
        for key, (label, description, access_model) in values["modules"].items():
            definition_module, _ = DefinitionModule.objects.update_or_create(
                definition=definition,
                key=key,
                defaults={
                    "label": label,
                    "description": description,
                    "access_model": access_model,
                    "is_published": True,
                },
            )
            for module in Module.objects.filter(adapter__provider=provider, key=key):
                module.definition_module_id = definition_module.pk
                module.access_model = access_model
                module.save(update_fields=["definition_module", "access_model"])
        Adapter.objects.filter(provider=provider, definition__isnull=True).update(
            definition_id=definition.pk
        )


class Migration(migrations.Migration):
    dependencies = [("portal_adapters", "0007_portaladapterdefinition_and_more")]

    operations = [migrations.RunPython(seed_definitions, migrations.RunPython.noop)]
