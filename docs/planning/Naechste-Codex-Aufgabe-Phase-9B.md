# Nächste Codex-Aufgabe: Phase 9B – WebUntis-Elternkonto und persönlicher Import

Stand: 31. August 2026

## Auftrag

Setze Phase 9B vollständig um. Stelle den vorhandenen WebUntis-Adapter auf den
tatsächlichen, im Browser funktionierenden Elternkontoablauf des THG um,
importiere die ausdrücklich aktivierten Daten des bestätigten Kindes
idempotent und zeige sie ausschließlich den dafür berechtigten Personen an.

Der Auftrag umfasst außerdem eine belastbare Capability-Prüfung für
Abwesenheiten. Lesbare Abwesenheiten sollen persönlich und geschützt
angezeigt werden. Eine Abwesenheit/Krankmeldung darf nur dann aus dem
Klassenportal an WebUntis übermittelt werden, wenn der reale Elternaccount
diese Aktion technisch und organisatorisch tatsächlich erlaubt und der
verwendete Endpunkt sicher verifiziert wurde. Andernfalls muss die Oberfläche
transparent auf WebUntis verweisen und darf keine vorhandene Schreibfunktion
behaupten.

Arbeite selbstständig bis zum vollständigen Qualitätsgate, dokumentiere
Grenzen ehrlich, committe in kleinen nachvollziehbaren Schritten und pushe erst
nach erfolgreicher Abnahme auf den bestehenden Branch. Frage nicht nach
Erlaubnis für normale, reversible Arbeiten innerhalb dieses Auftrags.

## Vor Beginn vollständig lesen

1. `C:\Users\Bjoern\.homeops\codex-instructions.md`
2. `AGENTS.md`
3. `PROJECT.md`
4. `docs/Architecture.md`
5. `docs/DecisionLog.md`
6. `docs/Roadmap.md`
7. `docs/status/Projektstatus-2026-08-31.md`
8. `docs/integrations/WebUntis.md`
9. `docs/integrations/WebUntis-Betrieb.md`
10. `docs/integrations/WebUntis-Funktionsmatrix.md`
11. `docs/privacy/Datenschutz-WebUntis.md`
12. `docs/privacy/Einwilligung-WebUntis.md`
13. `docs/privacy/WebUntis-Pilotplan.md`
14. `docs/planning/WebUntis-Quellenspezifikation.md`
15. vorhandene WebUntis-, Schedule-, Onboarding-, Policy- und UI-Tests

## Verbindlicher Ausgangszustand

- `main` stand vor den Übergabedokumenten auf `3e33236` und entsprach
  `origin/main`.
- Die App ist unter `https://5e.eventmonitor.eu` erreichbar und der Container
  ist gesund.
- Eine anonymisierte Pilotverbindung existiert und ist als `ok` markiert.
- 13 Kategorien sind in der Laufzeitdatenbank aktiviert.
- Es existieren 0 importierte WebUntis-Stunden und 0 Hausaufgaben.
- Der jüngste Lauf endete mit `not_authorized`.
- `execute_run()` ruft Endpunkte auf, verwirft aber alle Fachantworten.
- `absences` existiert in der Client-Allowlist und im Einwilligungskatalog,
  fehlt jedoch als `FeatureKey`, Importmodell und UI-Funktion.
- Der aktuelle Client ist read-only und besitzt keine Krankmeldungsfunktion.
- Zugangsdaten funktionieren nach Aussage des Betreibers im normalen
  WebUntis-Browserlogin. Das beweist nicht, dass der alte JSON-RPC-Endpunkt für
  dieses Elternkonto freigegeben ist.

## Nicht verhandelbare Regeln

- Jedes Elternkonto verwendet ausschließlich seinen eigenen WebUntis-Zugang.
- Es gibt keinen gemeinsamen Schul-, Klassen- oder Integrationszugang.
- Die Verarbeitung bleibt auf bestätigte, aktuell berechtigte Kinder begrenzt.
- Niemals anhand eines Vornamens oder einer unsicheren Ähnlichkeit zuordnen.
- Bei keiner oder mehrdeutiger Quellzuordnung sicher stoppen.
- Keine Zugangsdaten, Cookies, JWTs, Session-IDs, vollständigen URLs mit Token,
  Rohantworten oder personenbezogenen Inhalte ausgeben oder loggen.
