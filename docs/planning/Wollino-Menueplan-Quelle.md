# Quellen-Spezifikation: Wollino-Menüpläne für das THG

Stand: 26.08.2026

Dieses Dokument konkretisiert den in `UX-und-externe-Kalender.md` vorgemerkten
Essenskalender. Es hält die Ergebnisse eines read-only Quellen- und PDF-Audits
fest. Es autorisiert noch keine Implementierung und verändert die Freigabe der
Roadmap-Phasen nicht.

## 1. Ziel

Das CMS soll angemeldeten Klassenmitgliedern zwei Zugänge zum Speiseplan bieten:

1. `Aktuelle Menüpläne` mit den von Wollino veröffentlichten Wochenplänen für
   das Theodor-Heuss-Gymnasium;
2. eine kompakte Dashboard-Karte mit dem Essen für den aktuell relevanten
   Schultag und einem später ergänzbaren Stundenplan desselben Tages.

Die Originalquelle bleibt erkennbar. Importierte Inhalte dürfen nicht als
medizinisch garantierte oder gegenüber Wollino verbindlichere Information
dargestellt werden.

## 2. Geprüfte Quelle

- Anbieter: WOLLINO GmbH
- Startseite: `https://www.wollino.de/`
- öffentliche Menüplanseite für weiterführende Schulen:
  `https://www.wollino.de/newpagefa4f13d4`
- kein Login für Seite oder PDF-Abruf erforderlich;
- der relevante zweite Schulblock nennt gemeinsam:
  Schulzentrum Fallersleben, Schulzentrum Westhagen, Schulzentrum Vorsfelde,
  Theodor-Heuss-Gymnasium und Leonardo da Vinci Gesamtschule;
- darunter werden fortlaufend datierte Wochenlinks veröffentlicht;
- beim Audit waren die aktuelle und die folgenden Wochen sichtbar;
- die PDF-Dateinamen enthalten unter anderem die Kennung `THG`.

Die PDF-Links zeigen auf signierte CDN-URLs mit Ablaufparametern. Diese
vollständigen URLs sind deshalb nicht als dauerhafte Konfiguration geeignet.
Der Adapter muss die öffentliche Menüplanseite erneut lesen und die jeweils
aktuellen Links semantisch dem zweiten Schulblock zuordnen.

Eine Auswahl ausschließlich über Linkpositionen wie „der neunte Link“ ist
unzulässig. Der Adapter validiert Überschrift, Schulnamen, Datumsbeschriftung,
Dateityp und nach Möglichkeit die THG-Kennung im Dateinamen. Bei Mehrdeutigkeit
wird nicht automatisch importiert.

## 3. Ergebnis des PDF-Audits

Geprüfte Beispieldatei:
`KW35_LDV_SZV_SZW_SZF_THG_AEN.pdf`.

Die einseitige PDF/X-4-Datei besitzt eine echte Textebene und kann ohne OCR
verarbeitet werden. Eine lineare Textextraktion ist dennoch ungeeignet, weil
das mehrspaltige Layout Textreihenfolgen vermischt und einzelne eingebettete
Schriften Sonderzeichen nicht zuverlässig als Klartext liefern.

Die belastbare Auswertung erfolgt positionsbasiert:

- Kalenderwoche aus dem Dokument und Jahres-/Datumsbereich aus dem Linklabel;
- Spalten als Wochentage;
- Zeilen als Menülinie 1 und Menülinie 2;
- Gerichte innerhalb der Schnittfläche aus Wochentag und Menülinie;
- unmittelbar zugeordnete runde Codes für Zusatzstoffe und Allergene;
- separate Legende zur Übersetzung der Codes;
- Dokumentstand und Änderungsvorbehalt als Quellenmetadaten.

Die geprüfte Datei enthält Montag bis Donnerstag, aber keinen Freitag. Der
Import darf daher nicht voraussetzen, dass jede Woche fünf Essenstage besitzt.
Fehlende Tage werden als `nicht veröffentlicht` behandelt und nicht als
ausgefallenes Essen erfunden.

