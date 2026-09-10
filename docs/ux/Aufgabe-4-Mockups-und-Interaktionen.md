# Aufgabe 4 – Seiten- und Formular-Mockups

Stand: 10.09.2026. Dieses Dokument ist der prüfbare Entwurf für das responsive Redesign. Es ersetzt keine serverseitige Berechtigung und beschreibt keine neue Fachlogik. Die unter [tailwind-playground-redesign.html](tailwind-playground-redesign.html) enthaltene Vorschau ist absichtlich statisch: Sie dient nur der Abstimmung von Informationshierarchie, Farbklima, Bedienung und Reaktionsverhalten.

## Farbdefinitionen

| Token | Wert | Verwendung |
|---|---:|---|
| `ink` | `#172033` | Überschriften, Navigation, Fokus auf hellem Grund |
| `canvas` | `#F5F7FB` | Seitenhintergrund |
| `surface` | `#FFFFFF` | Karten, Dialoge, Eingaben |
| `line` | `#DCE3F0` | ruhige Trennung von Bereichen |
| `primary` | `#3159D7` | genau eine Hauptaktion je Abschnitt |
| `primary-soft` | `#E8EDFF` | aktive Tabs, dezente Hervorhebung |
| `child-blue` | `#2374E1` | optionale Familienfarbe Kind 1 |
| `child-violet` | `#7A4DE8` | optionale Familienfarbe Kind 2 |
| `child-teal` | `#0F8B7B` | optionale Familienfarbe Kind 3 |
| `success` | `#087A4B` | Erfolg, nie ohne Textsymbol |
| `warning` | `#A55A00` | Klärung, ausstehende Prüfung |
| `danger` | `#C23737` | Sperren und irreversible Aktionen |

Die optionalen Kinderfarben markieren nur die Familienansicht von Sorgeberechtigten. Schüler sehen weiterhin die einheitliche Portalgestaltung. Jede Kombination braucht mindestens WCAG-AA-Kontrast; Status wird stets zusätzlich über Text und Symbol beschrieben.

**Bestätigte Grundlage (10.09.2026):** Das helle, ruhige Farbsystem ist das verbindliche Startdesign. Komponenten dürfen Farben, Flächen, Linien und Schatten ausschließlich über semantische Design-Tokens beziehen. Ein dunkles Design sowie später freigegebene Tailwind-Vorlagen werden als austauschbare Themes ergänzt; sie verändern weder Fachlogik noch Seitenstruktur.

## Gemeinsame Interaktionsregeln

- Mobile: untere Navigation mit `Start`, `Kalender`, `Chat`, `Mehr`; die aktuelle Hauptaktion sitzt innerhalb des erreichbaren Inhaltsbereichs oberhalb der Safe Area. Die Kontaktliste liegt unter `Mehr`.
- Ab 1024 px: linke Navigation mit `Start`, `Kalender`, `Chat`, `Kontaktliste`, `Familie`, `Fotos` und `Mehr`; Hauptinhalt maximal 1200 px. Die mobile Leiste verschwindet.
- Buttons sind mindestens 44 × 44 px. `Primär` ist gefüllt, `Sekundär` umrandet, `Tertiär` eine Textaktion. Destruktive Aktionen brauchen ein Bestätigungsdialogfenster.
- Hover hebt auf Desktop Karte oder Button 2 px an und verstärkt den Schatten. Fokus nutzt einen 3-px-Ring; `prefers-reduced-motion` deaktiviert Höhenbewegung und Carousel-Autoplay.
- Dialoge blenden mit 150 ms ein. Escape, Klick auf Schließen und sichtbarer Abbrechen-Button schließen sie. Der Fokus beginnt im Dialogtitel und bleibt darin.
- Formulare zeigen Label, Hilfetext, Feldfehler und Erfolgszustand direkt am Feld. Speichern bleibt sichtbar, bis die serverseitige Antwort vorliegt.

## 1. Shell, Dashboard und Benachrichtigungen

**Ziel:** In höchstens drei Entscheidungen zu Tagesplan, Chat, wichtigen Änderungen oder dem passenden Kind gelangen.

| Element | Wirkung | Ziel |
|---|---|---|
| Kind-Kontext `Mila · THG 5e` | Dropdown mit Familienansicht und Kindern, Auswahl per POST | `/familie/ansicht/<student_id>/` |
| Nachrichten-Zähler | separates Postfach; zählt keine Systemwarnungen | `/chat/` bzw. Raumübersicht |
| Glocken-Zähler | separate wichtige Änderungen | `/benachrichtigungen/` |
| Tageskarte | leichte Anhebung bei Hover, ganzer Bereich fokussierbar; jede Stunde zeigt Uhrzeit, Fach, Lehrkraft und Raum | Kalender/Stundenplan |
| `Alle Aufgaben` | sekundäre Aktion | `/mehr/webuntis/` oder Aufgabenansicht |

