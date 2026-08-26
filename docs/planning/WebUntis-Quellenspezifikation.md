# Quellen-Spezifikation: WebUntis am Theodor-Heuss-Gymnasium

Stand: 26.08.2026

Dieses Dokument konkretisiert die Quellenprüfung für Phase 9. Es basiert auf
der angemeldeten Erziehungsberechtigten-Ansicht, den bereitgestellten
Screenshots und der offiziellen Untis-Dokumentation. Es autorisiert noch keine
produktive Anbindung, keinen automatisierten Login und kein Scraping.

## 1. Ziel

Das KlassenCMS soll die bereits in Phase 8 vorhandenen neutralen Kalender- und
Stundenplanmodelle aus WebUntis aktualisieren können. Auf dem persönlichen
Dashboard sollen der relevante Schultag, Stundenplan, Änderungen und später
der Wollino-Speiseplan gemeinsam, aber fachlich getrennt dargestellt werden.

Gewünschte Datenbereiche:

- regulärer Stundenplan;
- Vertretungen und sonstige Änderungen;
- Unterrichtsentfall;
- Prüfungen und Klassenarbeiten;
- Zusatzveranstaltungen und Hinweise zur Stunde;
- Ferien und unterrichtsfreie Zeiträume;
- Hausaufgaben mit Aufgabe- und Fälligkeitsdatum;
- Quellzeitpunkt und letzter erfolgreicher Abruf.

Abwesenheiten, Mitteilungen, Klassenbucheinträge, Noten und andere in WebUntis
sichtbare Bereiche gehören nicht zu diesem Auftrag.

## 2. Geprüfte Quelle

- Produkt: WebUntis
- Schule: Theodor-Heuss-Gymnasium Wolfsburg
- Schulkennung: `thgwob`
- Login:
  `https://thgwob.webuntis.com/WebUntis/?school=thgwob#/basic/login`
- persönliche Stundenplanansicht:
  `https://thgwob.webuntis.com/timetable/my-student`
- Hausaufgabenansicht:
  `https://thgwob.webuntis.com/student-homework`
- Zugriff: authentisierter Erziehungsberechtigten-Zugang;
- geprüftes Schuljahr: 2026/2027;
- Navigation: wochenweise über Vor-/Zurück-Schaltflächen und direkte
  Datumsparameter.

Die bereitgestellte lokale Zugangsdaten-Datei heißt
`.env.webuntis.local`, wird bereits von der allgemeinen Regel `.env.*`
ignoriert und war nie Bestandteil von Git. Die darin enthaltenen persönlichen
Eltern-Zugangsdaten sind ausschließlich Prüfmaterial und kein zulässiges
Produktionsgeheimnis.

## 3. Sichtbare Stundenplandaten

Die Wochenansicht enthält je Unterrichtskarte mindestens:

- Datum, Beginn und Ende beziehungsweise Zuordnung zum Zeitraster;
- Fachkürzel;
- Lehrkraftkürzel;
- Raum;
- Klasse oder beteiligte Klassen;
- ergänzende Bezeichnung oder Information zur Stunde;
- Status und gegebenenfalls parallele ursprüngliche/geänderte Belegung.

Beobachtete Statusarten:

- regulärer Unterricht;
- `Änderung`, in der Oberfläche grün markiert;
- `Prüfung`, in der Oberfläche gelb markiert;
- `Entfall`, in der Oberfläche rot markiert und teils durchgestrichen;
- Ferien als flächiger, gesperrter Zeitraum;
- zusätzliche Veranstaltung, beispielsweise Exkursion oder Spendenlauf;
- gekürzter oder anderweitig erläuterter Unterricht über den Detailtext.

Farben sind nur Darstellungshinweise und dürfen nicht zur alleinigen
fachlichen Klassifikation verwendet werden. Der Adapter benötigt strukturierte
Statusfelder beziehungsweise zugängliche Statusbezeichnungen. Das CMS zeigt
zusätzlich immer Symbol und Text.

Prüfungsdetails können unter anderem enthalten:

- Prüfungsart, beispielsweise Klassenarbeit;
- Fach;
- Datum und Zeit;
- Raum;
- Lehrkraft;
- freigegebene Information zur Stunde.

Nicht jeder sichtbare interne WebUntis-Bezeichner ist für Eltern hilfreich.
Technische IDs, interne Entitätsnummern und nicht benötigte Klassenlisten
werden nicht in das CMS übernommen.

