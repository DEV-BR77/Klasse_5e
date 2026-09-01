# Naechste Codex-Aufgabe: stabiler WebUntis-Elternkonto-Token und Hausaufgaben

Stand: 1. September 2026

## Ziel

Schliesse die verbleibende Phase-9B-Grenze: Ermittle und implementiere einen
stabilen, eng begrenzten Authentisierungsweg fuer den vom echten Elternkonto
verwendeten Hausaufgaben-Endpunkt. Fuehre danach den realen, persoenlich
isolierten Hausaufgabenimport durch und pruefe im Anschluss die
Abwesenheits-Capabilities.

Der vorhandene Stundenplan, das Mapping, der gemeinsame Kalender, die
iCalendar-Funktionen und die drei taeglichen Synchronisationszeiten duerfen
nicht regressieren.

## Ausgangszustand

- main enthaelt ab Commit f3fa80d den gemeinsamen Monatskalender und das
  numerische Referenzmapping.
- 357 persoenliche Unterrichtszeilen sind vorhanden.
- Keine Unterrichtszeile zeigt noch rein numerische Fach- oder
  Lehrkraftbezeichnungen.
- 12 Fach-Aliase und 17 Lehrkraft-Aliase wurden aus den privaten lokalen
  Referenzen abgeleitet.
- Der JSON-RPC-Login mit der verschluesselten Laufzeitverbindung funktioniert
  fuer den Stundenplan.
- Der REST-Aufruf /api/homeworks/lessons liefert mit diesem Session-Cookie
  HTTP 500; der Synchronisationslauf klassifiziert den Teilfehler als
  not_authorized und behaelt die Stundenplandaten.
- Die Weboberflaeche verwendet nach dem Formularlogin zusaetzlich
  /api/token/new.
- Das reale Hausaufgabenschema ist bekannt und der synthetisch getestete
  Normalisierer fuer data/homeworks/lessons/records/teachers ist vorhanden.
- Die Produktionsdatenbank enthaelt weiterhin 0 Hausaufgaben.
- 92 App-Tests bestehen.

## Verbindliche Arbeitspakete

### 1. Authentisierung reproduzierbar klassifizieren

- Verwende ausschliesslich die bereits verschluesselte Pilotverbindung.
- Gib niemals Benutzername, Passwort, Cookie, Session-ID, CSRF-Wert, User-Token,
  Antworttext oder personenbezogene Inhalte aus.
- Erfasse nur Host, Methode, Pfad, Statusklasse, Headernamen, Schemaform und
  Anzahl.
- Klaere, ob /api/token/new einen fuer den User bestimmten Access-Token liefert
  und welche dokumentierte oder von der Weboberflaeche selbst verwendete
  Headerform der Hausaufgaben-Endpunkt erwartet.
- Pruefe die aktuellen offiziellen WebUntis-Unterlagen zum User Access Token.
- Verwende keinen dauerhaften Playwright-/Browser-Scraper im
  Produktionscontainer.
- Wenn ein Token einmalig durch den Benutzer erzeugt werden muss, ergaenze ein
  verschluesseltes, widerrufbares Tokenfeld und einen klaren Einrichtungsweg.
  Token niemals in URL, Logs, Git oder Dokumentation uebernehmen.

### 2. Eng begrenzten Client implementieren

- Host- und Endpoint-Allowlist beibehalten.
- JSON-RPC-Stundenplan und moderner User-Token duerfen getrennte
  Authentisierungskontexte besitzen.
- Sessions und Tokens nur so lange und so eng wie notwendig halten.
- 401/403, 429, 5xx, abgelaufener Token, MFA/SSO und unbekanntes Schema getrennt
  klassifizieren.
- Alte gueltige Daten bei einem temporaeren Fehler erhalten und als veraltet
  markieren.
- Keine beliebigen REST-/RPC-Aufrufe und keine Raw-Response-Funktion schaffen.

### 3. Realen Hausaufgabenimport abschliessen

- Nur bei aktivierter Hausaufgabenpraeferenz und bestaetigter Eltern-Kind-
  Zuordnung abrufen.
- Ausschliesslich Daten des bestaetigten Kindes speichern.
- Hausaufgabe ueber lessonId mit dem Fach verbinden.
- Ausgabe- und Faelligkeitsdatum, Text/Bemerkung und Erledigt-Status
  idempotent speichern.
- Wiederholung darf keine Duplikate erzeugen.
- Neue, geaenderte, unveraenderte und nicht mehr gelieferte Eintraege sauber
  behandeln.
- Hausaufgaben im gemeinsamen Kalender orange anzeigen und in der
  Tagesagenda mit dem Textlabel Hausaufgabe kennzeichnen.
- iCalendar-Snapshot und Abo-Feed mit realen Hausaufgaben pruefen.

### 4. Abwesenheits-Capability

- Lesen und Schreiben strikt trennen.
- Zuerst nur feststellen, ob das Elternkonto Abwesenheiten lesen und/oder
  anlegen darf.
- Lesende Abwesenheiten benoetigen eine eigene aktivierte Praeferenz und eine
  persoenliche Anzeige.
- Einen Schreibablauf nur umsetzen, wenn ein stabiler offizieller oder von der
  Weboberflaeche eindeutig verwendeter Endpunkt und das Recht des Elternkontos
  verifiziert sind.
- Andernfalls in der Oberflaeche ehrlich nach WebUntis verlinken.
- Kein medizinischer Freitext, keine Diagnose und keine stille Wiederholung
  eines Schreibrequests.

### 5. Betrieb und Dokumentation

- Automatische Abrufe weiterhin um 06:00, 12:00 und 18:00 Uhr.
- Keine neuen Worker, Redis-, WebSocket- oder Microservice-Abhaengigkeiten.
- Datenschutz-, Betriebs-, Funktionsmatrix-, Status- und Entscheidungsdokumente
  aktualisieren.
- Private Tabellen, CSVs, Browserprobes und Rohantworten bleiben ignoriert.
- Danach die separate UX-Aufgabe fuer Onboarding, Einstellungen und visuelle
  Erklaerungen als naechsten Auftrag formulieren.

## Pflichtpruefungen

- Synthetische Tests fuer Token erfolgreich, abgelaufen, abgelehnt und
  MFA/SSO-pflichtig.
- Keine Geheimnisse in Exception, Log, Git-Diff oder Testausgabe.
- Hausaufgaben: Erstimport, Wiederholung, Aenderung, Entfernung und Teilfehler.
- Persoenliche Isolation fuer Dashboard, Kalender und iCalendar.
- Abwesenheits-Capability fuer erlaubt, nicht erlaubt und nicht unterstuetzt.
- Vollstaendige App-Test-Suite.
- Ruff, Python-Kompilierung, Django check, Migrationsdrift und git diff --check.
- Docker-Build und kontrolliertes Deployment.
- Oeffentliche HTTPS-Smoke-Tests.
- Kontrollierter Realtest ausschliesslich fuer die bestehende Pilotverbindung.
- Bericht mit anonymisierten Anzahlen und klarer Aussage, ob Krankmeldungen im
  Portal moeglich sind.

## Abschluss

Arbeite selbststaendig bis zum Gate. Committe und pushe auf origin/main.
Wenn der reale User-Token ohne eine einmalige Benutzerhandlung nicht sicher
erzeugt werden kann, implementiere den sicheren Einrichtungsweg, dokumentiere
den exakten lokalen Schritt und behaupte keinen erfolgreichen Realimport.
