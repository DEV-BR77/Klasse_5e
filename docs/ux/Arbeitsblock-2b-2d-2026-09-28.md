# Arbeitsblock 2b–2d – Ergebnis und Prüfnachweis

Stand: 28.09.2026. Dieser Bericht ergänzt die
[Gesamtanalyse](Gesamtanalyse-2026-09-28.md). Die Arbeitsblöcke **2b, 2c und
2d sind im lokalen Quellstand umgesetzt und funktional geprüft**. Die
Build-/Staging-/Gerätezuordnung aus 2e und die unabhängige Schlussabnahme aus
Punkt 3 sind ausdrücklich noch nicht vorweggenommen.

## 2b – Designsystem, CSS-Tokens und Themes

- `PortalTheme` besitzt jetzt neben den vorhandenen Markenfarben auch
  editierbare semantische Tokens für Linie, Erfolg, Warnung und Fehler sowie
  Typografie und Dichte. Migration: `0041_portaltheme_semantic_tokens.py`.
- Der Token-Editor ist in drei kompakte Gruppen gegliedert und zeigt eine
  unmittelbare Komponentenprobe für Navigation, Karte, Formularfeld,
  Statusfarben und Aktionen. Das Öffnen eines Themes aktiviert es nicht.
- Die serverseitige Validierung prüft Text/Fläche mit 4,5:1 sowie Statusfarben
  mit 3:1. Unlesbare Kombinationen werden nicht gespeichert.
- Theme-Verwaltung und persönliche Vorschau arbeiten weiterhin mit
  Vorschau → Abbrechen beziehungsweise Vorschau → Übernehmen → Reload.
- Die gemeinsame CSS-Quelle verwendet die neuen Tokens für Schrift, Linien,
  Statusfarben, Eingabehöhe und Flächenabstand.

Prüfung:

- 20 fokussierte Theme-/Token-/Redesign-Tests bestanden.
- Im abschließenden kombinierten Lauf waren alle 32 geänderten Verträge grün.
- Alle acht Presets wurden im Browser bei 360, 768 und 1440 px geöffnet,
  abgebrochen und einmal übernommen; kein Überlauf und kein JavaScript-Fehler.
- Visuell geprüft wurden insbesondere Token-Editor Desktop/Mobil,
  `Midnight Focus` mobil sowie Theme-Verwaltung und persönliche Vorschau.

Lokale Buildgrenze: Windows Application Control blockiert die mitgelieferte
Tailwind-Programmdatei (`WinError 4551`). Deshalb ist die Quellschicht fertig,
der vorhandene lokale Dist-Bundle aber nicht neu erzeugt. Das erklärt auch den
im lokalen Browserbild noch sichtbaren alten CSS-Pseudohaken im Login; Markup
und Quell-CSS enthalten nur noch ein dekoratives, `aria-hidden` gesetztes
Symbol. Der reproduzierbare Linux-/Staging-Build ist Bestandteil von 2e.

Fortschreibung vom 28.09.2026: Die Windows-Grenze wurde mit einem
reproduzierbaren Linux-/Docker-Build aufgelöst. Das erzeugte CSS-Bundle wurde
dem Buildkandidaten eindeutig zugeordnet und der Browser-Smoke anschließend
erneut bestanden. Image, Hashes und Prüfergebnis stehen im
[Buildnachweis](Buildkandidat-2026-09-28.md). Staging wurde dabei nicht
verändert; die unabhängige Schlussabnahme bleibt separat.

## 2c – Navigation, URL-Verträge, Zugang und begrenzte CSS-Konsolidierung

- Rückziele folgen jetzt der Fachhierarchie:
  Klasse → zugehörige Schule/Klassen-Tab, Adapterdefinition → Adapterliste,
  Designsystem → Themes und itslearning-Unterseiten → itslearning-Portal.
- Die drei doppelt definierten Kalender-/iCal-Routen wurden auf je eine
  Definition reduziert.
- Der Login enthält genau einen Passwort-zurücksetzen-Link. Die Vorteilssymbole
  sind dekorativ ausgezeichnet und der Cookie-Text beschreibt ausschließlich
  erforderliche Sitzungscookies.
- Die abschließende gemeinsame CSS-Schicht bindet Shell, Fokus, Felder,
  Schaltflächen, Karten und Statusdarstellung an die semantischen Tokens;
  Hover-Zustände verschieben keine Flächen.

Prüfung:

- 9 Navigations- und Formularaktionsverträge bestanden.
- 3 Login-Verträge bestanden.
- Django-Systemcheck ohne Befund; `makemigrations --check --dry-run` meldet
  keine fehlende Migration.

## 2d – Funktions- und Seitenpakete

Die vereinbarte fachliche Matrix B01–B04, B08–B11 und B14–B23 wurde mit
synthetischen Daten und passenden Rollen gegen bestehende sowie ergänzte
Vertragstests ausgeführt. Abgedeckt sind Zugang, Orientierung, Dashboard,
Kalender, Familie/Freigaben, Schulzugänge, Abwesenheiten,
Benachrichtigungen/PWA, Schulen/Klassen, Adapter/Module, Kontakte,
Klassenleben, Inhalte/Dokumente, Veranstaltungen, Fotos, Mobilität,
Photo Memory, Portalverwaltung und Betrieb/Technik.

- 47 zugeordnete Testdateien: **277 Tests bestanden** in 333,93 Sekunden.
- Danach vollständiger lokaler Browser-Smoke mit isolierter Datenbank:
  36 benannte Seiten, 360/768/1440 px, 156 Screenshots.
- Geprüfte Bedienfolgen: Login, Navigation und Rückwege, Abbrechen/Speichern,
  Theme-Vorschau und -Übernahme, Token-Speicherung, Validierungsfehler,
  Chat-Senden/Fehler/Ändern, Melden/Moderieren, Datei, Emoji/Sticker,
  Familien-Tabs, Monitoring-Konfiguration sowie Avatar-Posen und Übernahme.
- Ergebnis: **PASS**, kein horizontaler Dokumentüberlauf und
  `browser-errors.json` enthält `[]`.

Die Aufnahmen liegen lokal unter `qa-artifacts/redesign-current/`. Sie sind
Prüfartefakte des Arbeitsstands, keine Behauptung einer bereits ausgerollten
Staging-Version.

## Bewusste Grenzen und nächster Block

Nicht in 2b–2d künstlich simuliert wurden echte Push-Zustellung, ein reales
Mikrofon, PWA-Installation auf Zielgeräten, externe Schulübermittlungen und die
Zuordnung des Quellstands zu einem reproduzierbar gebauten Staging-Image.
Diese Punkte gehören zusammen mit der Dist-CSS-Erzeugung ausschließlich in
**2e – Build-Zuordnung, Staging-Vergleich und Gerätefunktionen**. Erst danach
folgt Punkt 3, die unabhängige visuelle und funktionale Schlussabnahme gegen
die konkreten Mockups und Anforderungen.
