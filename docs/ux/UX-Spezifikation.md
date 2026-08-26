# UX-Spezifikation Klasse 5e

Status: verbindliches UX-Spezifikationsgate vor einer späteren UI-Überarbeitung.
Keine der beschriebenen Ansichten implementiert WebUntis, Wollino oder neue
Fachlogik. Siehe [Informationsarchitektur](Informationsarchitektur.md),
[Wireframes](Wireframes.md) und [Abnahmeszenarien](Abnahmeszenarien.md).

## 1. Leitbild und Prioritäten

Die Oberfläche wirkt freundlich, ruhig und modern: eine vertrauenswürdige
Klassenmappe, keine Unternehmenssoftware und kein kindliches Spielzeug.
Texte verwenden kurze deutsche Alltagssprache (`Foto melden`, `Zusage
zurücknehmen`). Kleine, bekannte Symbole unterstützen Text, ersetzen ihn aber
nie. Normale Mitglieder sehen keine technischen IDs, Pipelinewerte oder
Wagtail-Begriffe. Redaktion, Moderation und Systemadministration sind eigene
Arbeitsbereiche.

Kennzeichnung in diesem Dokument:

- **Muss:** für sichere, verständliche Alltagsnutzung erforderlich.
- **Soll:** hoher Nutzen, darf nach dem ersten responsiven Kern folgen.
- **Kann:** klarer Komfortgewinn; nur bei verbleibendem Aufwandsspielraum.
- **Später:** benötigt eine noch nicht freigegebene Quelle oder Fachphase.

`Kann` und `Später` werden nur mit genanntem Nutzen aufgenommen. Alles andere
wird gestrichen.

### Bestandsabgleich

Die Spezifikation wurde gegen die vorhandenen Module `core`, `content`,
`events`, `media`, `biometrics`, `chat` und `schedule`, deren URL-Routen,
Rollenpolicies und Datenmodelle geprüft. Aktuell existieren nur ein minimales
Basis-/Dashboard-/Offline-Template, Einladung, Galerie und zwei Biometrie-
Templates sowie eine kleine `app.css`; mehrere Fachrouten liefern derzeit
JSON. Die später umzusetzende Oberfläche darf diese Verträge nutzen, muss aber
weiterhin jede serverseitige Berechtigungsprüfung beibehalten. Die
Spezifikation erfindet keine neue Datenpersistenz und kennzeichnet noch nicht
vorhandene Quellinformationen ausdrücklich als `Später`.

## 2. Kleines visuelles Vokabular

Dies sind Gestaltungsgrenzen, keine allgemeine Komponentenbibliothek.

| Bereich | Vorgabe |
|---|---|
| Farben | **Muss:** warmes Off-White `#FAF8F3`, dunkles Tintenblau `#18324A`, ruhiges Primärblau `#28628A`, helles Kartenweiß. Statusfarben nur zusammen mit Symbol und Text: Grün Erfolg, Ocker Hinweis, Rot Fehler/Sperre, Grau inaktiv. Kontraste vor Umsetzung nach WCAG AA messen. |
| Schrift | **Muss:** Systemschrift; Grundtext mindestens 16 px/1,5, Nebeninfo 14 px, Seitentitel 28–32 px, Kartentitel 18–20 px. Textvergrößerung bis 200 % ohne Informationsverlust. |
| Abstände | **Muss:** 4-px-Raster; üblich 8/12/16/24/32 px. Touchziele mindestens 44×44 px, zwischen gefährlichen Aktionen ausreichend Abstand. |
| Karten | **Muss:** 12 px Innenabstand mobil, 16–20 px größer; dezenter Rand, 10–12 px Radius, Schatten nur sehr sparsam. Ganze Karte nur klickbar, wenn Fokus und Zweck eindeutig sind. |
| Status | **Muss:** Icon + kurzer Text (`✕ Entfällt`, `! Klärung nötig`), niemals Farbe allein. Statuschips sind nicht interaktiv, sofern sie nicht als Filter beschriftet sind. |
| Buttons | **Muss:** primär gefüllt, sekundär umrandet, tertiär als Textaktion; destruktiv rot und mit Bestätigung. Pro Abschnitt höchstens eine primäre Aktion. |
| Icons | **Soll:** kleiner konsistenter Satz für Start, Beitrag, Dokument, Kalender, Event, Essen, Chat, Foto, Person, Zustimmung, Glocke. Immer mit Text oder zugänglichem Namen. Keine rein dekorativen Emoji-Ketten. |
| Formulare | **Muss:** Label oberhalb, Hilfetext vor Fehlermeldung, Fehler direkt am Feld und als Zusammenfassung; Erfolg nicht nur per Toast. Pflichtfelder sprachlich erklären. |
| Bewegung | **Muss:** keine unnötigen Animationen; Statuswechsel höchstens kurz und unter `prefers-reduced-motion` ohne Bewegung. |

