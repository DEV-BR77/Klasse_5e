# Technische Übergabe – KlassID 0.3.0-beta.2

Stand: 03.09.2026

## Umgesetzter Stand

Das Feedback aus `Feedback aktueller Stand.docx` wurde als Anforderungsquelle
ausgewertet; die zwei beigefügten Screenshots dienten ausschließlich als
visuelle Referenz. Umgesetzt sind das generische KlassID-Branding, die mobile
Navigation, das neue Dashboard, Wochenkalender, Chat, Veranstaltungen,
Mitbringlisten, Einstellungen und die Mobilitätsansichten.

Die Mobilitätsbörse unterstützt Bieten und Suchen für Auto, Fahrrad und
Fußgruppen. Eine lokale Straßenkarte für Wolfsburg zeigt Schule, grobe
Startbereiche und öffentliche Treffpunkte. Kartenpunkte werden direkt durch
Antippen gewählt; ein zulässiger Umweg wird in Minuten gepflegt. Die Karte
benötigt zur Laufzeit keinen externen Kartendienst.

Mitbringlisten unterstützen freie Positionen, Mengen, Reservierungen und erste
Einträge bereits beim Anlegen eines Events. Die Lebensmittelsuche bietet lokale
deutsche Kategorien und ergänzt diese optional über Spoonacular. Der Provider
erhält nur den Suchbegriff.

## Wichtige Dateien

- Oberfläche: `app/templates/`, `app/static/app.css`, `app/static/app.js`
- Mobilität: `app/src/klasse5e/mobility/`, `app/templates/mobility/`
- Offline-Karte: `app/static/maps/wolfsburg-roads.json`
- Karten-Generator: `tools/Build-LocalMobilityMap.py`
- Events/Spoonacular: `app/src/klasse5e/events/`,
  `app/templates/ui/event_detail.html`
- Kartendokumentation: `docs/integrations/Offline-Mobilitaetskarte.md`
- Spoonacular-Dokumentation:
  `docs/integrations/Spoonacular-Lebensmittelsuche.md`
- Migration: `app/src/klasse5e/mobility/migrations/0002_map_origins_and_detour_minutes.py`

## Bewusste Abgrenzung

Das separate Repository `PDF-SmartForms-Studio` wurde nicht verändert. Das
Feedback dazu ist eine repositoryübergreifende Integrationsaufgabe und benötigt
eine ausdrücklich freigegebene Bearbeitung dieses Projekts. Bestehende
KlassID-Dokumentfunktionen bleiben unverändert verfügbar.

Die vorbestehende Benutzerdatei `.tmp-webuntis-main.js` wurde weder verändert
noch in Git aufgenommen.

## Auslieferung

Ausgeliefert ist `0.3.0-beta.2` als Containerimage
`klasse-5e-app:0.3.0b2`. Die Funktionsänderungen sind mit `6563ffb` und der
APIlayer-Endpunktkorrektur mit `b990218` auf `origin/main` veröffentlicht.

- 138 Django-Gesamttests bestanden; anschließend 6 fokussierte
  Spoonacular-Tests nach der Endpunktkorrektur.
- Ruff, JavaScript-Syntax, Django-Systemcheck und Migrationscheck bestanden.
- Container für Anwendung, Vision und PostgreSQL sind `healthy`.
- `mobility.0002_map_origins_and_detour_minutes` ist produktiv angewendet.
- Der echte APIlayer-Aufruf liefert Produktvorschläge; der Schlüssel wurde nur
  als vorhanden/nicht vorhanden geprüft und nicht ausgegeben.
- `https://5e.eventmonitor.eu/health/` und die Anmeldeseite unter
  `https://5e.klassid.de/accounts/login/` liefern HTTP 200.
- Die produktive Anmeldeseite wurde im Browser mit generischem KlassID-Logo und
  der neuen Nutzenkommunikation visuell geprüft.