- Keine echten Schuldaten in Git, Fixtures, Snapshots oder Dokumentation.
- Vorhandene lokale Secrets nur über die bestehende Geheimnisverwaltung oder
  die bereits verschlüsselte Laufzeitverbindung verwenden.
- Keine entschlüsselten Werte in Prozessargumente, Shell-Ausgabe oder
  dauerhafte Dateien schreiben.
- Host-Allowlist und HTTPS-Zwang beibehalten.
- Keine beliebigen RPC-/REST-Aufrufe und kein öffentliches Raw-Call-Werkzeug.
- Alle freiwilligen Kategorien bleiben standardmäßig aus und benötigen eine
  aktuelle, getrennte Einwilligung.
- Normale Seitenaufrufe lösen keinen externen Abruf aus.
- Alte gültige Daten bleiben bei temporären Quellfehlern erhalten und werden
  sichtbar als veraltet gekennzeichnet.
- Keine automatische endgültige Aktion in WebUntis, keine stillen
  Schreibversuche und keine Wiederholung eines Schreibrequests ohne
  nachgewiesene Idempotenz.

## Arbeitspaket 1: Reproduzierbare Diagnose des Elternkontoablaufs

1. Reproduziere `not_authorized` mit dem vorhandenen verschlüsselten
   Pilotzugang, ohne Geheimnisse oder Antwortinhalte auszugeben.
2. Trenne sauber zwischen:
   - Login nicht möglich,
   - Login möglich, Endpoint nicht berechtigt,
   - zusätzlicher JWT-/Cookie-/CSRF-Schritt erforderlich,
   - MFA/SSO erforderlich,
   - Endpoint oder Pfad nicht mehr gültig,
   - Kind für diesen Endpoint nicht korrekt aufgelöst.
3. Untersuche den tatsächlichen Browserablauf in einer bestehenden
   angemeldeten WebUntis-Sitzung oder mit einer lokal isolierten
   Entwicklungsanalyse. Erfasse ausschließlich Methode, Host, Pfad,
   erforderliche Headerarten, Statusklasse und ein anonymisiertes
   Schemaprofil. Keine Nutzdaten oder Token in Git/Logs übernehmen.
4. Prüfe vorrangig offizielle beziehungsweise von der Weboberfläche selbst
   verwendete Schnittstellen. Browser-Scraping von HTML ist nur der letzte
   Ausweg und bedarf einer neuen dokumentierten Entscheidung.
5. Vergleiche den ermittelten Ablauf mit der festgehaltenen Upstream-Referenz
   `kohlsalem/untis-mcp` am Commit
   `a40b237aab03b5ece6b62956854315dc3c25c3cb`, ohne MCP-/Claude-Laufzeit oder
   einen beliebigen Raw-Call zu übernehmen.
6. Ergänze eine datensparsame Diagnose-/Capability-Struktur. Zulässig sind nur
   Kategorien, Status, Anzahl, Schema-/Versionsfingerprint und Zeitpunkt.

Abnahme: Die Ursache von `not_authorized` ist reproduzierbar klassifiziert,
und eine synthetisch getestete, eng begrenzte Authentisierungsstrategie ist
implementiert. Ein Realtest darf erst danach und ausschließlich gegen das
bestätigte Pilotkind erfolgen.

## Arbeitspaket 2: Sichere Eltern-Kind-Auflösung

1. Ermittle die vom Elternkonto tatsächlich bereitgestellten Kinder über den
   authentisierten Quellkontext.
2. Ergänze eine explizite lokale Zuordnung zwischen externer opaque Kinder-ID
   und der bereits ausgewählten bestätigten lokalen Person.
3. Speichere keine unnötigen Namen als technische Schlüssel.
4. Fordere eine einmalige bewusste Bestätigung, wenn erstmals eine externe ID
   gebunden wird.
5. Verweigere Abruf und Import bei fehlender, abgelaufener oder widerrufener
   Sorgebeziehung sowie bei mehrdeutiger Quellzuordnung.