## 3. Responsive Rahmen

- **Muss – Smartphone hochkant:** primäre Alltagsansicht, eine Spalte, maximal
  zwei einfache Auswahlkacheln je Zeile. Untere Navigation mit `Start`,
  `Kalender`, `Chat`, `Mehr`; kontextuelle Hauptaktion gut mit einer Hand
  erreichbar, ohne Inhalte dauerhaft zu verdecken.
- **Muss – Smartphone quer:** keine Desktopnavigation erzwingen; kompakte
  untere Navigation, Karten bei ausreichender Breite zweispaltig.
- **Muss – Tablet:** zwei Spalten für Dashboard/Galerie, Inhaltsbreite etwa
  960 px; Navigation je nach Breite unten oder links.
- **Muss – Notebook/Desktop:** linke Navigation, Hauptinhalt maximal 1200 px;
  Lesetext maximal 70 Zeichen pro Zeile. Dashboard zwei bis drei Spalten,
  Fotogalerie drei bis fünf.
- **Muss – PWA/Browser:** gleiche Funktionen. Sichere Bereiche werden nicht
  dauerhaft offline gespeichert. Browser zeigt zusätzlich Installationshilfe,
  wenn unterstützt und sinnvoll.
- **Muss – Eingabe:** alles per Touch, Maus und Tastatur. Sichtbarer Fokus,
  logische Fokusreihenfolge, Sprunglink zum Inhalt, keine Hover-Pflicht.
- **Soll:** lange Titel nach zwei Zeilen umbrechen; niemals wichtige
  Statusinformationen abschneiden. Tabellen werden mobil zu beschrifteten
  Karten, nicht horizontal unlesbar zusammengeschoben.
- **Kann:** Swipe zwischen Tagen/Kategorien als Komfort; sichtbare
  Zurück-/Weiter- oder Tab-Schaltflächen bleiben immer vorhanden.
- **Kann:** Pull-to-refresh nur auf Dashboard, Kalender und Chat mit
  sichtbarer Aktualisieren-Schaltfläche als Alternative.

Zustände: Skeletons nur kurz und mit zugänglicher Ladeansage; danach klare
Leermeldung mit nächstem Schritt. Fehler nennen Auswirkung und sichere Aktion.
Bei langsamem Netz bleiben bereits sichtbare Daten stehen und tragen
`Wird aktualisiert`. Offline zeigt die PWA nur die neutrale Offline-Seite,
keine Profile, Chattexte oder Fotos aus einem dauerhaften Cache.

## 4. Dashboard

**Muss:** Begrüßung, gemeinsamer ausgewählter Schultag, kompakter Stundenplan,
kurzfristige Änderungen/Entfälle, nächste Prüfung, nächster Termin, offene
eigene Mitbringzusage, neue Beiträge und Chat-Ungelesenstatus. Karten verlinken
in das zuständige Fachmodul. Entfallene Stunden bleiben sichtbar.

**Später – Nutzen: täglicher Überblick aus freigegebenen Quellen:** Wollino-
Tagesmenü, WebUntis-Hausaufgaben und Synchronisationsstände. Sie erscheinen
nur mit synthetischen Daten in Wireframes und deutlich als `geplant`.

Zeitregel: Vor der konfigurierten Umschaltzeit (Planungsannahme 15:00 Uhr)
steht heute im Fokus, danach der nächste veröffentlichte tatsächliche
Schultag. Wochenenden, Ferien und unveröffentlichte Tage werden übersprungen.
Stundenplan und Essen teilen die Tagesauswahl, bleiben getrennte Karten.
Veraltete Quellen zeigen `Stand … · derzeit nicht aktualisierbar`; sie werden
nicht als aktuell ausgegeben. Siehe konkrete Hierarchie in den Wireframes.