**Bestätigter Kopfbereich:** Nachrichten und Benachrichtigungen sind zwei getrennte, gleich große Icon-Buttons mit lesbarem Zähler. Nachrichtenzähler öffnen die Chatübersicht; die Glocke öffnet ausschließlich die Systembenachrichtigungen. Das Profil zeigt ein hochgeladenes Foto, sonst die Initialen, und öffnet das persönliche Menü. Der Kind-Kontext erscheint als beschriftete Auswahl: auf Desktop als Dropdown, auf Mobilgeräten als Bottom Sheet. Er wird nur gezeigt, wenn die aktuelle Seite tatsächlich familien- oder kindbezogene Daten steuert.

## 2. Familienzentrale und Avatar

**Ziel:** Erwachsene bearbeiten ihr eigenes Profil, Kinder werden über eindeutige Tabs getrennt gepflegt.

| Element | Wirkung | Ziel |
|---|---|---|
| Tab `Mila` | Die am Kind gespeicherte Familienfarbe färbt den aktiven Tab vollflächig; inaktive Kind-Tabs zeigen dieselbe Farbe als helle Fläche. Name, aktiver Zustand und Fokus bleiben zusätzlich eindeutig; keine Datenmischung. | `?tab=data&child=<relationship_id>` |
| `Stammdaten` / `Freigaben` / `Schulzugänge` | ruhige Segment-Tabs; `Freigaben` umfasst kindbezogene Einwilligungen; aktiver Tab nur als ein klarer Fokus | jeweilige Query-Route in `/familie/` |
| `Avatar gestalten` | Modal mit großer Vorschau; Auswahl bleibt unverbindlich bis `Übernehmen` | Dialog `#avatar-designer` |
| `Profilfoto` | native Dateiauswahl und lokale Vorschau; Speicherung erst mit Formular | gleiche Formularroute `/familie/` |
| Sichtbarkeitsschalter | Text „Im Portal anzeigen“, keine Symbol-only-Schalter | Speicherung mit Profilformular |
| `Angaben speichern` | primär; Ladezustand, dann feldnahe Erfolgsmeldung | POST `/familie/` |

Der Avatar-Designer verwendet eine große, schrittweise Auswahl. **Pose** ist die erste Kategorie und beginnt mit `stehend` oder `sitzend`. Sie bestimmt die geometrisch passende vollständige SVG-Vorlage. Erst danach folgen kompatible Kategorien wie Haare, Gesicht, Kleidung, Accessoires und Hintergrund. Der v3-Assetkatalog kombiniert ausschließlich nachweislich passende Vorlagen und Bausteine; das verhindert kaputte oder abgeschnittene Avatare.

**Sichtbarkeit persönlicher Kontaktdaten:** Erwachsene verwalten Adresse, E-Mail-Adresse und Telefonnummer direkt in ihrem jeweiligen Stammdatenformular. Jedes Feld besitzt dort einen beschrifteten Schalter `Im Portal sichtbar` beziehungsweise `Ausblenden`; der Standard ist sichtbar. Es gibt keine getrennte Datenschutzseite für diese drei Felder. Der Kind-Tab heißt `Freigaben` und enthält ausschließlich kindbezogene Einwilligungen und Freigaben.

## 3. Schulzugänge

**Ziel:** Schule und Familie sehen nur die für das jeweilige Kind relevanten Informationen; Eltern tippen keine technische Schulkennung ein.

| Element | Wirkung | Ziel |
|---|---|---|
| Adapterkarte `WebUntis` | Schule, Portaladresse und Status sind lesbar; technische IDs bleiben im Verwaltungsbereich | Detail im Kind-Tab `Schulzugänge` |
| Zugang aktiv | beschrifteter Schalter direkt in der Adapterkarte. `Aktiv` zeigt Grün plus Text, `Inaktiv` neutrales Grau plus Text; er aktiviert oder pausiert Abruf und Darstellung, löscht aber keine gespeicherten Zugangsdaten. | POST Modulverbindung |
| Zugangsdatenformular | Passwort bleibt maskiert, Augen-Icon nur lokal; keine Werte nach Speicherung ausgeben | POST `/mehr/webuntis/` |
| `Verbindung prüfen` | neutraler Ladezustand „Prüfung läuft“, keine Zugangsdaten/Serverfehler ausgeben | POST WebUntis-Prüfung |
| `Verbindung entfernen` | roter Bestätigungsdialog mit Folge „lokale Daten werden getrennt“ | POST WebUntis-Löschung |

## 4. Galerie, Ereignis und Upload

**Ziel:** Erst Schuljahr/Ereignis wählen, dann Bilder hochladen; Event und Reviewstatus bleiben in jeder Ansicht sichtbar.