6. Prüfe die Beziehung erneut unmittelbar vor jedem Abruf und vor jeder
   möglichen Schreibaktion.

Abnahme: Konten mit keinem, einem und mehreren Kindern sind synthetisch
getestet; ein Elternkonto kann nie Daten eines nicht bestätigten Kindes
importieren oder sehen.

## Arbeitspaket 3: Kategorien und Capability-Status

1. Bringe `FeatureKey`, `CAPABILITIES`, Einwilligungskatalog und Oberfläche in
   eine konsistente Zuordnung.
2. Nimm mindestens folgende separat steuerbare Kategorien auf:
   - Stundenplan,
   - erweiterte Stundendetails,
   - Änderungen/Entfall,
   - Prüfungen,
   - Hausaufgaben,
   - Ferien,
   - Stundenraster,
   - Fächer, Räume und freigegebene Lehrkraftbezeichnungen,
   - Schuljahr und Statusdaten,
   - Abwesenheiten lesend,
   - persönliche Mitteilungen nur, wenn tatsächlich freigegeben und fachlich
     benötigt.
3. Speichere je Verbindung/Kategorie einen real ermittelten Status:
   `available`, `not_authorized`, `unsupported`, `temporarily_unavailable`
   oder `not_checked`.
4. Ein aktivierter Wunsch darf in der UI nicht als technisch verfügbar
   dargestellt werden, solange die Capability-Prüfung dies nicht bestätigt.
5. Zeige eine verständliche Erklärung und den letzten erfolgreichen
   Prüfzeitpunkt, aber keine externen Fehlermeldungen oder Inhalte.

## Arbeitspaket 4: Normalisierung und idempotenter Import

1. Definiere kleine typisierte DTOs zwischen Client und Django-Schicht.
2. Validiere externe Antworten streng und stoppe bei unbekanntem Schema sicher.
3. Normalisiere nur aktivierte und aktuell erlaubte Kategorien.
4. Nutze stabile externe IDs oder dokumentierte fachliche Fingerprints plus
   Inhaltsrevision. Derselbe Abruf darf keine Duplikate erzeugen.
5. Implementiere transaktionssicheren Änderungsvergleich mit Zählung von neu,
   geändert, unverändert und entfernt/veraltet.
6. Speichere Quell- und Abrufzeitpunkt, Schema-/Adapterversion und eine
   geeignete Löschfrist.
7. Persönliche WebUntis-Daten dürfen nicht ungeprüft in klassenweit sichtbare
   `schedule.CalendarEntry`- oder `TimetableEntry`-Datensätze geschrieben
   werden. Ergänze eine klare persönliche Import-/Leseschnittstelle oder nutze
   klassenweite Modelle nur für nachweislich nicht persönliche Daten.
8. Bei Fehlern bleiben vorherige Daten erhalten, werden aber mit
   Aktualitätsstatus angezeigt.
9. Widerruf, Verbindungsentfernung oder Verlust der Sorgeberechtigung löscht
   beziehungsweise sperrt alle abhängigen normalisierten Daten sofort und
   idempotent.

Mindestens abzubilden:

- Regelunterricht, Änderung, Entfall, Prüfung, Ferien und Zusatzereignis;
- Fach, Beginn/Ende, Raum und zulässige Lehrkraftbezeichnung;
- Hausaufgabe mit Aufgabe-/Fälligkeitsdatum und freigegebenem Text;
- Abwesenheit mit Zeitraum, Status und nur den fachlich nötigen Angaben.

## Arbeitspaket 5: Persönliche Anzeige

1. Zeige importierte Daten auf Dashboard, Tages-/Wochenansicht und
   WebUntis-Statusseite ausschließlich für das verbundene bestätigte Kind.
2. Trenne Quellen visuell: manuell gepflegter Klassenkalender und persönliche
   WebUntis-Daten dürfen nicht verwechselt werden.
3. Zeige Quelle, letzten erfolgreichen Abruf, Alter der Daten und einen
   verständlichen Fehler-/Veraltet-Hinweis.
4. Entfallene Stunden bleiben sichtbar und werden als Entfall markiert.
5. Verwende Status nicht ausschließlich über Farben, sondern zusätzlich Text
   und Symbol.
