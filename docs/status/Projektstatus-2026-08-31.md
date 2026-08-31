# Projektstatus Klasse 5e

Stand: 31. August 2026

## Kurzfassung

Das Klassenportal ist unter `https://5e.eventmonitor.eu` erreichbar, durch
Anmeldung und verpflichtende MFA für privilegierte Konten geschützt und läuft
im Docker-Betrieb gesund. Die Phasen 0 bis 8 sowie das Datenschutz- und
Onboarding-Arbeitspaket aus `Nextsteps.md` (Aufgaben 1 bis 14) sind technisch
umgesetzt. Phase 9 ist mit Phase 9A als sicherer, kontrollierter
WebUntis-Pilot begonnen, aber noch nicht fachlich abgeschlossen.

Der wichtigste offene Punkt ist die tatsächliche WebUntis-Anbindung eines
Elternkontos. Die Verbindung kann eingerichtet und geprüft werden, die
aktivierten Datenkategorien werden jedoch noch nicht normalisiert oder im
Portal angezeigt. Der jüngste reale, anonymisiert geprüfte Synchronisationslauf
endete außerdem mit `not_authorized`. Abwesenheiten können derzeit weder
importiert noch über das Klassenportal eingetragen werden.

## Repository-Stand

- Branch: `main`
- Ausgangscommit dieses Berichts: `3e33236`
- `main` und `origin/main` waren vor Erstellung dieses Berichts identisch.
- Der Arbeitsbaum war vor Erstellung der beiden Übergabedokumente sauber.
- Letzte relevante Commits:
  - `3e33236` – WebUntis-Kategoriestatus sichtbar gemacht
  - `9c03d0b` – Onboarding und Grenzen des WebUntis-Piloten erklärt
  - `2201792` – Anmeldung, MFA-Seiten und statische Gestaltung vereinheitlicht
  - `07e8a93` – Anwendung über den abgesicherten Reverse Proxy veröffentlicht
  - `2ae7fa0` – privilegierte Konten korrekt zur MFA-Einrichtung geleitet
  - `dee3b7d` – Qualitätsgate für Aufgaben 1 bis 14 dokumentiert

## Umgesetzter Funktionsumfang

### Fachliche Phasen

- Phasen 0 bis 8 sind laut `docs/Roadmap.md` abgeschlossen.
- Das Django-/Wagtail-Grundsystem, Einladungen, Rollen, bestätigte
  Sorgebeziehungen, Einwilligungen und Audit sind vorhanden.
- CMS-Inhalte, geschützte Dokumente, Veranstaltungen, Mitbringlisten,
  geschützte Galerien, optional gesperrte Biometrie, Klassenchat, manueller
  Kalender und iCal sind umgesetzt.
- Biometrische Funktionen bleiben global deaktiviert. Die vorhandenen
  Pilotentscheidungen sind ausschließlich in der Laufzeitdatenbank erfasst;
  Git enthält keine personenbezogenen Pilotdaten, Bilder oder Embeddings.
- Die Aufgaben 1 bis 14 aus `Nextsteps.md` sind dokumentiert und technisch
  umgesetzt. Die rechtliche und organisatorische Produktivfreigabe ist dadurch
  nicht ersetzt.

### Anmeldung, Onboarding und Bedienoberfläche

- Öffentliche Selbstregistrierung ist entfernt.
- Die Anmelde-, Reauthentifizierungs- und MFA-Oberflächen verwenden das
  Projektlayout und die gesammelten statischen Dateien.
- Der frühere MFA-Weiterleitungsfehler ist behoben.
- Das Onboarding ist fortsetzbar, erlaubt Pause und spätere Änderungen und
  erklärt die getrennten freiwilligen Funktionen ausführlicher.
- Datenschutzinformationen öffnen außerhalb des erzwungenen Schrittflusses,
  ohne den Benutzer wieder an den Anfang des Onboardings zu schicken.
- Das Tutorial ist erneut aufrufbar und verwendet synthetische Illustrationen.

Offen bleibt eine echte qualitative UX-Abnahme mit einem neuen, noch nicht
zugeordneten Testkonto. Die aktuelle Tour ist eine interaktive Erklärung mit
schematischen Illustrationen, kein produziertes Erklärvideo. Ob sie für neue
Eltern ohne Vorwissen ausreichend verständlich ist, muss noch praktisch
getestet und gegebenenfalls überarbeitet werden.

### WebUntis Phase 9A

Vorhanden sind:

- ein interner, auf `thgwob.webuntis.com` begrenzter JSON-RPC-/REST-Client;
- eine feste Endpoint-Allowlist ohne beliebige Rohaufrufe;
- verschlüsselte Zugangsdaten in PostgreSQL;
- genau eine Verbindung je Benutzer und bestätigtem Kind;
- serverseitige Prüfung der Sorgeberechtigung und Einwilligung;
- getrennte, standardmäßig deaktivierte Funktionspräferenzen;
- manuelle Verbindungsprüfung und kontrollierter Abruf;
- Sperre, Mindestabstand, Idempotency-Key und neutrale Fehlerklassen;
- eine standardmäßig deaktivierte automatische Synchronisationskonfiguration;
- vollständiges, idempotentes Entfernen einer Verbindung;
- sichtbare Erklärung, warum Phase 9A noch keine Termine importiert.

Anonymisierter Laufzeitstand am 31. August 2026:

- 1 eingerichtete Verbindung mit Status `ok`;
- 13 aktivierte Funktionspräferenzen;
- 0 gespeicherte WebUntis-Stunden;
- 0 gespeicherte WebUntis-Hausaufgaben;
- jüngster Lauf: `failed`, Fehlerklasse `not_authorized`;
- ein früherer Lauf erreichte `no_change`, hatte jedoch keine wirksam
  abgerufenen Kategorien;
- keine Rohantwort, kein Kennwort, keine Session-ID und keine personenbezogene
  WebUntis-Antwort wurde für diesen Bericht ausgegeben oder gespeichert.

Wichtige technische Grenze: `execute_run()` ruft aktivierte Endpunkte nur auf
und verwirft die Antworten. Es gibt noch keine Normalisierung, keinen
Änderungsvergleich und keine Übergabe an Dashboard oder Kalender. Der
JSON-RPC-Login bildet den aktuell im Browser funktionierenden
Elternkontoablauf offenbar noch nicht zuverlässig ab.

Abwesenheiten sind im Einwilligungskatalog und in der Adapter-Allowlist
vorbereitet. Sie fehlen jedoch im aktuellen `FeatureKey`, besitzen kein
Importmodell und keine Darstellung. Das Eintragen oder Melden einer
Abwesenheit ist ausdrücklich nicht implementiert; der Adapter ist bisher
read-only.

## Aktueller Betriebsstand

- Öffentliche URL: `https://5e.eventmonitor.eu`
- Loginseite und WebUntis-Seite antworteten am 31. August 2026 über HTTPS mit
  Status 200.
- App-Container: `running` und `healthy`, Failing Streak 0.
- Image: `klasse-5e-app:0.2.0`.
- App-Prozess: UID/GID `10001:10001`.
- Root-Dateisystem des App-Containers: schreibgeschützt.
- Zugriff erfolgt über den globalen Caddy; die Anwendung veröffentlicht keinen
  eigenen produktiven Host-Port.
- `python manage.py check` im laufenden App-Container: ohne Fehler.

Die Produktionsimage enthält absichtlich keine Entwicklungsabhängigkeiten und
daher kein `pytest`. Das letzte eingecheckte Gesamtgate dokumentiert 76
bestandene App-Tests und 33 bestandene Vision-Tests. Nach den späteren UI- und
WebUntis-Korrekturen muss die vollständige aktuelle Testsuite in einem
reproduzierbaren Entwicklungs-/Testimage erneut ausgeführt werden.

Ein direktes `docker compose` aus einer neuen Shell benötigt weiterhin die
lokal injizierten Secret-Werte. Ohne diese bricht Compose bereits bei der
Variablenauflösung ab. Der laufende produktive Container ist davon nicht
betroffen. Geheimnisse dürfen für eine Übergabe an einen anderen Rechner nicht
in Git oder eine eingecheckte `.env`-Datei übernommen werden.

## Letzte Probleme und deren Status