| Element | Wirkung | Ziel |
|---|---|---|
| Schuljahrkarte | Hover vergrößert nicht den Inhalt, sondern verstärkt nur Rand/Schatten; klarer Tastaturfokus | Galerieübersicht nach Schuljahr |
| Ereigniskachel | zeigt Kategorie, Titel, Bildanzahl und Status; ganzer Kachelbereich ist Link | `/galleries/<id>/` |
| Filter `Mein Kind` | schaltet nur die Ansicht, nie Berechtigungen | Query-Filter der Galerie |
| Raster / Fokusansicht | Raster ist Standard; Fokusansicht per sichtbarer Taste, Pfeile/Wischen; Autoplay immer aus | clientseitige Ansichtswahl |
| `Fotos hochladen` | Dialog mit Ereigniskontext, Mehrfachdatei, Beschreibung und Personenangabe | POST `/galleries/<id>/upload/` |
| `Erneut prüfen lassen` | nur für eigene erste Rückfrage bis Frist; Ersatzbild optional | POST `/photos/<id>/resubmit/` |
| Download | zunächst nicht anzeigen; erst nach eigenständiger Freigabe und Audit-Entscheidung | späterer, protokollierter Downloadpfad |

**Bestätigter Galerieaufbau:** Die Übersicht gliedert zuerst nach Schuljahr und darin nach Ereigniskacheln. Ein Ereignis öffnet seine eigene Galerie mit Raster als Standard und einer bewusst wählbaren Fokusansicht. Kacheln verstärken bei Hover nur Schatten und Rand, ohne das Layout zu verschieben. `Mein Kind` ist ein reiner Ansichtsfilter; Downloads bleiben bis zu einer eigenen Freigabe verborgen.

## 5. Formulare, Fehler und destruktive Aktionen

| Fall | Darstellung | Aktion |
|---|---|---|
| Pflichtfeld fehlt | rote Kurzmeldung direkt unter Eingabe, Fokus auf erstes Feld | keine Navigation |
| Netzwerkfehler | bestehende Eingabe erhalten, Banner mit `Erneut versuchen` | erneuter POST |
| Foto in Klärung | ockerfarbener Status, Frist mit Datum/Uhrzeit, kein permanenter Alarm | Ersatz/erneute Prüfung |
| Foto final abgelehnt | neutrale Erklärung, Datei nicht mehr abrufbar | keine Wiederholung |
| Verbindung entfernen | Dialog mit Name des Kindes, Folgen und `Abbrechen` als Standardfokus | nur bestätigter POST |

**Bestätigter Formularstandard:** Felder zeigen Label, Hilfetext und Fehler direkt am Feld. Eingaben bleiben während Speichern und bei Netzwerkfehlern erhalten. Pro Formular gibt es genau eine gefüllte Hauptaktion; Passwortfelder erhalten ein lokales Augen-Icon. Nur irreversible oder folgenreiche Aktionen öffnen einen Bestätigungsdialog. Reversible Ein-/Aus-Schalter werden unmittelbar, mit klarer Statusrückmeldung gespeichert.

## 6. Erster Login und Orientierung

**Bestätigter Ablauf:** Nach dem ersten Login erscheint eine kurze, nicht blockierende Willkommensseite. Sie zeigt nur die für Rolle und Konto noch offenen Schritte: Profil prüfen, Familie oder Kind auswählen, Freigaben ansehen sowie optional Benachrichtigungen aktivieren. `Zum Dashboard` bleibt jederzeit verfügbar. Erledigte Schritte werden bestätigt; offene Punkte erscheinen danach nur noch als zurückhaltende Dashboard-Karte.

Ist eine veröffentlichte Portalvorstellung vorhanden, ergänzt die Seite diese Karte:

> **Fragen zum Portal?** In mehreren Vorstellungsterminen zeigen wir KlassID und sammeln eure Fragen und Anregungen. Den passenden Termin findest du in den Veranstaltungen.

`Termine ansehen` führt zur jeweiligen veröffentlichten Portalvorstellung. Ohne veröffentlichten Termin wird die Karte nicht gerendert.

## 7. Abwesenheiten

**Bestätigter Ablauf:** Abwesenheiten sind pro Kind sichtbar. Die vollständige Liste und `Abwesenheit melden` liegen unter `Mehr`; aktuelle Einträge erscheinen zusätzlich als kompakte Karte im Dashboard und im Kalenderkontext des gewählten Kindes. Importierte Einträge zeigen Zeitraum, Uhrzeit, Status und Abrufzeit, jedoch keine Lehrkraft oder Ursache, wenn WebUntis diese Metadaten nicht liefert. Eine neue importierte Abwesenheit kann als eigene In-App-Benachrichtigung erscheinen. Eltern erfassen Meldungen ausschließlich für ihre eigenen berechtigten Kinder; die endgültige WebUntis-Meldung beginnt nur nach ausdrücklichem Absenden und anschließender Rückprüfung.

## Abnahmekriterien für den Mockup-Block

1. Alle wichtigen Interaktionen sind ohne Hover, nur per Tastatur und auf einem 360-px-Smartphone erreichbar.
2. Pro Abschnitt ist höchstens eine gefüllte Hauptaktion sichtbar.
3. Jede beschriftete Aktion besitzt ein konkretes Ziel oder ist ausdrücklich ein lokaler Dialog.
4. Kinderkontext, Nachrichten und Systembenachrichtigungen sind getrennt erkennbar.
5. Kein Mockup zeigt Passwort, technische Kennung oder direkte Medien-URL.
6. Die Tailwind-Vorschau folgt denselben Farben, Radien, Größen und Schaltflächenhierarchien.