Erkannte Inhaltsgruppen:

- zwei Menüalternativen pro veröffentlichtem Tag;
- mehrere Bestandteile je Menü, etwa Hauptgericht, Beilage, Gemüse/Salat und
  Nachspeise;
- Zusatzstoffkennzeichen als Zahlen, einschließlich Unterkennzeichen;
- Allergenkennzeichen als Buchstaben mit teils genauer Getreideangabe;
- Bestellhinweis, Preise, Dokumentstand und Änderungsvorbehalt.

OCR dient nur als ausdrücklich gekennzeichneter Fallback für spätere PDFs ohne
brauchbare Textebene. OCR-Ergebnisse dürfen nicht ungeprüft als verbindliche
Allergeninformation veröffentlicht werden.

## 4. Internes Importmodell

Der quellenspezifische Adapter liefert neutrale Datensätze mit mindestens:

- `source_id`, Quellseite und Original-PDF-Link;
- Linkbeschriftung und veröffentlichter Datumsbereich;
- ISO-Jahr, ISO-Kalenderwoche und konkretes Menüdatum;
- Menülinie und geordnete Gerichtbestandteile;
- Zusatzstoffcodes samt aus der Dokumentlegende übernommener Bedeutung;
- Allergencodes samt aus der Dokumentlegende übernommener Bedeutung;
- Dokumentstand, Abrufzeit, Prüfsumme und Adapter-/Parser-Version;
- Importstatus, Prüfhinweise und optionaler redaktioneller Korrekturstatus.

Rohimport und redaktionelle Korrektur bleiben getrennt. Ein erneuter Import
darf eine bestätigte manuelle Korrektur nicht still überschreiben.

## 5. Synchronisation und Fehlerverhalten

Vorgeschlagen ist ein begrenzter serverseitiger read-only Abruf einmal täglich
am frühen Morgen sowie ein manueller Admin-Abruf. Häufigeres Polling ist bei
vier Wochenplänen nicht erforderlich.

Ablauf:

1. öffentliche Menüplanseite abrufen;
2. zweiten Schulblock über die Schulnamen identifizieren;
3. gültige datierte PDF-Links ermitteln;
4. nur neue oder anhand Prüfsumme geänderte PDFs verarbeiten;
5. Layout und Pflichtfelder validieren;
6. plausiblen Import veröffentlichen oder `Prüfung erforderlich` setzen;
7. letzten erfolgreichen Abruf und einen nicht sensitiven Fehlerstatus zeigen.

Bei geänderter Seiten- oder PDF-Struktur bleibt der Original-Link sichtbar,
aber nicht ausreichend geprüfte Tagesdaten werden nicht automatisch angezeigt.
Ein Fehler bei Wollino darf weder das Dashboard noch andere CMS-Module
blockieren.

## 6. Dashboard-Regel für den relevanten Tag

Die Umschaltzeit ist eine konfigurierbare Klassen- beziehungsweise
Systemeinstellung in `Europe/Berlin`; vorgeschlagener Standard ist 15:00 Uhr.

- vor der Umschaltzeit: heutiges Menü, sofern vorhanden;
- ab der Umschaltzeit: nächster veröffentlichter Essenstag;
- wenn heute kein Menü vorliegt: nächster veröffentlichter Essenstag;
- Wochenenden, Feiertage, Ferien und im PDF fehlende Tage werden übersprungen;
- existiert noch kein künftiger Plan, erscheint ein klarer Leerzustand mit Link
  zu den aktuellen Originalplänen.

Die Karte bezeichnet den Status ausdrücklich als `Heute`, `Morgen` oder
`Nächster Essenstag` und zeigt Datum und letzten Quellenabruf. Die spätere
Stundenplankarte soll dieselbe Tagesauswahl verwenden, bleibt aber ein eigener
Adapter und ein eigenes Fachmodell.