6. Smartphone-Ansicht zuerst; zusätzlich 320 bis 1440 Pixel, 200 Prozent Zoom,
   Tastatur, Screenreader und Forced Colors prüfen.
7. Ergänze ein synthetisches Beispiel für ein Konto ohne bestätigte
   Kindzuordnung, damit dieser Zustand ohne echte Daten abgenommen werden kann.

## Arbeitspaket 6: Abwesenheit/Krankmeldung

Behandle Lesen und Schreiben strikt getrennt.

### Lesen

- Abwesenheiten benötigen eigene Einwilligung und Capability.
- Die Anzeige ist ausschließlich persönlich für das bestätigte Kind.
- Keine Abwesenheitsdetails in Push, Audit-Metadaten oder technischen Logs.
- Widerruf entfernt die importierten Abwesenheiten nach dem dokumentierten
  Löschweg.

### Schreiben

1. Ermittle zuerst, ob der Elternaccount in WebUntis selbst eine Abwesenheit
   anlegen darf und welcher von der Weboberfläche verwendete oder offiziell
   dokumentierte Endpunkt dafür zuständig ist.
2. Wenn dies nicht eindeutig und stabil verifiziert werden kann, implementiere
   keinen Schreibzugriff. Zeige stattdessen einen klaren Link zur passenden
   WebUntis-Funktion.
3. Falls die Funktion verifiziert ist, erstelle eine gesonderte
   Architektur-/Sicherheitsentscheidung und einen eigenen Opt-in. Eine
   Lesefreigabe genügt nicht.
4. Erforderlich sind mindestens:
   - erneute Prüfung von Benutzer, Mitgliedschaft, Sorgebeziehung und Kind;
   - CSRF-Schutz und POST-only;
   - Beginn, Ende, ganztägig/zeitweise und nur notwendige optionale Angabe;
   - Zusammenfassungsseite mit ausdrücklicher Bestätigung;
   - serverseitige Zeit- und Plausibilitätsvalidierung;
   - eindeutiger clientseitiger Vorgangsschlüssel gegen Doppelklicks;
   - keine automatische Wiederholung eines unklar beantworteten Requests;
   - Erfolg erst nach eindeutiger Quellbestätigung;
   - minimiertes Audit ohne Krankheitsgrund oder Freitext;
   - klare Behandlung von Timeout mit Status „Ausgang unklar“ statt
     fälschlicher Erfolgsmeldung;
   - Tests gegen IDOR, fremde Kinder, Replay und doppelte Übermittlung.
5. Krankheitsdiagnosen oder medizinische Details werden nicht verlangt und
   nicht gespeichert.

## Arbeitspaket 7: Synchronisation und Betrieb

- Behalte DB-Lock, Idempotency-Key, Mindestabstand, begrenztes Retry und
  neutrale Fehlerklassen bei.
- Korrigiere den aktuellen Idempotency-Key der Webform so, dass ein späterer
  legitimer manueller Lauf nicht dauerhaft denselben Schlüssel wiederverwendet.
- Read-only Abrufe dürfen begrenzt wiederholt werden; Schreiboperationen nicht.
- Automatische Synchronisation bleibt standardmäßig deaktiviert.
- Aktiviere keinen neuen Worker, Redis, WebSocket-Dienst oder Microservice.
- Dokumentiere einen reproduzierbaren Scheduler-Aufruf, ohne ihn ungefragt
  global einzurichten.
- Ergänze Health-/Diagnoseinformationen ohne personenbezogene Inhalte.
- Aktualisiere Löschung, Backup/Restore und Schuljahreswechsel für die neuen
  persönlichen Importdaten.

## Verpflichtende Tests

Mindestens automatisiert abdecken:

- alter JSON-RPC-Login erfolgreich und abgelehnt;
- tatsächlich gewählter Elternkontoablauf erfolgreich, abgelehnt, abgelaufen
  und MFA/SSO-pflichtig;
- keine Token/Cookies/Passwörter in Exceptions oder Logs;
- Host-Allowlist, HTTPS und Endpoint-Allowlist;
- Konto ohne Kind, ein Kind, mehrere Kinder und mehrdeutige Zuordnung;
- fremdes oder nicht mehr bestätigtes Kind vollständig gesperrt;
- jede Kategorie standardmäßig aus;
- Capability verfügbar, nicht berechtigt, nicht unterstützt und temporär
  gestört;
