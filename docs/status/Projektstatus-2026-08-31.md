# Projektstatus Klasse 5e

Stand: 1. September 2026

## Kurzfassung

Das Klassenportal ist unter https://5e.eventmonitor.eu erreichbar und der
Produktionscontainer laeuft stabil. Der persoenliche WebUntis-Stundenplan ist
importiert, die numerischen Fach- und Lehrkraft-IDs sind in der laufenden
Datenbank durch lesbare Bezeichnungen ersetzt und die Kalenderseite ist jetzt
ein gemeinsamer, responsiver Monatskalender.

Termine, Hausaufgaben, Unterricht und Lernplattform-Eintraege erscheinen in
einer Kalenderansicht mit getrennten Farben und gemeinsamer Tagesagenda. Der
iCalendar-Download und die abonnierbare iCalendar-Adresse bleiben vorhanden.

Der reale Hausaufgabenimport ist noch nicht abgeschlossen: Das tatsaechliche
Elternkonto kann den JSON-RPC-Stundenplan lesen. Der interne
Hausaufgaben-Endpunkt antwortet in diesem Sitzungsweg weiterhin nicht
autorisiert beziehungsweise mit HTTP 500. Die real beobachtete Antwortstruktur
ist bereits synthetisch nachgebildet und der Normalisierer ist implementiert,
aber es wurden weiterhin keine echten Hausaufgaben gespeichert.

## Repository und Deployment

- Branch: main
- Code-Commit: f3fa80d
- Produktionsimage: klasse-5e-app:0.2.0
- Oeffentliche URL: https://5e.eventmonitor.eu
- App-, Datenbank- und Vision-Container laufen.
- Das App-Root-Dateisystem bleibt schreibgeschuetzt.
- Private Referenzdateien, Zugangsdaten und Laufzeitantworten sind nicht in Git.

## In diesem Stand umgesetzt

### Fach- und Lehrkraft-Mapping

- Die bereitgestellte Tabelle wurde mit dem Spreadsheet-Werkzeug strukturell
  ausgewertet.
- Anzeigenamen werden beim Import von versehentlichen Abschlusskommas bereinigt.
- Der neue Import verbindet den persoenlichen Referenzstundenplan ueber Datum
  sowie exakte Start- und Endzeit mit den bereits normalisierten
  WebUntis-Stunden.
- Sowohl Fachkuerzel als auch ausgeschriebene Fachnamen werden gegen die
  klassenbezogene Tabelle 3 aufgeloest.
- Numerische WebUntis-Fach- und Lehrkraft-IDs werden als lokale Aliase
  gespeichert; es findet kein unzulaessiger schulweiter Lehrkraefteabruf statt.
- Reale Anwendung: 12 Fach-Aliase, 17 Lehrkraft-Aliase und 294 aktualisierte
  Stundenzeilen.
- Nach der Anwendung enthalten 0 von 357 Stundenzeilen noch eine rein
  numerische Fach- oder Lehrkraftanzeige.
- Die im gemeldeten Dashboard-Zustand sichtbaren Zahlenpaare sind verschwunden;
  die erwartete Kombination Kunst/Duve ist in der laufenden Zuordnung vorhanden.

### Gemeinsamer Kalender

- Echte Monatsansicht mit sechs Wochen und Navigation zwischen Monaten.
- Gemeinsame Datenquelle fuer persoenlichen WebUntis-Unterricht,
  WebUntis-Hausaufgaben, Klassenkalender, Veranstaltungen und
  itslearning-Kalender.
- Farben und zusaetzliche Textlabels:
  - Termine: blau
  - Hausaufgaben: orange
  - Unterricht: gruen
  - Lernplattform: violett
- Ein Klick auf einen Tag oeffnet darunter eine gemeinsame, chronologisch
  sortierte Tagesagenda.
- Mobile Darstellung reduziert Monatstage auf gut erfassbare Farbpunkte und
  zeigt Details in der Tagesagenda.
- Die Bedeutung wird nicht nur ueber Farbe vermittelt.
- Interner Produktions-Smoke-Test: HTTP 200, Monatsraster und Legende vorhanden.

### Hausaufgaben

- Die reale Elternkonto-Antwortstruktur data/homeworks/lessons/records/teachers
  ist als streng begrenzter Normalisierungspfad umgesetzt.
- Hausaufgaben werden ueber lessonId mit dem Fach verbunden.
- Aufgabe, Bemerkung, Ausgabe- und Faelligkeitsdatum sowie Erledigt-Status
  werden normalisiert.
- Synthetische Regressionstests bestehen.
- Der reale Lauf speichert noch 0 Hausaufgaben, weil der REST-Endpunkt im
  funktionierenden JSON-RPC-Sitzungskontext HTTP 500 liefert.
- Erfolgreiche Stundenplandaten bleiben bei diesem Teilfehler erhalten.
- Es wurden keine Cookies, Tokens, Passwoerter oder Rohantworten gespeichert
  oder dokumentiert.

## Qualitaetsgate

- 92 App-Tests bestanden.
- WebUntis-/Mapping-/Kalender-Regressionen: 6 bestanden.
- Ruff: ohne Befund.
- Python-Kompilierung: erfolgreich.
- git diff --check: ohne Befund.
- Django makemigrations --check --dry-run: keine Aenderungen.
- Django check --deploy: keine Fehler; zwei bekannte HSTS-Haertungshinweise fuer
  includeSubDomains und preload bleiben bewusst offen.
- Produktionsimage erfolgreich gebaut und ausgerollt.
- Health, Login und produktives CSS liefern ueber HTTPS jeweils HTTP 200.
- Produktives Dashboard intern gerendert: HTTP 200, lesbare Bezeichnungen,
  keine der gemeldeten numerischen Paare.
- Produktiver Kalender intern gerendert: HTTP 200, Monatsraster und Farblegende.

## Offene Punkte

1. Den modernen Elternkonto-Authentisierungsweg fuer den
   Hausaufgaben-Endpunkt stabilisieren. Der WebUntis-Browserablauf verwendet
   zusaetzlich einen User-Token-Schritt; der alte JSON-RPC-Session-Cookie allein
   genuegt nicht.
2. Danach einen kontrollierten Realimport der Hausaufgaben durchfuehren und
   Idempotenz sowie Aktualitaetsanzeige pruefen.
3. Abwesenheiten lesend als eigene Capability umsetzen.
4. Eine Krankmeldung nur nach eindeutig verifiziertem, separatem Schreibrecht,
   eigener Zustimmung und bestaetigtem Schreibablauf anbieten; sonst direkt
   nach WebUntis verlinken.
5. Anschliessend die qualitative Onboarding- und Layout-Abnahme mit einem neuen,
   noch nicht zugeordneten Testkonto fortsetzen.
6. Die beiden HSTS-Optionen erst aktivieren, wenn bestaetigt ist, dass alle
   Subdomains dauerhaft ausschliesslich HTTPS verwenden.

## Naechster Arbeitsauftrag

Der ausfuehrbare Folgeauftrag steht in
docs/planning/Naechste-Codex-Aufgabe-Phase-9B.md.
