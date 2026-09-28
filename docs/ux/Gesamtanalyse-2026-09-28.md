# Gesamtanalyse und Übergabe für die Browser-Abnahme

Stand: 28.09.2026. **Analyseblock abgeschlossen; Portal noch nicht insgesamt abgenommen.**

Fortschreibung: Die Arbeitsblöcke 2a–2d wurden anschließend umgesetzt und
lokal geprüft. Maßgeblich für den aktuellen Stand ist der
[Prüfnachweis zu 2b–2d](Arbeitsblock-2b-2d-2026-09-28.md); als nächstes folgt
2e (Build-/Staging-/Gerätezuordnung). Die nachstehende Analyse bleibt als
Ausgangsbefund erhalten.

Dieser Bericht schließt Punkt 1 der zuletzt vereinbarten Aufteilung ab:
einmalige Gesamtanalyse → gezielte Korrekturen und fehlende Prüfungen → finale
Abnahme. Das ist keine erneute Durchführung der acht ursprünglichen
Umsetzungsblöcke. Produktcode, Daten und Staging wurden in diesem Analyseblock
nicht geändert. Ein neuer vollständiger Testlauf wurde nicht gestartet.

## 1. Ergebnis

Es gibt erhebliche bereits umgesetzte und lokal geprüfte Arbeit. Die pauschale
Aussage, Personenverwaltung, Rollenrechte, Chat und Avatar seien weiterhin
unfertig, ist durch den aktuellen Bericht nicht gedeckt. Ebenso wenig ist eine
vollständige Portalabnahme belegt.

Die wesentlichen verbleibenden Aufgaben sind:

1. Konkrete gemeinsame UI-Lücken schließen: Formularaktionen, Token-Wirkung,
   Editor-Komposition und gezielte visuelle Zustände.
2. Für die übrigen Fachbereiche die noch fehlenden vollständigen Bedienabläufe
   nachweisen. Ein vorhandener Seiten-Smoke-Test bleibt gültiger Teilnachweis.
3. Den geprüften lokalen Stand eindeutig einem Staging-Build zuordnen und die
   offenen Staging-/Geräteprüfungen ausführen.

Die vorhandenen Prüfungen von Personen, Rollen und Chat werden übernommen.
Eine Wiederholung braucht einen Grund: betroffene gemeinsame Änderung,
konkreter Fehler, abweichender Build oder bisher ungeprüfter Zustand.

## 2. Quellen und belastbarer Umfang

- Verbindlicher Auftrag: `../UI Neuausrichtung von KlassID.md` und die neueren
  Nutzeranweisungen zu allen Seiten, aufklappbaren Menüs, stabilen Layouts,
  Zurück sowie Abbrechen links/Speichern rechts.
- Zielbeschreibung: `Aufgabe-4-Mockups-und-Interaktionen.md` und
  `tailwind-playground-redesign.html`. Die spätere Forderung nach unbeweglichen
  Oberflächen ersetzt die ältere Hover-Anhebung im Mockup-Dokument.
- Aktueller Fortschrittsnachweis: `Redesign-Abnahme-2026-09-25.md`, einschließlich
  der Ergänzungen vom 27.09.; Rollenvertrag: `../Rollenrechte-Laufzeit.md`.
- Historische Quellen: `UI-Abnahmeplan.md`, `UI-Ist-Soll-Abgleich.md`,
  `Portal-Redesign-Audit.md`. Deren frühere Aussagen sind keine frischen Befunde.
- Aktueller Quellstand: URL-Konfiguration, Templates, gemeinsame CSS-/JS-Schicht,
  Navigation, Theme-Editor und zugehörige Browser-Prüfskripte. Inventar:
  [Routen und Templates](Gesamtanalyse-Inventar-2026-09-28.md).
- Acht bestehende lokale Aufnahmen wurden gezielt angesehen: Chat bei 1440 px,
  Personendetail bei 1440 px, Token-Editor bei 1440 px, dunkle Theme-Vorschau
  bei 360 px, Bereiche bei 1440 px, Kalender bei 1440 px, Avatar-Dialog bei
  360 px und Dashboard bei 1440 px. Sie stammen aus früheren Prüfläufen, nicht
  aus einer heute neu gestarteten Browsersitzung.
