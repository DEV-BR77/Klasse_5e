# Vollständiger Portal-Neuaufbau – laufende Abnahme

Status: **in Arbeit, nicht abgenommen**. Die Beispiele des Auftraggebers
begrenzen den Auftrag nicht. Maßgeblich sind `UI Neuausrichtung von KlassID.md`
und `Aufgabe-4-Mockups-und-Interaktionen.md`; neuere Nutzeranweisungen haben
Vorrang (insbesondere keine Hover-Bewegungen, gemeinsame Rücknavigation,
Abbrechen links und Speichern rechts).

## Verbindliche Reihenfolge des Gesamtauftrags

1. Astra: Bestandsaufnahme und verbindlicher Umsetzungsplan.
2. Astra: gemeinsames Designsystem und Seitenstruktur.
3. Astra: Chat.
4. Astra: Personen-, Rollen- und Berechtigungsverwaltung.
5. Sol: Avatar-Designer und kleinere Fachseiten.
6. Astra: vollständige Browser-Abnahme und Korrekturschleifen **aller** Seiten.
7. Sol: Tests, technische Bereinigung und Abschlussbericht.
8. Astra: finale unabhängige Abnahme gegen Mockups und Anforderungen.

Die Modellzuordnung ist die vereinbarte Arbeitsaufteilung, kein Nachweis eines
automatisch erfolgten Modellwechsels. Vorgezogene Arbeiten schließen keinen
Block ab. Der Seitenumfang umfasst auch die unten aufgeführten Fachbereiche.

Zuletzt lokal geprüfte Teilaufträge: tatsächliche Zugriffswirkung der Rollenrechte
aus Punkt 4, Chat einschließlich Grafik-Sticker aus Punkt 3 sowie Avatar und
Profil-Unterseiten aus Punkt 5 (27.09.2026). Echte Gerätefunktionen und
Staging-Abnahme bleiben offen.
Die Gesamtpunkte 1–8 sind nicht insgesamt abgenommen.

### Chat-Prüfschritt vom 27.09.2026

- Die Zielgruppe wird jetzt auch beim Hinzufügen von Raummitgliedern geprüft;
  lokale Moderatoren benötigen tatsächlichen Raumzugriff. Erwähnungen dürfen
  keine für den Raum unberechtigten Konten benachrichtigen.
- Das Entfernen des letzten expliziten Mitglieds öffnet den Raum nicht mehr
  unbemerkt für die gesamte Zielgruppe. Dafür gibt es nun eine getrennte,
  bestätigungspflichtige Aktion „Mitgliederauswahl aufheben“.
- Sticker-Auswahl auf schmalen Bildschirmen visuell korrigiert; die vorhandenen
  Katalogeinträge bleiben weiterhin Text-/Asset-Kennungen, keine Bild-Sticker.
- 11 gezielte Mitglieder-/Asset-Tests und 26 Chat-Sicherheits-/Phase-7-/Portaltests
  bestanden. Der isolierte Browserlauf bestand bei 360, 768 und 1440 px mit
  Senden, simuliertem Netzfehler, Bearbeiten, Emoji-/Sticker-Auswahl, sichtbaren
  Nachrichtenaktionen und ohne JS-Fehler oder horizontales Überlaufen.
- Eine weitere isolierte Browser-Klickstrecke bestand bei 360, 768, 1440 und
  1920 px: Raum anlegen/bearbeiten/archivieren/löschen, Mitglied hinzufügen,
  ungewolltes Öffnen durch Einzelentfernung verhindern, Auswahl ausdrücklich
  aufheben, Nachricht senden/melden/moderieren und PDF-Anhang geschützt abrufen.
  Dabei wurde ein echter Bedienfehler behoben: Der Moderations-POST lieferte
  zuvor 204 ohne Seitenaktualisierung; das Raumformular leitet jetzt zurück.
