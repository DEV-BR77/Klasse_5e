# Spezifikationsbedarf: Responsive UX und externe Kalender

Stand: 26.08.2026

Dieses Dokument hält verbindliche Anforderungen für kommende Planungsphasen
fest. Es autorisiert noch keine Implementierung und verändert die Freigabe der
Roadmap-Phasen nicht. Nach Abschluss der aktuell laufenden Arbeit wird es in
`docs/Roadmap.md` verlinkt und in die endgültige Phasenfolge eingeordnet.

## 1. Verbindliches UX-Spezifikationsgate

Die vorhandenen und künftigen Fachfunktionen dürfen nicht lediglich als
technische Formulare nebeneinandergestellt werden. Vor der nächsten größeren
UI-Ausbaustufe wird ein eigenes UX-/UI-Spezifikationsgate durchgeführt.

Zu bewerten und anschließend präzise zu spezifizieren sind mindestens:

- Dashboard und globale Navigation;
- geschützte PDF-Formulare und Dokumentdownloads;
- Veranstaltungen und Mitbringlisten;
- Foto- und Bildergalerien;
- Profile, Familienbeziehungen und Einwilligungen;
- künftiger Essenskalender;
- künftiger Stundenplan und Vertretungsänderungen.

### Geräteszenarien

Die Oberfläche muss mindestens auf folgenden Ansichten gezielt entworfen und
praktisch geprüft werden:

- Smartphone im Hochformat als primäre Alltagsansicht;
- Smartphone im Querformat;
- Tablet im Hoch- und Querformat;
- Desktop beziehungsweise Notebook im Querformat;
- installierte PWA und normaler Browseraufruf.

Mobile Bedienung ist kein nachträgliches Zusammenschieben der Desktopansicht.
Informationsdichte, Priorität, Navigation und Interaktionen werden für kleine
Bildschirme eigenständig festgelegt.

### Interaktionsprinzipien

- wichtige Aktionen mit wenigen Berührungen erreichbar;
- große, gut unterscheidbare Touch-Ziele;
- Kachelansichten für visuell auswählbare Elemente;
- Suche, Kategorien und zuletzt beziehungsweise häufig verwendet;
- verständliche Bestätigung vor verbindlichen Änderungen;
- unmittelbares Feedback nach Auswahl oder Reservierung;
- keine allein von Hover abhängigen Funktionen;
- Wischgesten nur als Komfortfunktion, nie als einziger Bedienweg;
- immer sichtbare beziehungsweise tastaturbedienbare Alternativen zu Gesten;
- keine horizontale Pflichtnavigation für zentrale Funktionen;
- verständliche Lade-, Leer-, Fehler- und Offlinezustände;
- barrierearme Kontraste, Fokusführung und Screenreader-Beschriftungen;
- keine Statusinformation ausschließlich über Farbe.

### Mitbringlisten

Die bestehende Mitbringfunktion benötigt eine vertiefte Produktspezifikation.
Geprüft werden mindestens:

- Kacheln für typische Beiträge wie Brot, Brötchen, Salat, Obst, Getränke,
  Geschirr und Helferdienste;
- Kategorieauswahl und schnelle Suche;
- Synonyme und tolerante Suche, beispielsweise `Brötchen`/`Semmeln`;
- häufig verwendete und zuletzt verwendete Einträge;
- Menge und Einheit direkt an der Auswahl;
- eigener freier Beitrag;
- Kennzeichnung `noch benötigt`, `vollständig` und `bereits vergeben`;
- verständliche Reservierungsbestätigung;
- Korrektur und Rücknahme;
- Schutz vor Doppel- und Überbuchung;
- mobile Kachelgröße und Anzahl pro Zeile;
- Desktopdarstellung mit höherer Informationsdichte;
- optionales horizontales Blättern zwischen Kategorien mit sichtbarer
  Alternative über Tabs oder Schaltflächen;
- Lade- und Konfliktzustand bei gleichzeitigen Reservierungen.

Vor Umsetzung der UI-Überarbeitung werden Wireframes für Smartphone und
Desktop, ein Interaktionsablauf und konkrete Abnahmeszenarien erstellt. Die
bestehenden Sicherheits-, Rollen- und Transaktionsregeln bleiben maßgeblich.

## 2. Essenskalender

Ein Essenskalender soll als neues Fachmodul beziehungsweise als klar
abgegrenzte Kalenderansicht geplant werden. Er soll nach Möglichkeit Daten aus
einer externen Quelle übernehmen.

Zu spezifizieren sind mindestens:

- Quelle beziehungsweise Anbieter und konkrete URL;
- öffentlicher Zugriff oder Anmeldung;
- offizielle API, iCal, JSON, PDF, HTML oder anderer Export;
- Nutzungsbedingungen und zulässige Abruffrequenz;
- Menüdatum, Menüname und Beschreibung;
- mehrere Menülinien beziehungsweise Alternativen;
- vegetarisch, vegan und weitere Kennzeichnungen;
- Allergene und Zusatzstoffe, soweit die Quelle sie verlässlich liefert;
- Preisangaben nur bei tatsächlichem Bedarf;
- Ausfall, Ferien, Feiertag und `kein Essen`;
- Quelle und Zeitpunkt der letzten Synchronisation;
- Änderungsmarkierung und Fehlerstatus;
- manueller Fallback ohne Überschreiben verlässlicher redaktioneller Daten;
- mobile Tages-/Wochenansicht;
- optionale Benachrichtigungen nur nach eigener Freigabe.

Extern gelieferte Allergieinformationen dürfen nicht als medizinisch
garantiert dargestellt werden. Quelle, Aktualität und Haftungsgrenzen müssen
sichtbar bleiben.

Vor Implementierung wird ein read-only Quellen-Audit durchgeführt. Scraping
ist nur nach Prüfung von Nutzungsrecht, Stabilität, robots-/Zugriffsregeln und
fehlender offizieller Alternative zulässig. Zugangsdaten gehören ausschließlich
in die zentrale Geheimnisverwaltung.

## 3. Stundenplan und Vertretungen

Der Stundenplan bleibt ein eigenes Fachmodul mit neutralem internen Modell.
Eine externe Quelle wird über einen austauschbaren Adapter angebunden.

Zu spezifizieren sind mindestens:

- verwendetes Schulportal beziehungsweise Anbieter;
- konkrete Login- und Zielseiten;
- offizieller Klassen-, Eltern- oder Lesenzugang;
- API, iCal, JSON, PDF, HTML oder anderer Export;
- Nutzungsrecht und Zustimmung der Schule;
- MFA, Sitzungsdauer und technische Zugriffsbeschränkungen;
- reguläre Unterrichtsstunden;
- Fach, Lehrer, Raum, Beginn und Ende;
- Ausfall, Vertretung, Raumwechsel und Verschiebung;
- Gültigkeitszeitraum und Quelle;
- Zeitpunkt der letzten erfolgreichen Synchronisation;
- idempotenter Import und Änderungsvergleich;
- Schutz gegen doppelte oder veraltete Meldungen;
- manueller Stundenplan als Fallback;
- Wochenansicht auf Desktop;
- priorisierte Tagesansicht auf Smartphones;
- datensparsame Push-Nachricht mit Details erst nach Login.

Es werden keine individuellen Portal-Zugangsdaten der Eltern gespeichert.
Bevorzugt wird ein offiziell vorgesehener gemeinsamer Lesezugang oder Export.
Browser-Scraping ist keine Standardentscheidung und benötigt eine gesonderte
Machbarkeits- und Rechtsprüfung.

## 4. Gemeinsame Adapter- und Synchronisationsgrenze

Essenskalender und Stundenplan verwenden getrennte Quelladapter, liefern aber
in kleine neutrale Importverträge. Quellenspezifische HTML-Selektoren,
Sitzungen und Zugangsdaten dürfen nicht in den Fachmodellen verteilt werden.

Jeder Adapter benötigt mindestens:

- eindeutige Quellenkennung und Adapterversion;
- read-only Abruf;
- validiertes neutrales Ergebnis;
- idempotente Synchronisation;
- Abrufzeit und Quellzeitpunkt;
- nicht sensitiven Fehlerstatus;
- Rate-Limit und Timeout;
- Test-Fixtures ohne echte Zugangsdaten;
- Erkennung geänderter Quellstruktur;
- manuellen Fallback;
- Abschaltmöglichkeit ohne Ausfall der übrigen Plattform.

## 5. Ablauf der nächsten Spezifikationsgespräche

Für jede externe Internetseite wird zunächst nur eine Quellen-Spezifikation
erstellt. Benötigte Angaben:

1. URL der Start- und Zielseite;
2. Name des Anbieters;
3. öffentlich oder Login erforderlich;
4. vorhandener Export beziehungsweise offizielle App;
5. beispielhafte gewünschte Datenfelder;
6. gewünschte Aktualisierungshäufigkeit;
7. gewünschte Darstellung auf Smartphone und Desktop;
8. gewünschte Änderungs- und Pushregeln;
9. bekannte Zustimmung oder Vorgaben der Schule;
10. zulässiger Testzugang ohne Offenlegung eines Passworts im Chat.

Erst nach dem Quellen-Audit wird entschieden zwischen:

- offizieller API;
- iCal-/Dateiimport;
- serverseitigem read-only Adapter;
- manuellem Import;
- oder bewusst keiner automatischen Integration.

## 6. Noch nicht autorisiert

Dieses Dokument autorisiert weder die UI-Überarbeitung noch einen externen
Login, Web-Scraping, Kalenderimport oder Push-Versand. Es sichert die
Anforderungen für die kommende Roadmap- und Spezifikationsarbeit.