- Der bestehende Staging-Tab wurde lesend geöffnet: Er zeigt tatsächlich die
  Anmeldung mit abgelaufener Sitzung. Geschützte Staging-Seiten wurden hier
  nicht live geprüft. Das ist kein Hindernis für diesen Analysebericht, aber
  ein offener Zugangspunkt für die spätere Staging-Abnahme.

Die Inventur enthält **177 Routeinträge, 174 unterschiedliche Pfade und 122
HTML-Templates**. Routen sind nicht gleich Seiten: enthalten sind APIs,
Downloads, Aktionen, dynamische Details und drei Includes für Accounts,
Django-Admin und Wagtail. Deren Unterrouten sind nicht in den 174 enthalten.
Die Inventur ist vollständig für diese expliziten Projektdefinitionen;
Detailanalysen und visuelle Stichproben sind keine Behauptung, jeden Klick
bereits neu geprüft zu haben.

Die bereitgestellten Staging-Screenshots vom 23.–25.09. dokumentieren auch
beanstandete Zustände. Sie sind nicht automatisch Zielmockups. Maßgeblich für
die Gestaltung bleiben die Zielvorgaben. Ein vollständiger bildgenauer Abgleich
aller ursprünglichen Chat-/Designreferenzen ist mit den hier ausgewerteten
Quellen nicht belegt. Bei der Endabnahme muss jeder visuelle Vergleich die
konkrete Zielreferenz nennen; wo sie fehlt, bleibt genau dieser Vergleich offen.

## 3. Bereits belegte Arbeit übernehmen

| Bereich | Vorhandener lokaler Nachweis vom 27.09. | Noch gezielt offen |
|---|---|---|
| Personen | Eigene Detailansicht, Suche/Filter/Sortierung, mobile Karten, Rollenaktionen, Rückweg; 28 Backendtests und Browser bei 360/768/1440/1920 px dokumentiert | Staging-Zuordnung; nur betroffene Regressionen nach gemeinsamen Änderungen |
| Rollen/Rechte | Zuweisen/Entziehen, Matrix, atomare Speicherung, direkte Zugriffswirkung, zweite Benutzersitzung; 111 unterschiedliche relevante Backendtests über mehrere Läufe dokumentiert | Kein neuer pauschaler Rollen-Neuaufbau; Staging und noch ungetestete Fachkombinationen |
| Chat | Räume, Mitglieder, Senden/Fehler/Ändern, Moderation, PDF, Grafik-Sticker und simulierte Audioaufnahme; mehrbreitige Browsernachweise | Reales Mikrofon, Audioqualität, echte Push-Zustellung, Einsatznachweis des Aufbewahrungsjobs, vollständiger Referenzvergleich |
| Avatar | Stehend/Sitzend, Vorschau, Abbrechen, Übernehmen, Speichern/Reload in eigenem und Kinderprofil dokumentiert | Gezielte mobile Vorschauprüfung aus Befund V-02; Staging |
| Profil | Stammdaten speichern/verwerfen, In-App-Präferenz speichern; übrige Tabs erreichbar | Sicherheit, Fotowechsel und restliche Präferenzen nicht dadurch vollständig abgenommen |
| Themes/Token-Editor | Acht Vorschauen, Abbrechen/Übernehmen/Reload; Editorvalidierung und Theme-Fehlerkorrektur dokumentiert | Vollständige Komponentenwirkung, alle Kontrastzustände, gezielter Editor-Layoutvergleich |
| Navigation/Kontext | Aufklappbare Einstellungsgruppen und Kontextwechsel mit Escape/Geometrie dokumentiert | Rückziele für weitere Detailseiten, realistische große Menüs und lange Bezeichnungen |

Die genannten Testzahlen sind historische Nachweise, keine in diesem Block
neu ausgeführten Tests. Sie werden weder addiert noch als vollständige aktuelle
Gesamtsuite ausgegeben. Die einzelne Datei `.qa-current/browser-errors.json`
enthält `[]`; sie identifiziert jedoch nicht alle vorherigen Läufe oder Builds.

## 4. Konkrete Befunde für Punkt 2

Priorität P1: vor Gesamtfreigabe erledigen. P2: begrenzte Konsistenz- oder
Bedienkorrektur. „Prüfbedarf“ ist kein bereits reproduzierter Laufzeitfehler.