- **Keine vollständige Chat-Abnahme:** Bild-Sticker sind weiterhin nur
  Text-/Asset-Kennungen. Sprachaufnahme, Bildanhang, Push-Zustellung und
  Aufbewahrungsjob sind nicht als Browserstrecke abgenommen. Der Staging-Login
  ist abgelaufen; auf Staging wurde weder geändert noch geprüft. Die
  Gesamt-Abnahme aller Seiten bleibt offen.

## Laufende Nachweise – lokal, nicht auf Staging ausgerollt

- 21 gezielte Backendtests für Familienkontext, Theme-Katalog, Vorschau,
  ausdrückliche Übernahme, Token-Editor und vorhandene Redesign-Verträge bestanden.
- Browserdurchlauf bei 360, 768 und 1440 px: Seitenaufrufe, acht Theme-Vorschauen
  mit Abbrechen, Theme-Übernahme und Reload, Token-Bearbeitung und Reload bestanden.
- Familienauswahl auf Dropdown/ausklappbare mobile Auswahl umgestellt;
  tatsächlicher Wechsel Kind/Gesamtansicht, Escape, unveränderte Position des
  Inhalts und vollständig sichtbarer Auswahlbereich geprüft.
- Fehler gefunden und korrigiert: Header-Unschärfe verschob den mobilen
  Auswahlbereich aus dem Viewport. Der Browsercheck prüft nun die Geometrie.
- Aufgeklappte Einstellungsgruppen bleiben bei Klicks außerhalb offen.
- Theme-Auswahl, Vorschau und Speicherung nutzen denselben verfügbaren Katalog.
  Nicht passende Zielgruppen und unveröffentlichte Themes werden für normale
  Konten sowohl in der Vorschau als auch beim direkten Speicheraufruf abgewiesen.
- Rahmenfarben werden aus dem Theme abgeleitet und auch im Editor aktualisiert.

- Erweiterter Browserdurchlauf bei allen drei Breiten bestanden: Nachricht nach
  simuliertem Netzfehler erneut senden, bearbeiten und erneut laden; Personenkarte
  über den tatsächlichen Listenlink öffnen und über Zurück zur Liste wechseln.
- Theme-Verwaltung verwendet nun die Validierung des Token-Editors. Ungültige
  Eingaben bleiben in einer gebundenen Fehleransicht erhalten und verändern die
  Datenbank nicht. 17 gezielte Theme-/Redesigntests bestanden (einschließlich
  ungültigem Schattenwert und anschließend erfolgreicher Korrektur).
- Gemeinsame Aktionszeile für persönliche Stammdaten, Profilbild,
  Benachrichtigungspräferenzen, Kinderstammdaten und Schulzugänge ergänzt.
  Abbrechen lädt den gespeicherten Stand per GET; Speichern bleibt rechts.
- 26 gezielte Profil-/Familien-/Redesigntests bestanden. Der abschließende
  Browserdurchlauf bei 360/768/1440 px enthält zusätzlich das Ändern und
  Abbrechen persönlicher Stammdaten und ist bestanden.
- Fokus- sowie Erfolgs-, Warnungs- und Fehlerfarben sind in der gemeinsamen
  Token-Schicht definiert. Der lokale Tailwind-Build ist erfolgreich.

Diese Nachweise sind Teilprüfungen. Vollständige visuelle Abnahme, alle weiteren
Fachabläufe sowie Staging-Abnahme sind weiterhin offen. Die Browserprüfung des
Theme-Fehlerformulars einschließlich Korrektur und erfolgreichem Speichern ist
bei allen drei Breiten bestanden. Die dabei absichtlich erzeugten HTTP-400-
Antworten sind erwartete Validierungsfehler.

## Seitenmatrix

### Rollenverwaltung und Rollenberechtigungen – lokal abgeschlossen am 27.09.2026

- Rollenverwaltung: Formularfehler bleiben sichtbar, gespeicherte Zuweisungen
  lassen sich direkt und nach Bestätigung entziehen. Elternvertreter-Chat
  wurde verbunden und wieder gelöst; Abbrechen lädt den gespeicherten Stand.