## 7. Darstellung

### Dashboard auf Smartphone

- kompakte Tageskarte mit Datum und Status;
- Menü 1 und Menü 2 als getrennte, gut lesbare Abschnitte;
- Zusatzstoffe und Allergene als beschriftete Chips;
- aufklappbare vollständige Legende;
- sichtbarer Link `Original-PDF bei Wollino`;
- letzte Aktualisierung und Änderungsvorbehalt;
- keine Wischgeste als einziger Zugangsweg.

### Seite `Aktuelle Menüpläne`

- Wochenkarten mit Kalenderwoche und Datumsbereich;
- aktuelle Woche zuerst, danach kommende Wochen;
- Link zum Original-PDF;
- optional eine strukturierte Tages-/Wochenansicht;
- Desktop als Wochenraster, mobil vorrangig als Tageskarten mit sichtbaren
  Zurück-/Weiter-Schaltflächen und optional ergänzendem Swipe;
- klare Lade-, Leer-, Fehler- und `Prüfung erforderlich`-Zustände.

## 8. Rechtliche und fachliche Grenze

Die Wollino-Seite weist darauf hin, dass veröffentlichte Inhalte und Werke dem
Urheberrecht unterliegen und eine weitergehende Vervielfältigung, Bearbeitung
oder Verbreitung grundsätzlich vorherige Zustimmung erfordern kann. Deshalb
gilt für die Planung:

- externe Verlinkung auf den aktuellen Originalplan ist die sichere
  Basisfunktion;
- strukturierte Auswertung wird mit Quellenangabe und ausschließlich für den
  geschützten Klassenbereich geplant;
- vor dauerhafter PDF-Spiegelung oder produktiver automatisierter Übernahme
  wird eine kurze schriftliche Zustimmung von Wollino beziehungsweise der
  zuständigen Schule eingeholt;
- bis dahin werden PDFs höchstens temporär zur Verarbeitung geladen und nicht
  als eigene öffentliche Kopie angeboten;
- Allergene und Zusatzstoffe werden quellengetreu dargestellt, jedoch mit
  Aktualitätsangabe, Original-Link und Hinweis, dass im Zweifel der aktuelle
  Wollino-Plan beziehungsweise die Mensa maßgeblich ist.

Kontaktangaben sind auf der Wollino-Seite beziehungsweise im Impressum
veröffentlicht. Die spätere Anfrage soll Verlinkung, automatisierten Abruf,
strukturierte geschützte Darstellung, Zwischenspeicherung und Änderungsabruf
jeweils ausdrücklich benennen.

## 9. Abnahmekriterien einer späteren Implementierung

- Der Adapter wählt nachweislich den THG-Schulblock und nicht den ähnlich
  aufgebauten ersten Block.
- Abgelaufene signierte CDN-Links werden durch erneute Quellenermittlung
  ersetzt.
- Der bereitgestellte KW-35-Plan wird mit korrekten Tagen, zwei Menülinien und
  zugeordneten Zusatzstoff-/Allergencodes verarbeitet.
- Ein fehlender Freitag erzeugt kein erfundenes Menü.
- Ab der konfigurierten Umschaltzeit erscheint der nächste tatsächlich
  veröffentlichte Essenstag.
- Eine unerwartete Layoutänderung führt zu `Prüfung erforderlich` statt zu
  stillen Falschinformationen.
- Das Original-PDF, Quelle, Abrufzeit und Änderungsvorbehalt sind erreichbar.
- Smartphone- und Desktopdarstellung werden mit konkreten Wireframes und
  Bedienabläufen vor der UI-Implementierung abgenommen.

## 10. Noch nicht autorisiert

Dieses Audit autorisiert weder Scraper, Importjob, Datenmodell, UI noch einen
periodischen Containerprozess. Die Implementierung wird erst in einer dafür
freigegebenen Phase beauftragt.