- strikte Schemavalidierung und sicherer Stopp bei unbekannter Antwort;
- idempotenter Erstimport, Wiederholung, Änderung und Entfernung;
- persönliche Isolation in Dashboard, Kalender, Detailansicht und Export;
- Widerruf und Verbindungsentfernung löschen/sperren abhängige Daten;
- temporärer Fehler erhält letzte Daten und markiert sie als veraltet;
- Abwesenheit lesen nur mit eigener Freigabe;
- optionaler Schreibablauf: Fremdkind, CSRF, Doppelklick, Replay, Timeout,
  unklarer Ausgang und bestätigter Erfolg;
- keine sensiblen Push-Inhalte und keine Push-Dopplungen;
- Migrationen vorwärts sowie Lösch-/Restore-Szenario;
- responsive und barrierefreie Zustände mit synthetischen Daten.

Reale Antworten dürfen nicht als Fixture gespeichert werden. Erzeuge
vollständig synthetische, strukturgleiche Testdaten ohne echte Namen, IDs,
Texte, Zeiten oder sonstige Schuldaten.

## Qualitätsgate

Vor Abschluss vollständig ausführen und Ergebnis dokumentieren:

1. Python-Kompilierung.
2. Django-Systemprüfung im App- beziehungsweise Testimage.
3. `makemigrations --check --dry-run`.
4. vollständige App-Pytest-Suite mit Dev-Abhängigkeiten.
5. relevante Vision- und Web-Push-Suiten, soweit durch Änderungen berührt.
6. Ruff Lint und Formatprüfung.
7. Docker-Build ohne Cache, soweit reproduzierbar erforderlich.
8. Migration und Start gegen eine gesicherte Testdatenbank.
9. manueller synthetischer UI-Smoke-Test.
10. kontrollierter Realtest ausschließlich mit der bestehenden
    Pilotverbindung und dem bestätigten Pilotkind.
11. Wiederholter Realabruf zur Prüfung der Idempotenz.
12. Prüfung, dass Git, Logs, Testausgaben, Screenshots und Dokumentation keine
    Geheimnisse oder personenbezogenen WebUntis-Inhalte enthalten.
13. `git diff --check`, Secret-Scan und Dokumentlinkprüfung.
14. öffentlicher HTTPS-Smoke-Test nach Deployment.

Wenn ein Realtest technisch nicht möglich ist, darf das Gate nicht als
vollständig bestanden bezeichnet werden. Dokumentiere dann genaue neutrale
Fehlerklasse, bereits geprüfte Hypothesen und den kleinsten nächsten Schritt,
ohne Zugangsdaten oder Inhalte offenzulegen.

## Ergebnisdateien und Übergabe

Mindestens aktualisieren:

- WebUntis-Client, Adapter, Modelle, Migrationen, Services, Views und Templates;
- persönliche Schedule-/Dashboard-Integrationsgrenze;
- synthetische Tests;
- `docs/integrations/WebUntis.md`;
- `docs/integrations/WebUntis-Funktionsmatrix.md`;
- `docs/integrations/WebUntis-Betrieb.md`;
- `docs/privacy/Datenschutz-WebUntis.md`;
- `docs/privacy/WebUntis-Pilotplan.md`;
- `docs/DecisionLog.md`;
- `docs/Roadmap.md`;
- einen neuen Qualitätsbericht für Phase 9B.

Der Abschlussbericht nennt:

- implementierten Authentisierungsweg;
- real verfügbare und nicht verfügbare Kategorien;
- Import- und Änderungszahlen ausschließlich anonymisiert;
- Status der lesenden Abwesenheiten;
- eindeutige Aussage, ob Krankmeldungen im Portal möglich sind;
- Testzahlen und Betriebsprüfung;
- Migrationen, Löschung und Restore;
- bekannte Grenzen;
- Commit-IDs und Push-Status.

Keine personenbezogenen Pilotdaten, Geheimnisse oder WebUntis-Rohantworten
dürfen Teil dieser Übergabe sein.