## 5. Dokumente und Beiträge

### Dokumentencenter

- **Muss:** Kategorien, Suche nach Titel/Beschreibung, `Neu/Aktualisiert`,
  Datum, Version, Dateigröße, PDF-Symbol und eindeutige Aktion `PDF öffnen`.
  Original und ausfüllbare Variante sind getrennt beschriftet. Download bleibt
  über die geschützte Route; keine Medien-URL wird dargestellt.
- **Soll:** `Häufig verwendet` und `Aktuell` auf Basis minimierter, fachlich
  zulässiger Metadaten; Nutzen: schneller Zugriff auf wiederkehrende Formulare.
- **Muss:** leere Kategorie erklärt, wie der Filter zurückgesetzt wird;
  Downloadfehler bietet Wiederholen; fehlende Berechtigung erklärt neutral,
  dass Anmeldung oder Klassenmitgliedschaft fehlt; neue Version verweist auf
  den aktuellen Stand.
- **Kann:** Filterchips für Kategorie/Schuljahr; Nutzen: bessere Übersicht bei
  wachsendem Bestand.

### Aktuelles und Beiträge

- **Muss:** wichtig/angeheftet zuerst, danach chronologisch; Titel, Kategorie,
  Datum, kurzer Anriss, ungelesene Markierung. Lange Beiträge nutzen ruhige
  Lesebreite und klare Zwischenüberschriften.
- **Muss:** Autor wird nur als erlaubte, aus verifizierter Beziehung
  abgeleitete Familienbezeichnung angezeigt. Moderation kennt intern weiterhin
  das handelnde Konto.
- **Muss:** Kommentare zeigen Antworten, Bearbeitungsstand, `Zurückgezogen`
  beziehungsweise `Durch Moderation ausgeblendet`, Melden und bei Eigenanteil
  Bearbeiten/Zurückziehen. Geschlossene Themen erklären den gesperrten Editor.
- **Soll:** neue Kommentare seit letztem Besuch hervorheben; Nutzen: Anschluss
  an Diskussion ohne Echtzeitdruck.
- **Muss:** Content-Bearbeiter erhalten einen klar markierten
  `Bearbeitungsbereich`, niemals Konten- oder Rollenverwaltung.

## 6. Veranstaltungen und Mitbringlisten

Die Übersicht zeigt **Muss** Datum, Titel, Ort, eigenen Zusagestatus und offene
Mitbringpositionen. Das Detail ordnet Informationen: Termin → wichtige Hinweise
→ eigene Zusagen → Mitbringliste → Dokumente/Beitrag → Organisatoren.

Mitbringauswahl:

1. **Muss:** sichtbare Kategorien (`Brot`, `Brötchen`, `Salat`, `Obst`,
   `Getränke`, `Geschirr`, `Hilfe`) mit kleinem Icon und Text.
2. **Muss:** große Kacheln, mobil zwei je Zeile; Status `noch benötigt`,
   `vollständig`, `von mir reserviert`, `bereits vergeben` jeweils mit Text und
   Symbol. Nicht verfügbare Kacheln bleiben erklärend sichtbar.
3. **Soll:** tolerante Suche mit gepflegter kleiner Synonymliste, etwa
   Brötchen/Semmeln; Nutzen: schneller Treffer ohne allgemeine Suchplattform.
4. **Soll:** häufig und zuletzt von diesem Konto verwendete Einträge; Nutzen:
   weniger Schritte. Keine Familienprofile daraus ableiten.
5. **Muss:** Menge/Einheit vor verbindlicher Bestätigung, Zusammenfassung
   `Du reservierst 2 Flaschen Saft`, primär `Verbindlich reservieren`.
6. **Muss:** freie Beiträge mit Kategorie, kurzer Bezeichnung, Menge, Einheit
   und Bemerkung; Hinweis, dass Moderation möglich ist.
7. **Muss:** Erfolg dauerhaft in `Meine Zusagen` zeigen. Korrektur und
   Rücknahme verlangen Bestätigung. Abgelaufene Frist deaktiviert mit Datum.