| Problem | Ursache | Status |
|---|---|---|
| `/cms/` lieferte zunächst einen Serverfehler | unvollständiger Laufzeit-/Routingzustand | behoben |
| Privilegiertes Konto landete ohne nutzbaren Weg vor der MFA-Sperre | MFA-Einrichtung wurde durch die eigene Schutzlogik abgefangen | mit gezielter MFA-Einrichtungsroute behoben |
| Reauthentifizierung erzeugte zu viele Weiterleitungen | Middleware behandelte erforderliche Allauth-Routen nicht als Ausnahme | behoben |
| Login und MFA erschienen ungestaltet | Projekt-CSS und Allauth-Layouts waren nicht vollständig eingebunden | behoben und ausgerollt |
| Onboarding war formularartig und Datenschutzlink startete erneut bei Schritt 1 | fehlende erklärende Ebene und falsche Einbindung in den erzwungenen Ablauf | technisch behoben; qualitative UX-Abnahme bleibt offen |
| Trotz WebUntis-Aktivierung erschienen keine Termine | Phase 9A verwirft Fachantworten und importiert absichtlich noch nichts | offen; Hauptgegenstand von Phase 9B |
| Reales Elternkonto liefert beim aktuellen Synchronisationsweg `not_authorized` | derzeitiger JSON-RPC-/REST-Sitzungsaufbau entspricht nicht zuverlässig dem Browserablauf oder dem Konto fehlt der konkrete API-Endpunkt | offen; zuerst sicher diagnostizieren |
| Abwesenheiten können nicht gelesen oder gemeldet werden | nur Einwilligung und read-only Endpoint-Idee vorhanden; Modell, Präferenz und Schreibablauf fehlen | offen |
| Sporadische systemweite DNS-Fehler bei Browser und Paketabrufen | AdGuard war einziger Windows-Resolver; zusätzlich war eine Tailscale-NRPT-Regel zeitweise beschädigt | behoben und nachgetestet |
| Paketinstallation/Teststart aus beliebiger Shell | notwendige lokale Secrets beziehungsweise Dev-Abhängigkeiten fehlen dort | bekannte Betriebsgrenze, sauber über Testimage/Secret-Injektion lösen |

## DNS- und Netzwerkreparatur vom 30. August 2026

- Tailscale wurde von `1.102.2` auf `1.102.3` aktualisiert.
- Die Tailscale-DNS-Integration wurde kontrolliert deaktiviert und neu
  aktiviert; Windows erzeugte die NRPT-Regeln neu.
- Der Windows-DNS-Cache wurde geleert.
- Windows verwendet jetzt AdGuard `192.168.178.61` primär und die FritzBox
  `192.168.178.1` sekundär.
- 360 aufeinanderfolgende DNS-Abfragen gegen Portal, PyPI, Python-Dateihost,
  GitHub und ChatGPT endeten mit 0 Fehlern.
- Nach der Reparatur traten im Prüfzeitraum keine neuen Windows-DNS-Ereignisse
  1014 oder 1023 auf.

Damit ist die Rechnerseite aktuell stabil. Eine vollständige Redundanz des
AdGuard-Dienstes selbst ist damit noch nicht bewiesen; die FritzBox stellt aber
einen funktionierenden zweiten Resolverpfad für Windows bereit.

## Offene Produkt- und Freigabegrenzen

- Verantwortliche Stelle, echte Kontaktangaben, Rechtsgrundlagen und mögliche
  Auftragsverarbeitung sind organisatorisch beziehungsweise rechtlich noch
  verbindlich zu klären.
- Die Biometrie-DSFA ist ein Entwurf und nicht fachlich freigegeben; Biometrie
  bleibt global aus.
- Das Portal ist technisch öffentlich erreichbar, aber nur für angemeldete und
  berechtigte Mitglieder nutzbar. Das ersetzt keine organisatorische
  Produktivfreigabe.
- WebUntis darf nur mit dem eigenen Elternkonto und nur für ein bestätigtes
  zugeordnetes Kind arbeiten. Ein gemeinsamer Schul- oder Klassenzugang ist
  weder vorhanden noch vorgesehen.
- Jede WebUntis-Datenart bleibt separat wählbar. Ein Schreibzugriff für eine
  Krankmeldung darf nicht stillschweigend aus einer Lesefreigabe folgen.
- Vollständiges Backup-/Restore-, Schuljahreswechsel- und Übergabegate der
  Phase 10 bleibt vor einem breiteren Betrieb erforderlich.

## Empfohlener nächster Schritt

Als Nächstes ist ausschließlich Phase 9B umzusetzen: den tatsächlichen
Elternkonto-Sitzungsablauf sicher nachvollziehen, die verfügbaren Kategorien
pro Konto/Kind ermitteln, echte Antworten in persönliche normalisierte Daten
überführen und sie im Dashboard/Kalender anzeigen. Abwesenheiten sind dabei
zunächst lesend zu integrieren. Eine Krankmeldung darf nur nach gesonderter
Capability-Prüfung und mit einem explizit bestätigten, sicheren Schreibablauf
hinzukommen.

Der ausführbare Arbeitsauftrag steht in
`docs/planning/Naechste-Codex-Aufgabe-Phase-9B.md`.