## 4. Sichtbare Hausaufgabendaten

Die Hausaufgabenansicht enthält mindestens:

- Fach;
- Lehrkraftkürzel;
- Aufgabedatum;
- Fälligkeitsdatum;
- Aufgabenart;
- freigegebenen Aufgabentext;
- Gruppierung wie `Bald fällig`, `Noch nicht abgeschlossen` und `Verpasst`.

Der CMS-Import speichert den von WebUntis gelieferten fachlichen Status und
berechnet zusätzlich eine eigene datumsbezogene Anzeige. Er behauptet nicht,
dass eine Aufgabe individuell erledigt wurde, wenn WebUntis diesen Zustand
nicht eindeutig für den angemeldeten Schüler liefert.

Hausaufgabentexte sind schülerbezogene, nicht öffentliche Schuldaten. Sie
dürfen nur dem betreffenden Schüler und den verifizierten berechtigten
Sorgepersonen angezeigt werden. Push-Nachrichten enthalten keinen
Aufgabentext.

## 5. Offiziell vorgesehene Integrationswege

### 5.1 Persönliches iCal-Abo

WebUntis dokumentiert ein persönliches iCal-Abo direkt in der
Stundenplanansicht. Für Schülerinnen, Schüler und Sorgeberechtigte hängt die
Verfügbarkeit von der schulischen Modul- und Rechtekonfiguration ab.

Vorteile:

- offiziell vorgesehener read-only Export;
- kein automatisierter Browser-Login;
- gut für Basiszeiten und Kalenderdarstellung;
- einfacher, robuster Einstieg für einen begrenzten Pilotbetrieb.

Grenzen:

- der genaue Umfang dieses THG-Feeds ist noch praktisch zu prüfen;
- Prüfungs-, Hausaufgaben-, Entfall- und Detailinformationen können fehlen;
- Aktualisierungsintervalle externer Kalender sind nicht garantiert;
- ein persönlicher Feed ist ein geheimes Zugriffstoken und darf weder in Git
  noch in Logs oder öffentliche Links gelangen;
- ein Feed pro Kind beziehungsweise Konto skaliert organisatorisch schlecht.

iCal ist daher der bevorzugte erste technische Test, aber erst nach Sichtung
eines freigegebenen Beispiel-Feeds und seiner tatsächlichen Felder.

### 5.2 Offizielle WebUntis-Schnittstelle

Untis beschreibt weiterhin die WebUntis-API unter `jsonrpc.do` und nennt
Schulprojekte, Schülerentwicklungen und kleinere Eigenentwicklungen als
typische Anwendungsfälle auf Anfrage. Neuere Plattform-APIs und OIDC sind
ebenfalls vorhanden, ihre Nutzung hängt jedoch von einer als Plattform-App
freigegebenen Integration und den bereitgestellten Berechtigungen ab.

Für das KlassenCMS ist deshalb schriftlich bei Schule beziehungsweise
WebUntis-Betreuung zu klären:

- ob die API für dieses Projekt freigegeben wird;
- welche Schnittstelle aktuell empfohlen wird;
- ob ein eigener, rein lesender Integrationszugang erstellt werden kann;
- welche Datenbereiche dieser Zugang lesen darf;
- ob Stundenplanänderungen, Prüfungen und Hausaufgaben enthalten sind;
- welche Rate-Limits und Aufbewahrungsregeln gelten;
- ob OIDC beziehungsweise kurzlebige Tokens möglich sind;
- ob die alte JSON-RPC-API angesichts der dokumentierten Einschränkung bei 2FA
  überhaupt noch der passende Weg ist.

Ein dedizierter Klassen-/Integrationszugang mit minimalen Leserechten ist einem
persönlichen Elternkonto zwingend vorzuziehen.

### 5.3 Browser-Automatisierung

Ein automatisierter Login und das Auslesen der internen Weboberfläche sind
nicht die Standardlösung. Interne Endpunkte, HTML-Struktur und Sitzungsabläufe
können sich ohne Vorankündigung ändern. Eine solche Lösung wäre nur zulässig,
wenn:

- Schule und gegebenenfalls Untis schriftlich zustimmen;
- kein geeigneter offizieller Export oder API-Zugang verfügbar ist;
- ein dedizierter Lesezugang statt eines persönlichen Elternkontos existiert;
- MFA, Sitzungswechsel und Rate-Limits sauber gelöst sind;
- Strukturänderungen zum sicheren Importstopp führen;
- Zugangsdaten ausschließlich aus der zentralen Geheimnisverwaltung stammen.

## 6. Empfohlene Entscheidung

Die Integration wird in drei Prüfstufen entschieden:

1. **iCal-Pilot:** Verfügbarkeit und Feldumfang des persönlichen THG-Feeds mit
   einem ausdrücklich freigegebenen Testtoken prüfen.
2. **API-Anfrage:** Parallel einen dedizierten read-only Zugang für
   Stundenplan, Änderungen, Prüfungen und Hausaufgaben bei der Schule
   beantragen.
3. **Abbruch oder Sonderfreigabe:** Wenn beides nicht ausreicht, nicht
   automatisch auf Scraping wechseln, sondern eine neue dokumentierte
   Entscheidung einholen.

Für die vollständige gewünschte Funktion ist voraussichtlich eine offizielle
API erforderlich; iCal bleibt sinnvoller Fallback für den Grundstundenplan.

## 7. Neutraler Importvertrag

Der WebUntis-Adapter darf die vorhandenen Phase-8-Modelle nur über eine kleine
Import-Schnittstelle aktualisieren. Er liefert mindestens:

### Unterricht und Änderungen

- stabile externe Ereigniskennung, sofern vorhanden;
- Schüler-/Klassenbezug als lokale opaque Zuordnung;
- Datum, Beginn und Ende;
- Fach, freigegebene Lehrkraftbezeichnung und Raum;
- Status `regular`, `changed`, `cancelled`, `exam`, `event` oder `holiday`;
- ursprüngliche Werte bei Änderung oder Entfall, soweit geliefert;
- freigegebenen Hinweistext;
- Quellrevision beziehungsweise Inhaltsprüfsumme;
- Abrufzeit, Quellzeit und Adapterversion.

### Hausaufgaben

- stabile externe Aufgabenkennung, sofern vorhanden;
- Fach und freigegebene Lehrkraftbezeichnung;
- Aufgabe- und Fälligkeitsdatum;
- freigegebener Aufgabentext;
- Quellstatus;
- Abrufzeit, Quellzeit und Adapterversion.

Wenn die Quelle keine stabile ID liefert, wird ein dokumentierter fachlicher
Schlüssel plus Inhaltsprüfsumme verwendet. Derselbe Abruf erzeugt keine
doppelten Datensätze.

## 8. Änderungsvergleich und Benachrichtigung

Der Import vergleicht Revisionen und erzeugt nur bei einer tatsächlichen
fachlichen Änderung ein Ereignis. Reine Format-, Farb- oder Reihenfolgeänderung
erzeugt keine Benachrichtigung.

Benachrichtigungswürdige Änderungen:

- Unterricht entfällt;
- Vertretung, Fach, Raum oder Zeit ändert sich;
- zusätzliche Stunde oder Veranstaltung;
- neue oder geänderte Prüfung;
- neue oder geänderte Hausaufgabe nach eigener Benutzerpräferenz.

Push bleibt freiwillig und datensparsam, beispielsweise
`Der Stundenplan für morgen wurde geändert.` Details erscheinen erst nach dem
Login. Prüfungstitel, Hausaufgabentexte, Namen und Räume werden standardmäßig
nicht in die Push-Nachricht geschrieben.

## 9. Dashboard- und Mobilansicht

Das Smartphone zeigt vorrangig den relevanten Tag als vertikale Kartenliste:

- Uhrzeit und Unterrichtsblock;
- Fach, Raum und freigegebene Lehrkraftbezeichnung;
- gut sichtbare Statuschips mit Text und Symbol;
- Prüfung oder Hausaufgabe als eigener, aufklappbarer Hinweis;
- Speiseplan als getrennte Karte für denselben Tag;
- letzte erfolgreiche Aktualisierung und Link zu WebUntis.

Auf dem Desktop bleibt zusätzlich die Wochenansicht erhalten. Vor- und
Zurück-Schaltflächen sind immer vorhanden; eine Wischgeste ist nur eine
ergänzende Komfortfunktion.