| ID | Priorität / Sicherheit des Befunds | Beleg und Auswirkung | Begrenzter Auftrag und Abschlussnachweis |
|---|---|---|---|
| F-01 | P1, im Template bestätigt | `ui/school_detail.html`: Stammdaten haben Speichern vor Entfernen und kein Abbrechen; Klassenanlage ebenfalls ohne Abbrechen. `ui/chat_retention_settings.html`: nur Speichern. `ui/event_poll.html`: Abstimmung und Veröffentlichung ohne Abbrechen. `ui/family.html`: Familienfotoformular ohne Abbrechen. `itslearning/storage.html`: Speicherformular ohne Abbrechen. | Gemeinsame Aktionsleiste je bearbeitbarem Formular, Abbrechen verwirft per GET, Speichern rechts. Entfernen als eigene folgenbezogene Aktion. Mit synthetischen Werten ändern → abbrechen → öffnen und ändern → speichern → laden prüfen. Keine Abbrechen-Pflicht aus bloßen Such-/Filterformularen ableiten. |
| F-02 | P1, strukturell bestätigt | `styles.css` importiert acht ältere Stylesheets plus `design-system.css` und enthält spätere Übersteuerungen. Dies ist weiterhin eine Übergangsschicht. | Komponentenweise klare Zuständigkeit herstellen. Nur tatsächlich konkurrierende Regeln entfernen; kein pauschales Löschen alter CSS-Dateien. Jede geänderte Komponente an ihren Verbrauchern prüfen. |
| F-03 | P1, teilweise Token-Anbindung bestätigt | `PortalTheme.css_variables` und `DesignTokenForm` speichern acht Farben, Rundung, Schatten und Dunkelmodus. Die späten Regeln binden Buttons und mehrere Karten an `--radius`, Eingaben behalten jedoch `.75rem`, Verzeichnisgruppen `1rem`; semantische Radiusgrößen sind feste Pixelwerte. Typografie/Abstände/Statusfarben sind nicht über diesen Editor konfigurierbar. | Verbindlichen Token-Umfang sichtbar definieren; vorhandene Rundungs-/Schattenwerte konsistent auf die vorgesehenen gemeinsamen Komponenten anwenden. Neue editierbare Felder nur soweit vom Designsystemauftrag benötigt. Vorschau und gespeicherte Seite an Button, Input, Karte, Dialog, Navigation vergleichen. |
| V-01 | P2, visuell in bestehender Aufnahme bestätigt | `.qa-current/design-system-1440.png`: sehr große Abstände zwischen Theme-Auswahl, Titel, Hilfetext und ersten Feldern; wesentliche Editorfläche beginnt erst am unteren Bildrand. Gemeinsame CSS-Regel gibt jedem direkten Nicht-Header/-Footer-Kind einer Settings-Karte Innenabstand. | Editor als kompakte Feld-/Vorschaufläche gestalten; gemeinsame Innenabstände auf Container begrenzen. Editor oben und unten bei Desktop/Mobil aufnehmen; Vorschau und echte Aktionen eindeutig trennen. |
| V-02 | P2, gezielter Prüfbedarf aus Aufnahme | `.qa-current/avatar-dialog-360.png` zeigt bei geöffneter Hintergrundkategorie nur einen Teil der Figur. Pose-Auswahl und Aktionsleiste sind vorhanden. Aus der Aufnahme allein ist nicht bestimmbar, ob dies nur der gespeicherte Scrollzustand ist. | Dialog einmal frisch öffnen, Pose und Hintergrund wechseln, Vorschau-/Optionsbereich scrollen. Vollständige Figur muss kontrolliert erreichbar bleiben; gegebenenfalls Vorschau kompakt fixieren. Bestehende Pose-/Speichertests übernehmen. |
| V-03 | P1, fehlender Nachweis | Dunkle Aufnahmen zeigen schwer erkennbare aktive Navigationsbeschriftungen. Der Smoke-Lauf verändert Theme-Werte (`Smoke-Update des Designs`); diese Bilder beweisen keinen Defekt aller ursprünglichen Presets. Der Editor prüft im Hinweis nur Text gegen Kartenfläche. | Unveränderte Presets auf Text, aktive Navigation, sekundäre Buttons, Fokus, Fehler-/Erfolgsmeldungen prüfen. Kontrastwerte erfassen; Teständerungen isolieren. Acht Themes nicht mit allen Seiten kartesisch multiplizieren: erst Komponenten je Theme, dann Fachseiten im bestätigten Basisdesign. |
| N-01 | P2, Navigation teils korrigiert / Rest prüfbedürftig | `ui/more.html` enthält verschachtelte `details`; Rollen, Personen und Designsystem haben eigene Ziele. `parent_navigation` fällt bei `/verwaltung/klassen/<id>/` und Adapterdefinitionen allgemein auf Portalverwaltung zurück. | Hierarchische Rückziele Schule → Klasse und Adapterliste → Definition festlegen und erhalten. Vorhandene eigenständige Rollen-/Personenrouten nicht erneut zusammenlegen. Filter- und Tab-Erhalt für bearbeitete Wege prüfen. |
| C-01 | P2, doppelte Definition bestätigt | `urls.py` enthält Wochenabruf, iCal-Feed und iCal-Tokenroute je zweimal mit gleichem Namen/Handler. | Je eine Definition behalten; URL-Auflösung und bestehende Kalendertests prüfen. Dies ist kein nachgewiesener Ausfall der Kalenderseite. |
| A-01 | P1, veraltete Statusaussagen bestätigt | `UI-Ist-Soll-Abgleich.md` behauptet einen ausgerollten Stand; neuer Bericht vom 27.09. nennt lokale, nicht ausgerollte Änderungen. Alte Chatabschnitte nennen fehlende Grafik-Sticker, spätere Abschnitte belegen ihre Umsetzung. | Diesen Bericht als aktuelle Übergabe verwenden; alte Einträge datiert lesen. Vor Staging-Abnahme Build/Arbeitsstand eindeutig dokumentieren. Nur neue Analyse-Dateien isoliert versionieren; keine fremden Änderungen mitnehmen. |
| A-02 | P1, Nachweislücke | `Test-SettingsRedesign.py` besucht 36 benannte Seiten in seiner Seitenschleife; dort werden überwiegend Status, Überschrift und Overflow geprüft. Spezielle Aktionen folgen nur für ausgewählte Bereiche. | Fehlende Journeys aus Abschnitt 5 ergänzen. Ein `200` oder ein leerer Konsolenfehlerbericht genügt nicht für Speichern, Rechte, Datenfluss oder Referenztreue. |
| U-01 | P2, Staging-Beobachtung | Login zeigt „Passwort vergessen?“ zweimal; Vorteiltexte erscheinen im Accessibility-Baum mit doppelten Häkchen. Die Cookie-Aussage ist zudem erklärungsbedürftig bei einem Session-basierten Portal. | Login-Dopplung beseitigen, dekorative Symbole zugänglich auszeichnen, Text zu erforderlichen Sitzungscookies sachlich prüfen. Erst am zugehörigen Zugangspaket bearbeiten. |