- Berechtigungsmatrix: Rollenwechsel, aufklappbare Module, einzelne Aktionen,
  Geltungsbereich, Speichern, erneutes Laden und Abbrechen geprüft. Ungültige
  Rollen, fehlende Felder und ungültige Geltungsbereiche verändern keine Rechte.
  Änderungen einer Rolle werden atomar gespeichert; partielle Altaufrufe
  lassen nicht übermittelte Berechtigungen unverändert.
- 29 zugehörige Backendtests sowie der gezielte Browserdurchlauf bei
  360/768/1440/1920 px bestanden. Django-Systemprüfung ohne Befund.
- **Zugriffswirkung angeschlossen:** Die gespeicherte Matrix wird in Chat,
  Veranstaltungen, Kalender, Galerie, Photo Memory, Mobilität und Dokumenten
  ausgewertet. Unterstützte Aktionen, Voraussetzungen und die weiterhin
  eigenständigen Mitgliedschafts-/Familienrechte sind in
  [Rollenrechte im laufenden Portal](../Rollenrechte-Laufzeit.md) beschrieben.
- Sichtbare Aktionen und direkte Schreibaufrufe prüfen dieselben Fachrechte.
  Raum-Bearbeitung kann das Archivierungsrecht nicht umgehen. Abgelaufene
  Klassenmitglieder können nicht neu in einen Chat aufgenommen werden.
  Auch Dokumentübersicht, Terminumfrage und Kalender-Wochenabruf prüfen
  rollenbezogene Leserechte. Die Rollenadministration bleibt nach dem Entzug
  eines Fachmodulrechts erreichbar.
- Der Editor zeigt nur angeschlossene Aktionen; persönliche Module erklären
  ihre eigenen Freigaben. Der ausführliche Hinweis zur Rechtewirkung ist
  aufklappbar. Screenshots der mobilen und Desktopansicht wurden angesehen.
- Abschlussnachweis: 111 unterschiedliche relevante Backendtests bestanden
  über Haupt- und gezielte Nachläufe. Der Hauptlauf umfasste 108 Tests
  (107 bestanden, ein Fehler im neuen PDF-Test durch vorzeitiges Schließen der
  Testantwort). Nach den abschließenden Leserechtskorrekturen und drei zusätzlichen
  Testfällen: 50 bestandene Tests im Nachlauf; der korrigierte PDF-Einzeltest
  anschließend bestanden. Kein erneuter vollständiger Portallauf.
- Browser erneut bei 360/768/1440/1920 px bestanden: Rollen zuweisen/entziehen,
  Elternvertreter-Chat verbinden/lösen, Rollenwechsel, Module aufklappen,
  Geltungsbereich ändern, speichern, neu laden und abbrechen. Eine separate
  Benutzersitzung prüft das Ein- und Ausblenden von „Neuen Raum anlegen“ nach
  Freigabe/Entzug. Keine erfassten JavaScriptfehler oder geprüften Seitenüberläufe.
  Django-Systemprüfung ohne Befund. Lokale Bilder: `.qa-current/role-*-final-*.png`
  und `.qa-current/role-effect-chat-*.png`.
- Die acht früheren Fehler aus dem Rollenrechte-Testlauf sind behoben. Tests
  für Galerie und Mobilität vergeben erforderliche Rechte ausdrücklich und
  prüfen auch die Ablehnung ohne Freigabe. Photo Memory wird ausschließlich
  in der synthetischen Testklasse aktiviert; sein Betriebsstandard bleibt aus.
- Alles nur lokal; Staging ist nicht ausgerollt.

### Personenverwaltung – lokal abgeschlossen am 27.09.2026

- Eigene Personendetailansicht statt Rücksprung in die Personenliste; Zurück und
  Abbrechen erhalten die gesetzten Filter. Suche, Schule, Klasse, Rolle und
  Kontostatus wurden mit synthetischen Konten durchgespielt.