8. **Muss:** Race-Konflikt erklärt `Gerade vollständig vergeben` und bietet
   aktualisierte Alternativen; keine stillen Doppel- oder Überbuchungen.
9. **Kann:** Swipe zwischen Kategorien; Nutzen: schneller Touch-Wechsel, Tabs
   bleiben sichtbar.

## 7. Kalender, Stundenplan, Hausaufgaben und Prüfungen

**Muss:** Phase-8-Tagesansicht mobil und Wochenansicht Desktop, mit sichtbaren
Vor/Zurück-Aktionen, Fach, Zeit, freigegebener Lehrkraftbezeichnung, Raum und
`zuletzt aktualisiert`. Status: `Regulär`, `↔ Änderung`, `⇄ Vertretung`,
`✕ Entfall`, `! Prüfung`, `+ Zusatzveranstaltung`, `▦ Ferien`, `i Information`.
Manuelle Daten tragen `Manuell gepflegt`.

**Später – Nutzen: weniger Doppelerfassung nach schriftlicher Freigabe:**
WebUntis-Quelle und Original-Link, synchronisierte Original-/Änderungswerte,
Hausaufgaben und Prüfungen. Ausschließlich synthetische Beispiele dienen der
Spezifikation. Unerreichbares WebUntis lässt den manuellen Plan bestehen und
zeigt Alter/Fehlerstatus.

Hausaufgaben werden `Bald fällig`, `Später fällig`, `Verpasst` zugeordnet;
`Erledigt` nur, wenn die Quelle dies eindeutig liefert. Detail: Fach,
Aufgaben-/Fälligkeitsdatum, freigegebene Lehrkraft und Aufgabentext.
Prüfungen zeigen Termin, Fach und Art. Beide sind nur für den verknüpften
Schüler und berechtigte Sorgepersonen sichtbar. Push nennt nur, dass es eine
Änderung gibt, nie Aufgaben- oder Prüfungstext.

## 8. Wollino-Speiseplan

**Später – Nutzen: schneller Tagesüberblick, erst nach separater Freigabe:**
Dashboard-Tageskarte und Seite `Aktuelle Menüpläne` verwenden nur die
Quellenspezifikation. Die Karte zeigt Datum, Menü 1/2, geordnete Bestandteile,
Allergen- und Zusatzstoffchips, aufklappbare Legende, Kalenderwoche,
Quellenangabe, letzten Abruf, Änderungsvorbehalt und `Original-PDF bei
Wollino`. Ein fehlender Tag springt zum nächsten veröffentlichten Essenstag.
Parsingfehler zeigt `Prüfung erforderlich` und ausschließlich den Original-
Link. Wochenkarten listen verfügbare Wochen; kein Menü wird erfunden.

## 9. Chat

- **Muss:** Raumübersicht mit Klassenraum, Eventräumen, ungelesener Anzahl und
  Stummstatus; keine Direktnachrichten und keine Anhänge.
- **Muss:** vertrauter vertikaler Verlauf, Antworten mit kurzem Bezug,
  tatsächliche/abgeleitete Autorenanzeige nach Sichtbarkeit, Bearbeitet,
  Zurückgezogen, Moderiert, Melden. Eigene Nachricht kann bearbeitet oder
  zurückgezogen werden.
- **Muss:** Pollingstatus `Aktualisiert`, `Verbindung unterbrochen – erneut
  versuchen`; bereits sichtbare Nachrichten bleiben lesbar. Push enthält
  keinen Nachrichtentext.
- **Soll:** Sprung zu erster ungelesener Nachricht; Nutzen: schneller
  Wiedereinstieg.
- **Kann:** automatisches Nachladen am Verlaufsanfang; Nutzen: lange Räume ohne
  große Erstübertragung.

## 10. Fotos und lokale Suche

**Muss:** Galerieübersicht/Eventbezug, privater Speicherhinweis, geschütztes
Raster, Detail, Melden, eigener Rückzug und Download nur bei aktueller
Freigabe. Upload führt durch Dateiauswahl → Personenangabe → Nutzungsregeln →
`Wird verarbeitet` → `Wartet auf Moderation`. Zustände erklären `Einwilligung
fehlt`, `widerrufen`, `Klärung nötig`, `nicht mehr verfügbar`; niemals Namen
auf dem Foto oder öffentliche URLs.