Die früheren Fehler „Person lässt sich nicht öffnen“, „Rollen führt nur zu
Personen“, „Token-Seite ist nur Themes“ und „Pose fehlt“ werden hier **nicht**
als weiterhin nachgewiesene lokale Fehler geführt. Eigene Routen, passende
Templates und lokale Bediennachweise sind inzwischen vorhanden. Auf Staging
muss genau dieser aktualisierte Stand später ankommen.

## 5. Vollständige Seiten- und Funktionsmatrix

„Teilnachweis“ bedeutet vorhandene Implementierung oder dokumentierte Prüfung,
nicht automatisch eine fachliche Endabnahme. Detaillierte Endpunkte stehen im
Inventar; dynamische IDs werden nur mit synthetischen Datensätzen befüllt.

| Paket | Seiten / Einstiege | Vorhandene Basis | Verbleibender vollständiger Ablauf |
|---|---|---|---|
| B01 Zugang | Login, Einladung, Registrierung, Familienstart, Verifikation, Aktivierung, Passwort, MFA, Logout/Timeout | Lokale Templates und Login-/MFA-Smoke | gültig/ungültig/abgelaufen, Feldfehler, Rückwege, Reset/MFA einschließlich Bibliotheksseiten; keine echten Passwörter ändern |
| B02 Orientierung | Onboarding, Pause/Fortsetzen, Tutorial, Projekt, Demo, Datenschutz, Impressum, Nutzung, Lizenzen, Offline | Übersichts-Smoke / eigene Templates | alle Schritte, Überspringen/Fortsetzen, Links, Offline-Zustand, mobile Lesbarkeit |
| B03 Tagesübersicht | Start, Erwachsenen-/Kinderkontext, Tag, Hausaufgabenstatus, Hinweise, Abwesenheitenausschnitt | Kontext- und Dashboardtests, Screenshots | mehrere Kinder/kein Kind, volle/fehlende Schuldaten, Wochenwechsel, Aufgabenänderung, passende Detailziele |
| B04 Kalender | Tag/Woche/Monat, Filter, Ereignisdetail, Verbinden, iCal/Abonnement | Übersichtssmoke und Backendtests | alle Ansichten mit Daten, Filterkombination, Datumswechsel, Detailöffnung, Download/Widerruf; C-01 |
| B05 Chat | Liste/Raum, Direktchat, Raumdialoge, Mitglieder, Nachrichten, Medien, Moderation | weitgehender lokaler Abschluss, siehe Abschnitt 3 | nur benannte Restzustände, reale Audio-/Pushprüfung und Referenz-/Stagingvergleich |
| B06 Chatverwaltung | Katalog, Grafik-Sticker, Aufbewahrung | Katalog und Grafik-Sticker geprüft | F-01; Aufbewahrung ausschließlich mit synthetischen abgelaufenen/geschützten Nachrichten und realem Joblauf prüfen |
| B07 Profil/Avatar | Daten, Kontaktfreigaben, Foto/Avatar, Themes, Sicherheit, Kontolöschung | Avatar und ausgewählte Profilflüsse geprüft | V-02, Fotowechsel/Entfernen, unabhängige Freigaben, Sicherheitswege; Löschung nur disponibler Testkonten |
| B08 Familie/Freigaben | Übersicht, Erwachsene, Kinderanlage, Stammdaten, Beziehungen, Familienfoto, Einwilligungen/Widerruf | Teiltests und Kindavatar | Kind/Familie vollständig anlegen/ändern, mehrere Berechtigte, Konflikte/Entzug, F-01, Zugriff mit nicht berechtigtem Konto |
| B09 Schulzugänge | Kind-Module, WebUntis-Kompatibilitätsroute, itslearning/Kurse, WebDAV | Familien-/Adaptertests; bestehende technische Verbindungen | eine verständliche Zuständigkeit, Freigaben, Testen/Fehler/Pausieren/Entfernen; WebUntis-GET rendert weiterhin eigene Seite, keine reine Weiterleitung |
| B10 Abwesenheiten | `/abwesenheiten/`, lokaler Entwurf, Status/Rückprüfung | Backendtests | Kindauswahl, Eingaben, Validierung, Bestätigung, unklarer Zustand; kein echter Versand an Schule während QA |
| B11 Benachrichtigungen/PWA | Postfach, einzeln/alle gelesen, Präferenzen, Push-Geräte, Installationshilfe, Service Worker | Präferenz-Teilprüfung und serverseitige Push-Nachweise | vollständige Kategorien, Geräteentzug, verweigerte Freigabe, echte Zustellung und Installation auf Zielgeräten |
| B12 Personen | Liste, Filter, Sortierung, Detail, Rollen | lokal abgeschlossen | nur Staging und betroffene Komponentenregression; keinen vollständigen Neubau starten |
| B13 Rollen/Rechte | eigene Rollenverwaltung, Berechtigungsmatrix, Geltungsbereiche | lokal abgeschlossen | dokumentierte unabhängige Fachrechte beachten; Staging und durch spätere Fachänderung betroffene Endpunkte |
| B14 Schulen/Klassen | Suche, Katalog-/Strukturimport, Export, Schuldetail, Klassendetail, Freigaben | Übersichtssmoke / Backendtests | ganze Kette anlegen/ändern/deaktivieren, fehlerhafter Import, Export/Wiederimport, F-01/N-01, Klassenisolation |
| B15 Adapter/Module | Definitionen, Anbieter, Instanzen, Module, Zugangstyp, Schul-/Klassenfreigaben | Backendtests und Übersicht | Definition → Schule → Klasse → Kind → Modulfunktion; ungültige Konfiguration, getrennte Freigabe-/Verbindungszustände |
| B16 Kontakte/Klassenleben | Adressliste, Schüler, Lehrkräfte, Lernportale, Speiseplan | mehrere Seiten-Smokes | Suche/Detail, Kontaktfreigaben, Direktchatberechtigung, datums-/kindbezogener Speiseplan, sichere externe Links |
| B17 Inhalte/Dokumente | Beiträge, Detail/Kommentare, Dokumentliste, geschütztes PDF/Formular | Backendtests; verborgener Kommentartext wird aktuell im Template unterdrückt | Erstellen/Bearbeiten/Veröffentlichen über vorgesehene Redaktion, Kommentar/Meldung/Rückzug, Dateizugriff/Entzug und Leerdaten |
| B18 Veranstaltungen | Liste/Detail, Neu/Bearbeiten/Löschen, Teilnahme, Umfrage, Mitbringlisten, Reservierung, Rezepte | Tests und Übersichtssmoke | vollständiger Veranstaltungsablauf, Menge/Frist/Doppelreservierung, F-01, Moderation freier Beiträge, externer Ausfall |
| B19 Fotos/Galerie | Schuljahr/Ereignis, Galerie, Upload, Zuordnung, Freigabe, Moderation, Rückfrage, geschützte Dateien | umfangreiche Backendtests; Übersichtssmoke | Raster/Fokus, Mehrfachupload, fehlende Einwilligung, Ersatzbild, Rückzug, Zugriffsentzug und leere/befüllte Ansichten |
| B20 Mobilität | Übersicht/Detail, Treffpunkte, Reaktion, Entscheidung, private Abholung, Widerruf, Moderation | Backendtests | komplette Bedienkette mit zwei Testkonten; private Adresse erst nach erlaubtem Schritt; mobile Kartenbedienung |
| B21 Photo Memory | Suche und Moderation, Aktivierung/Widerruf | Rollen-/Consent-Tests, eigene Modul-Templates | freigegebene synthetische Betriebszustände; Templates noch sehr einfache Überschriften/Listen, visuell anpassen; standardmäßig deaktiviert lassen |
| B22 Portalverwaltung | Bereichsmenü, Menüeditor, Registrierungen/Einladungen/QR, Familien-Einladungen, Pilotmeldungen, Terminumfrage | Seitensmokes | vollständige Formulare, Reihenfolge/Sichtbarkeit, Fehler/Abbrechen/Reload, Meldungsstatus/geschützter Screenshot, gültige Zielseiten |
| B23 Betrieb/Technik | Systemstatus, Monitoring/Konfiguration, automatische Abmeldung, Modellansicht/Graph/Export | Teilprüfungen und Templates | Speichern/Fehler/Abbrechen, Zugriffsschutz, Export und Zustände ohne Messdaten; keine Infrastrukturänderung im UI-Paket |
| B24 Design/Themes | Token-Editor, Katalog, Theme-Dialoge, persönliche Auswahl, Live-/Seitenvorschau | dokumentierte Vorschau-/Speicherprüfungen | F-02/F-03/V-01/V-03; veröffentlichte/ungewählte Themes, gültige Tokens, alle gemeinsamen Komponenten |
| B25 Technische Oberflächen | Django-Admin, Wagtail, APIs, Health, Manifest, Medien, WebDAV | eigenständige Systemflächen/Endpunkte | erreichbare Standardwege und Zugriffsschutz erfassen; Admin/CMS nicht mit Eltern-Portaldesign gleichsetzen, keine direkten privaten Medienpfade veröffentlichen |