- Tabellenüberschriften sortieren auf Desktop; in der mobilen Kartenansicht
  ist dieselbe Sortierung über eine sichtbare Auswahl bedienbar. Leere
  Suchergebnisse erhalten eine eigene Rückmeldung.
- Rollenzuweisung und Entziehen, ungültige Schul-/Klassenkombination,
  abgelaufene Zugehörigkeit, gesperrte Konten und unzulässige Rollenaktionen
  wurden geprüft. 28 zugehörige Backendtests bestanden.
- Gezielter Browserdurchlauf bei 360, 768, 1440 und 1920 px bestanden;
  Listen- und Detailansichten nach den Korrekturen als Screenshots geprüft.
  Keine horizontalen Überläufe oder erfassten JavaScriptfehler.
- Abnahme gilt für die lokale Personenverwaltung. Die Staging-Version ist
  noch nicht ausgerollt; die vollständige Portalabnahme bleibt offen.

### Nachprüfung 26.09.2026 – gemeinsame Formulare und Chatkatalog

- ChatAssetForm validiert Typ, Pflichtfelder, Maximallängen, Position und
  eindeutige Typ-/Namenskombinationen. Fehler zeigen den gebundenen Entwurf
  mit Feldmeldungen; die Datenbank bleibt unverändert. Unbekannte Aktionen
  werden abgewiesen. Keine stille Kürzung oder Ersetzung ungültiger Positionen.
- Katalogdialoge liegen außerhalb der Tabelle. Neues Element sowie
  Fehlerkorrektur verwenden gemeinsame Abbrechen-/Speichern-Aktionen.
- 18 gezielte Chat-/Redesign-Tests bestanden. Drei Browserdurchläufe bei
  360/768/1440 px bestanden, einschließlich Abbrechen, ungültiger Position,
  Korrektur, Speicherung und erneutem Öffnen. Erwartete HTTP-400-Antworten
  sind Teil der Prüfung. Keine erfassten JavaScriptfehler oder Seitenüberläufe.
- Dritter Browserdurchlauf prüft Abbrechen und direktes Wiederöffnen ohne
  Reload sowie die Rückgabe des Tastaturfokus an den auslösenden Button.
- Gesamtsuite: 367 bestanden, ein zeitabhängiger Test fehlgeschlagen
  (368 Tests; schneller Passwort-Hasher ausschließlich im Testprozess).
  Ursache: Schuldatentest erzeugte Unterricht für heute, das Dashboard wählte
  am Wochenende ohne explizites Datum den nächsten Schultag. Der Zugriffstest
  verwendet jetzt sowohl für erlaubten als auch gesperrten Zugriff ausdrücklich
  den Tag der Testdaten. Danach bestanden alle 31 Tests aus Schulzugriff,
  Dashboard/Kalender, Chatkatalog, Redesign-Verträgen und Phase 7 mit dem
  normalen Passwort-Hasher. Kein erneuter vollständiger Gesamtlauf nach dieser
  reinen Testkorrektur; keine Änderung der Zugriffspolicy.
- Django-Systemprüfung: keine Probleme gemeldet.
- Sichtprüfung führte zu einer zweiten Korrekturschleife: kompakte Feldabstände
  im Fehlerformular und einheitliche beschriftete Kontrollkästchen statt
  übergroßer Checkboxen. Lokaler Tailwind-Build erfolgreich; neue Screenshots
  anschließend angesehen. Nachweise liegen lokal unter `.qa-current/`.
- Falsche Aussage zur Chat-Aufbewahrung berichtigt: Aktivieren kann auch
  ältere Bestandsnachrichten entfernen. Die bestehende Löschlogik wurde nicht
  verändert, keine Nachrichten oder echten Einstellungen wurden gelöscht.
- Gesamtauftrag und Staging-Abnahme bleiben offen. Die Arbeit ist weiterhin
  lokal; insbesondere Bild-Sticker, sämtliche übrigen Fachabläufe und alle
  Theme-/Kontrastzustände sind damit nicht vollständig abgenommen.

