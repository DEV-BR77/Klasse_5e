# Technische Übergabe – Klasse 5e

Stand: 02.09.2026

## Kurzstatus

Die vorhandene Veranstaltungs- und Mitbringfunktion ist produktseitig bereits
implementiert: Kategorien, Mengen, freie Beiträge, verbindliche Reservierungen,
Rücknahmen, Audit und Schutz gegen Überbuchung gehören zum Modul `events`.

Für eine neue Mobilitäts-/Mitfahrbörse wurde das verpflichtende UX- und
Datenschutzgate erstellt und als separater Commit gesichert. Eine fachliche
Implementierung der Mobilitätsfunktion ist noch nicht begonnen.

Spoonacular wurde als Datenbasis für Rezept- und Zutatenvorschläge ausgewählt.
Der API-Token ist lokal DPAPI-verschlüsselt gespeichert. Adapter,
Organisatorensuche, idempotente Zutatenübernahme, Tests und sichere
Docker-Laufzeitübergabe sind inzwischen implementiert.

## Bereits umgesetzt

### Mitbringlisten

- Veranstaltungen haben Kategorien und Mitbringpositionen.
- Eltern können Mengen reservieren, eigene Beiträge anlegen und eigene
  Reservierungen zurücknehmen.
- Reservierungen verwenden Idempotenzschlüssel und Datenbanktransaktionen;
  doppelte oder überbuchende Zusagen werden verhindert.
- Zugriffe sind an die aktive Klassenmitgliedschaft gebunden.
- Die technische Grundlage liegt in:
  - `app/src/klasse5e/events/models.py`
  - `app/src/klasse5e/events/services.py`
  - `app/src/klasse5e/events/views.py`
  - `app/src/klasse5e/core/ui_views.py`
  - `app/templates/ui/event_detail.html`
  - `app/tests/test_phase4.py`

### Mobilität und Mitfahrbörse

Das vorgeschaltete Gate umfasst:

- Biete-/Suche-Flüsse für PKW, Fahrrad- und Laufgruppen;
- Kartenansicht mit vollständigem Listenfallback;
- öffentliche Treffpunkte, grobe Bereiche und keine Wohnadressen auf Karten;
- private, widerrufbare Adressfreigabe ausschließlich nach gegenseitiger
  Annahme;
- Klassenisolation, Guardian-Prüfung, Meldung, Moderation, Ablauf und Audit;
- neutrale Push-Daten ohne Kinder-, Kontakt- oder Standortdetails.

Dateien:

- `docs/ux/Mobilitaet-Wireframes.md`
- `docs/planning/Mobilitaet-Mitfahrboerse-Gate.md`
- bestehende Ausgangsspezifikation:
  `docs/planning/Naechste-Aufgabe-Mobilitaet-Mitfahrboerse.md`

Git-Commit: `c3c78dc docs: define mobility privacy and UX gate`.

### Spoonacular als Datenbasis

Die geplante Nutzung ist bewusst eingeschränkt:

- Serverseitige Rezeptsuche und Abruf der Zutatenliste;
- keine Übertragung von Eltern-, Kinder-, Klassen-, Standort- oder
  Reservierungsdaten an den Anbieter;
- keine dauerhafte Speicherung externer Rezeptdaten;
- Organisatoren übernehmen Zutaten bewusst als lokale Mitbringpositionen;
- die verbindlichen Elternzusagen verbleiben ausschließlich in Klasse 5e.

Der Token ist als `secret://klasse5e/spoonacular-api-key` lokal
DPAPI-verschlüsselt hinterlegt. Sein Wert wurde nie ausgelesen, angezeigt oder
in Projektdateien gespeichert.

Der eingebundene Adapter liegt in:

- `app/src/klasse5e/events/spoonacular.py`

Er enthält:

- `search_recipes(query)` für eine begrenzte Rezeptsuche;
- `recipe_ingredients(recipe_id)` für Zutaten, Menge und Einheit;
- kurze Timeouts und einen kontrollierten Fehlerzustand;
- keine persistente Cache- oder Datenspeicherung.

## Umgesetzter Spoonacular-Ablauf

- Laufzeitkonfiguration in `app/src/klasse5e/settings.py` und `compose.yaml`.
- Suche nur für Eventorganisatoren; Übernahme ist CSRF-geschütztes POST.
- Lokale Quellenreferenz verhindert doppelte Rezeptimporte je Event.
- Responsive Rezeptauswahl und vollständige manuelle Fallback-Mitbringliste.
- Deployment über `tools/Deploy-Klasse5e.ps1`, ohne Secret in Git oder `.env`.

## Umgesetzte Mobilitätsfunktion

Das Django-Modul `mobility` enthält Biete-/Suche-Einträge, Auto, Fahrrad und
Fußgruppen, geordnete öffentliche Treffpunkte, Reaktionen, Annahme/Ablehnung,
Meldung, Status/Ablauf, deduplizierte Aufrufe sowie private widerrufbare
Abholfreigaben. Die responsive Übersicht besitzt Filter und eine lokale
schematische Routenkarte ohne externe Kartenabfragen.

Vor einem Realpilot bleiben außerdem Rechtsgrundlage, verbindliche
Löschfristen, versionierte Standort-/Kontaktfreigabetexte und die
Moderationsverantwortung zu entscheiden.

## Aktueller Arbeitsbaum und Hinweis

Die Datei `.tmp-webuntis-main.js` ist eine vorbestehende Benutzerdatei; sie wurde nie
  verändert und ist nicht Teil dieser Arbeiten.