## 6. Punkt 2: konkrete Reihenfolge und Modellzuordnung

Die Modellangaben sind eine Arbeitsaufteilung, keine Garantie für Dauer oder
Kontingentverbrauch und kein automatisch ausgeführter Modellwechsel.
Die konkrete Zuordnung ist eine projektbezogene Empfehlung. Die
[offizielle OpenAI-Modellübersicht](https://developers.openai.com/api/docs/models)
ordnet Astra komplexen Aufgaben und Sol dem Ausgleich von Leistungsfähigkeit
und Kosten zu; daraus folgt keine feste Ersparnis beim Codex-Plankontingent.

| Reihenfolge | Arbeitsblock | Empfohlene Einstellung | Fertig, wenn |
|---|---|---|---|
| 2a | F-01: gemeinsame Formularaktionen an den sechs benannten Stellen vervollständigen | **Sol Mittel** | Abbrechen/Speichern/Reload mit synthetischen Daten und Mobil/Desktop geprüft; je Seite konkreter Beleg |
| 2b | F-03/V-01/V-03: Token-Wirkung, kompakter Editor, Preset-Kontraste | Sol Mittel; Astra High nur bei ungelöster gemeinsamer CSS-Ursache oder Designentscheidung | Komponentenvergleich belegt; gültiger Entwurf unverbindlich, Abbrechen stellt Original her, Speichern wirkt nach Reload |
| 2c | N-01/C-01 und Zugangsdopplungen; begrenzte CSS-Konsolidierung aus F-02 | Sol Mittel | fachliche Rückwege und URL-Auflösung bestehen; nur die geänderten Komponenten nachgeprüft |
| 2d | Fehlende Journeys B01–B04, B08–B11 und B14–B23 seitenweise schließen | Sol Mittel | Bereichsabläufe mit passenden Rollen, Fehlern, befüllten Zuständen und responsiven Belegen abgeschlossen |
| 2e | Build-Zuordnung, Staging-Vergleich, echte Gerätefunktionen | Sol Mittel; Benutzeranmeldung/echtes Gerät soweit erforderlich | geprüfter Quellstand auf Staging identifiziert; offene Geräte-/Integrationspunkte belegbar erledigt oder ausdrücklich offen |
| 3 | Unabhängige Schlussbewertung gegen konkrete Mockups/Anforderungen | Astra High, gezielt | keine offenen Abnahmehindernisse; repräsentative Querverbindungen und visuelle Belege konsistent |

**Nächster Auftrag ist 2a mit Sol Mittel.** Er ist eng begrenzt und hat ein
prüfbares Ergebnis. Punkt 2 beginnt erst nach der vom Nutzer vorgesehenen
Modellentscheidung. Es wird keine weitere Gesamtanalyse vorgeschaltet.

## 7. Prüfen ohne endlose Nachläufe

- Pro Paket festhalten: geprüfter Stand, Rolle, Datensatzart, Schritte,
  Erwartung, Ergebnis, Bild-/Testbeleg, offene Abweichung. Historische Tests
  bleiben entsprechend datiert.
- Normale Fachseiten zunächst im bestätigten Basisdesign bei 360, 768 und
  1440 px. 1920 px gezielt bei breiten Arbeitsflächen und bereits bekannten
  Desktopproblemen. Lange Inhalte und volle Datenbestände ausdrücklich prüfen.
- Themes über einen gemeinsamen Komponentenvergleich abdecken. Nicht jede
  Fachseite unter jedem Theme und jedem Gerät vollständig neu durchspielen.
- Gemeinsame Änderungen lösen eine begrenzte Wirkungsprüfung aus: Formular-
  footer → betroffene Formulare; Tokens → Komponenten und repräsentative
  Fachseiten; Shell → Chat, Tabelle, Dialog und Navigation.
- Bestehende Personen-/Rollen-/Chatnachweise nur für veränderte oder unklare
  Zustände ergänzen. Ein wiederholter Lauf nennt vorher den konkreten Anlass.
- Nach erfolgreichem Paket den Abschluss dokumentieren und zum nächsten
  übergehen. Keine erneute flächige Prüfung ohne Änderung oder offenen Befund.
- Reale Konten, Nachrichten und Schuldaten werden nicht als Wegwerf-Testdaten
  benutzt. Geräteberechtigungen und echte externe Übermittlungen bleiben
  getrennte, ausdrücklich nachvollziehbare Prüfungen.

## 8. Abschluss dieses Analyseblocks

Geliefert sind eine aktuelle Bestandsbewertung, konkrete Befunde, die
vollständige Bereichsmatrix, ein Routen-/Templateinventar und die begrenzte
Reihenfolge für Punkt 2. Offen bleiben Umsetzung der Befunde und die benannten
Fach-, Staging-, Geräte- und Referenzprüfungen. Die Gesamtfreigabe wird daraus
nicht vorweggenommen.