### Nachprüfung 27.09.2026 – Chat-Restfunktionen (lokal)

- Grafik-Sticker können im Verwaltungskatalog als PNG/JPEG/WebP hochgeladen
  werden. Der Server begrenzt Größe und Pixelzahl, verwirft Animationen und
  kodiert das Bild als metadatenfreies PNG neu. Der geschützte Bildabruf
  erfordert Chat-Zugriff; fehlende Dateien liefern 404. Bereits versendete
  Sticker bleiben auch nach Deaktivierung sichtbar, können aber nicht erneut
  gesendet, gelöscht oder mit einem anderen Bild überschrieben werden.
- Ein Grafik-Sticker lässt sich ohne Nachrichtentext auswählen und senden.
  Desktop- und Mobilansicht wurden im synthetischen Browserlauf bei
  360/768/1440/1920 px nach Erstellen, Anhängen, Moderieren, Sticker-Senden,
  Bearbeiten, Archivieren und Löschen angesehen. Kein horizontaler Überlauf.
- Die Sprachaufnahme wurde mit simulierter MediaRecorder-Schnittstelle bis
  zum gespeicherten Audio-Anhang sowie für verweigerte Mikrofonfreigabe
  durchgeklickt. Ein reales Mikrofon, Audioqualität und echte Push-Zustellung
  wurden damit **nicht** geprüft. Für Push existieren serverseitige Tests zum
  neutralen Inhalt und Opt-in; die Aufbewahrung hat Tests für deaktivierte
  und aktivierte Löschung. 25 gezielte Tests aus Chatkatalog, Privatnachrichten
  und Phase 7 bestanden. Django-Systemprüfung ohne Befund.
- Diese lokale Teilprüfung ist keine Staging- oder Gesamtabnahme. Die weiteren
  Seiten und vollständigen Anforderungs-/Mockup-Vergleiche bleiben offen.

### Nachprüfung 27.09.2026 – Avatar und Profil-Unterseiten (lokal)

- Der Avatar-Designer wurde mit beiden vollständigen Posen „Stehend“ und
  „Sitzend“ durchgeklickt: Kategorien wechseln, Vorschau, Abbrechen ohne
  Datenänderung, Übernehmen, Profilformular speichern und erneut öffnen.
  Der Ablauf funktioniert im eigenen Profil und im Kinderprofil; gespeicherte
  `v3`-Auswahl wird serverseitig als vollständige SVG-Figur gerendert.
- Der mobile Dialog hatte zunächst eine abgeschnittene Aktionsleiste. Nach
  Layoutkorrektur bleiben Vorschau und Optionen scrollbar, während Abbrechen,
  Zufällig und Übernehmen bei 360 px vollständig sichtbar sind. Screenshots
  bei 360/768/1440/1920 px wurden erneut geprüft, ohne horizontalen Überlauf
  oder erfasste JavaScriptfehler.
- Profil-Stammdaten: Abbrechen verwirft den Entwurf, Speichern erhält den Wert
  nach erneutem Laden. Eine In-App-Benachrichtigungseinstellung wurde über den
  sichtbaren Schalter geändert, gespeichert und erneut geprüft. Design-/Theme-,
  App-Hilfe- und Sicherheits-Tab wurden auf Erreichbarkeit und Überlauf geprüft,
  nicht vollständig fachlich abgenommen. 26 Profil-, Familien- und
  Vertragsprüfungen sowie zwei neue Pose-Speichertests bestanden.
- Diese Prüfung nutzt ausschließlich synthetische lokale Daten. Staging,
  echte Geräte sowie der vollständige Profil-/Familienumfang bleiben offen.