**Später/deaktiviert – Nutzen: freigegebene eigene Kinderfotos finden:**
separate Einwilligung, ausschließlich eigenes verknüpftes Kind, Verarbeitung
im selbst betriebenen Container, keine Cloud, Vorschläge statt Identifikation,
menschliche Bestätigung und vollständiger Widerruf/Löschung. Der Einstieg
trägt sichtbar `Nicht freigegeben` beziehungsweise `Deaktiviert` und darf nicht
wie eine verfügbare Alltagssuche wirken.

## 11. Lehrkräfte, Familie und Profile

- **Muss:** Lehrkraftkarte mit Name, freigegebenem Bild, Fächern und
  Klassenfunktion; E-Mail/Sprechzeit nur feldweise freigegeben.
- **Muss:** persönliches Elternprofil und Schülerprofile klar trennen.
  Sorgepersonen besitzen eigene Konten; kein `Als Kind anmelden`.
- **Muss:** mehrere Kinder, Haushalte und Sorgepersonen als verifizierte
  Beziehungen darstellen. Rechte werden je Beziehung erklärt; Nutzer können
  sie nicht als Freitext behaupten.
- **Muss:** Kontaktfelder standardmäßig nicht sichtbar; Telefon, E-Mail und
  Profilfoto je Feld mit aktueller Sichtbarkeit und direktem Link zur
  Einwilligung.
- **Soll:** Familienumschalter bei mehreren Kindern; Nutzen: eindeutig
  schülerbezogene Hausaufgaben/Prüfungen auswählen.

## 12. Einwilligungen

**Muss:** Übersicht in Themenkarten: Profildaten, Telefon, E-Mail,
Fotoanzeige, Foto-Upload, manuelle Benennung, biometrische Suche und Push.
Jede Entscheidung bleibt einzeln. Ein Dialog zeigt in dieser Reihenfolge:
`Worum geht es?`, `Wer kann es sehen?`, `Wie lange?`, `Was passiert bei
Widerruf?`, Textversion/Stand, dann gleichwertige Aktionen `Zustimmen` und
`Nicht zustimmen`. Widerruf ist direkt erreichbar und bestätigt die
unmittelbare Wirkung. Juristische Langfassung ist ergänzend aufklappbar.

Mehrere Sorgeberechtigte sehen ihren eigenen Entscheidungsstand und den
neutralen Gesamtstatus `Noch nicht vollständig`, `Widerspruch – Klärung nötig`
oder `Erlaubt`; fremde Detailentscheidungen werden nicht unnötig offengelegt.
Administratoren können fehlende Zustimmung nicht ersetzen.

## 13. Benachrichtigungen und Konto

**Muss:** getrennte Schalter für wichtige Klasseninformationen,
Veranstaltungen, Mitbringlisten, Chat, Stundenplanänderungen, Prüfungen,
Hausaufgaben und neue Galerien. Jeder Schalter erklärt ein datensparsames
Beispiel. Push ist freiwillig; Browserberechtigung wird erst nach bewusster
Aktion angefragt. Nach Ablehnung erscheint dauerhaft eine ruhige Anleitung in
den Einstellungen, kein wiederkehrender Dialog. Abmeldung ist vollständig und
idempotent. Hinweis: kein Notfallkanal und kein Zustellnachweis.

Das persönliche Konto bündelt E-Mail, Passwort/Passkey/TOTP, Sitzungen,
Benachrichtigungen und Abmelden. Sicherheitsaktionen stehen getrennt von
Profilfreigaben.

## 14. Bewusste Streichungen

- kein universelles Design-System, Theme-Builder oder Iconpaket ohne Bedarf;
- keine personalisierbaren Dashboard-Layouts (kein belastbarer MVP-Nutzen);
- keine versteckten Swipe-only-Aktionen oder dekorativen Animationen;
- keine Direktnachrichten, Chat-Anhänge oder Messenger-Nachbauten;
- keine öffentliche Medienansicht, Social Sharing oder Screenshot-Schutz-
  Versprechen;
- keine automatische Gesichtserkennung als Freigabeprüfung;
- kein WebUntis-/Wollino-Zugriff in diesem Gate.
