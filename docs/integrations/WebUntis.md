# WebUntis Phase 9A

Stand: 27.08.2026. Der Pilot ist lesend, konto- und kindbezogen und standardmäßig nicht automatisch aktiv.

## Technische Referenz

Geprüft wurde `kohlsalem/untis-mcp` am Commit `a40b237aab03b5ece6b62956854315dc3c25c3cb` (README, `src/untis_mcp/api.py`, Server, Tests, `pyproject.toml`, LICENSE). Das Projekt nutzt einen kombinierten JSON-RPC-/REST-Client (`httpx`, JWT und JSESSIONID), bietet Eltern-Kinderauflösung und die unten genannten Datenbereiche. MCP-Server, Claude-Konfiguration, `untis_raw_call`, Daily-Reports und globale `.env`-Zugänge wurden ausdrücklich nicht übernommen. Die Upstream-Lizenz ist die Unlicense; der vollständige Lizenztext steht in `WebUntis-Lizenz-Unlicense.txt`.

Die Anwendung verwendet stattdessen `klasse5e.webuntis.client.WebUntisClient`: HTTPS, Host-Allowlist `thgwob.webuntis.com`, feste RPC-/REST-Allowlist, Timeout, maximal ein Backoff-Retry, Rate-Limit-Klassifikation und flüchtige Tokens. Rohantworten werden nicht gespeichert oder geloggt.

## Zugang und Datenschutz

Pro Elternkonto und bestätigtem Kind existiert höchstens eine Verbindung. Voraussetzung sind eine aktuelle, bestätigte, rechtliche Sorgebeziehung und Profilfreigabe. Zugangsdaten liegen als Fernet-Ciphertext in PostgreSQL; der Schlüssel wird ausschließlich über `WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY` aus `secret://klasse-5e/webuntis/credential-encryption-key` bereitgestellt. Benutzername/Passwort-Referenzen für den Pilot sind `secret://klasse-5e/webuntis/bjoern/username` und `secret://klasse-5e/webuntis/bjoern/password`. Werte werden nie an Browser, Logs, Audit-Metadaten oder Git zurückgegeben.

Persönliche Kategorien sind aus. Die Seite „WebUntis-Verbindung“ bietet Einrichtung, Einzel-Freigaben, „Aktuell prüfen“, Test und Entfernung. Entfernen löscht Verbindung, Freigaben und abhängige normalisierte Daten idempotent.

## Synchronisierung

Normale Seitenaufrufe synchronisieren nie. „Aktuell prüfen“ startet genau einen serverseitig begrenzten Lauf mit Idempotency-Key, DB-Lock und mindestens zehn Minuten Abstand. Automatische Läufe sind standardmäßig aus; ein Admin kann unter Django-Admin `SyncSchedule` verständliche Uhrzeiten (z. B. `06:00`) und Schultag-/Ferienregeln konfigurieren. Ein geplanter Aufruf erfolgt ausschließlich über `manage.py sync_webuntis --automatic`; es wird kein Worker, Redis oder externer Scheduler eingeführt.

Fehler werden als Kategorie gespeichert, nicht als externe Fehlermeldung. Bei temporären Fehlern bleiben alte Daten erhalten. Push darf nur aus fachlichen Änderungen entstehen; dieser Pilot erzeugt keine Push-Payloads aus persönlichen Inhalten.

## Lokaler Pilot

Ein realer Abruf ist nur nach lokaler Einrichtung der drei Secret-Referenzen zulässig. Mila darf ausschließlich über die bestätigte Beziehung ausgewählt werden. Ohne nachweisbare lokale Zuordnung bleibt der Pilotstatus „noch nicht geprüft“; es werden keine Namen anhand eines Vornamens geraten.