| Bereich | Seiten und vollständige Bedienabläufe | Stand |
|---|---|---|
| Gemeinsame Oberfläche | Header, Navigation, Kontext, Tabellen, Formulare, Dialoge, Fokus, mobile Bedienung | in Überarbeitung |
| Zugang | Login, Registrierung, Einladung, Passwort vergessen/ändern, MFA, Timeout, Logout | offen |
| Einstieg | Orientierung, Start, Kinderwechsel, Tageswechsel, Aufgabenstatus, leere Zustände | offen |
| Kalender | Tag/Woche/Monat, Filter, Datum, Ereignisdetail, Synchronisation | offen |
| Kommunikation | Räume anlegen/bearbeiten/archivieren/löschen, Mitglieder, Nachrichten, Anhänge, Moderation | offen |
| Chatverwaltung | Emoji-/Sticker-Katalog, Aufbewahrung, Rollenwirkung | offen |
| Profil | Stammdaten, Sichtbarkeit, Foto, Avatar einschließlich Pose, Speichern/erneut öffnen | Avatar und kleine Profil-Unterseiten lokal geprüft; übriger Umfang und Staging offen |
| Familie | Übersicht, Kind anlegen/bearbeiten, Beziehungen, Freigaben, Schulzugänge | offen |
| Datenschutz/Sicherheit | Einwilligungen, Widerruf, Kontoschutz, Sitzungen, Kontolöschung | offen |
| Benachrichtigungen | In-App-Liste, gelesen, Präferenzen, Geräte, Push, Installation | offen |
| Personen | Suche, sämtliche Filter/Sortierung, Detail, Rollen, Fehlerzustände | lokal abgeschlossen; Staging offen |
| Rollen | Zuweisungen, Berechtigungen, tatsächliche Zugriffswirkung | lokal abgeschlossen; Staging offen |
| Schulen/Klassen | Katalogsuche, Anlage, Import/Export, Detail, Zuordnungen | offen |
| Adapter/Module | Definitionen, Instanzen, Konfiguration, Freigaben, Verbindungsfehler | offen |
| Klassenleben | Kontakte, Lehrkräfte, Lernportale, Speiseplan, Aufgaben, Abwesenheiten | offen |
| Inhalte | Aktuelles, Veranstaltungen, Abstimmung, Mitbringliste, Dokumente | offen |
| Medien | Schuljahr/Ereignis, Galerie, Upload, Freigaben, Moderation, geschützter Abruf | offen |
| Weitere Fachmodule | Mobilität, PDF-Formulare, Photo Memory, fachliche Zustände der freigegebenen Module | offen |
| Portalverwaltung | Menüs, Registrierungen/Einladungen, Pilotmeldungen, Systemstatus, Monitoring, Modellansicht | offen |
| Designsystem/Themes | eigene Editorroute, validierte Tokens, Live-Vorschau, Abbrechen/Übernehmen, alle Presets | in Überarbeitung |

## Qualitätsgate je Bereich

1. Alle erreichbaren Seiten und Aktionen erfassen, einschließlich Details und Dialogen.
2. Fachliche Struktur mit Auftrag abgleichen; Wiederholungen und Platzhalter entfernen.
3. Gemeinsam definierte Komponenten einsetzen, nicht isolierte CSS-Reparaturen.
4. Synthetische Daten: Erstellen, Ändern, Abbrechen, Speichern, erneut öffnen,
   Fehler und zulässige Löschabläufe prüfen. Kein Test verändert reale Konten.
5. Berechtigte und unberechtigte Rollen getrennt testen.
6. Desktop, Tablet und Smartphone prüfen, einschließlich Tastatur, Dialogfokus,
   Scrollverhalten, Überläufe und stabiler Positionen beim Öffnen/Schließen.
7. Screenshots mit Zielvorgaben vergleichen; Korrektur und erneute Prüfung.
8. Ergebnis mit Testbeleg dokumentieren; nicht geprüfte Integrationen offen halten.

Ein bestandener Backendtest, ein erfolgreicher Build oder eine ladende Seite
ersetzt die visuelle und funktionale Abnahme nicht. Staging und lokaler Prüfstand
werden getrennt ausgewiesen. Der abschließende Status darf erst nach allen
Qualitätsgates auf abgenommen wechseln.