Für die Tagesauswahl gilt dieselbe konfigurierbare Umschaltlogik wie beim
Speiseplan: vor der Umschaltzeit der aktuelle Schultag, danach der nächste
tatsächliche Schultag. Entfallene Stunden bleiben als Entfall sichtbar und
werden nicht einfach aus dem Tagesplan entfernt.

## 10. Synchronisation und Ausfallsicherheit

Die endgültige Abruffrequenz wird erst nach Kenntnis des offiziellen
Rate-Limits festgelegt. Als Obergrenze für einen kleinen read-only Pilotbetrieb
ist zunächst vorgesehen:

- tagsüber höchstens alle 15 Minuten;
- nachts und an Wochenenden deutlich seltener;
- zusätzlicher manueller Admin-Abruf mit eigener Begrenzung;
- HTTP-Timeout, begrenzte Wiederholung und exponentielle Pause;
- keine parallelen Abrufe desselben Zeitraums;
- bevorzugt Änderungsmarker, ETag oder Quellrevision nutzen.

Bei Ausfall zeigt das CMS den letzten erfolgreichen Stand mit Zeitstempel und
dem Hinweis `WebUntis derzeit nicht aktualisierbar`. Alte Daten werden nicht
als aktuell ausgegeben. Der manuelle Phase-8-Stundenplan bleibt als Fallback
nutzbar und wird durch einen Quellenfehler nicht überschrieben.

## 11. Geheimnisse und Datenschutz

- keine persönlichen Elternpasswörter im Produktivbetrieb;
- keine Klartextzugänge in Repository, Compose-Datei, Image, Datenbank oder
  Logs;
- freigegebene Integrationsgeheimnisse nur über
  `secret://projects/klasse-5e/webuntis/...`;
- iCal-URLs wie Passwörter behandeln, nur gehasht referenzieren oder
  verschlüsselt bereitstellen und widerrufbar halten;
- nur Daten der Klasse beziehungsweise des verknüpften Kindes übernehmen;
- keine Abwesenheiten, Noten, Mitteilungen oder Klassenbucheinträge importieren;
- kurze, fachlich festzulegende Aufbewahrung und vollständige Löschung beim
  Ende der Berechtigung;
- Quellzugriff und administrative Korrekturen auditieren, Inhalte nicht in
  technische Logs schreiben.

## 12. Noch offene Freigaben

Vor Implementierung fehlen weiterhin:

1. schriftliche Zustimmung der Schule zur externen Darstellung im
   geschützten KlassenCMS;
2. Entscheidung der schulischen WebUntis-Administration über iCal, API oder
   Plattform-App;
3. freigegebener synthetischer oder dedizierter read-only Testzugang;
4. dokumentierter tatsächlicher Feldumfang eines THG-iCal-Feeds;
5. API-Dokumentation, Berechtigungen, MFA-Verhalten und Rate-Limit;
6. fachliche Festlegung, ob Lehrkraftkürzel im CMS sichtbar sein dürfen;
7. Lösch- und Aufbewahrungsfristen für Stundenplan, Prüfungen und Hausaufgaben.

## 13. Abnahmekriterien einer späteren Phase 9

- kein persönliches Elternkonto als unbeaufsichtigter Produktionszugang;
- ausschließlich offiziell freigegebener read-only Zugriff;
- Klasse-, Schüler- und Familienisolation in automatisierten Tests;
- korrekte Abbildung von Regelstunde, Änderung, Entfall, Prüfung, Ferien und
  Zusatzveranstaltung;
- Hausaufgaben nur für das verknüpfte Kind und berechtigte Sorgepersonen;
- idempotenter Import und reproduzierbarer Änderungsvergleich;
- keine Push-Dopplungen und keine sensitiven Push-Inhalte;
- sofortiger Zugriffsentzug nach Ende der Mitgliedschaft oder Quellfreigabe;
- sicherer Stillstand bei unbekanntem Quellformat;
- dokumentierter Export-/API-Ausfall und manueller Fallback;
- keine Geheimnisse oder echten Schuldaten in Git und Test-Fixtures.

## 14. Noch nicht autorisiert

Dieses Dokument schließt nur das fachliche Quellen-Audit ab. Es autorisiert
keinen API-Schlüssel, keine Plattform-App, keinen periodischen Abruf, keinen
automatisierten Login und kein Browser-Scraping. Phase 9 beginnt erst nach den
unter Abschnitt 12 genannten Freigaben.
