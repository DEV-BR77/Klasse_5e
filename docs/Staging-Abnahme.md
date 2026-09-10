# Staging-Abnahme vor dem Produktivstart

Diese Umgebung ist ausschließlich für die technische und fachliche Abnahme.
Sie verwendet weder die Produktivdatenbank noch Produktiv-Uploads und ersetzt
niemals den bestehenden Dienst auf `klassid.de`.

## Verbindliche Trennung

- Eigene HTTPS-Subdomain, DNS-Eintrag und Caddy-Route; der Zielname wird erst
  vor der Infrastrukturfreigabe festgelegt.
- Eigenes Compose-Projekt, eigene PostgreSQL-, Medien- und Vision-Volumes.
- Eigene Django-, Datenbank-, Verschlüsselungs-, Vision- und VAPID-Schlüssel.
- `APP_BASE_URL`, `DJANGO_ALLOWED_HOSTS` und
  `DJANGO_CSRF_TRUSTED_ORIGINS` enthalten ausschließlich den Staging-Host.
- `TEMPORARY_ADMIN_MFA_BYPASS=0`; alle administrativen Rollen testen MFA.
- Keine Kopie realer Familien-, Chat-, Foto- oder Zugangsdaten. Nur
  dokumentierte synthetische Abnahmekonten verwenden.

## Reproduzierbare Konfiguration

`compose.staging.yaml` ist eine nicht aktive Ergänzung zur bestehenden Compose-
Datei. Sie setzt einen eigenen Projektnamen sowie eigene PostgreSQL-, Medien-
und Vision-Volumes durch; der gemeinsame Reverse-Proxy bleibt der einzige
bewusst geteilte Dienst. Die lokale Datei `.env.staging` entsteht aus
`.env.staging.example`, bleibt von Git ausgeschlossen und enthält ausschließlich
neu erzeugte Staging-Secrets.

Vor dem ersten Start prüft der folgende reine Konfigurationsbefehl sowohl die
Compose-Auflösung als auch die Trennung vom Produktivhost. Er startet keine
Container und ändert weder DNS noch Caddy:

```powershell
.\tools\Test-StagingConfiguration.ps1
```

Erst danach wird die freigegebene Caddy-Route für den konkret benannten
Staging-Host gesetzt und die Umgebung mit beiden Compose-Dateien gestartet:

```powershell
docker compose --env-file .env.staging -f compose.yaml -f compose.staging.yaml up -d --build
```

## Technisches Gate

Vor einer externen Geräteabnahme müssen nachweislich erfolgreich sein:

1. `tools/Test-Klasse5e.ps1 -AppOnly` mit JUnit-Ergebnis ohne Fehler.
2. `manage.py check`, `manage.py makemigrations --check --dry-run` und der
   Tailwind-Build.
3. Container-Healthchecks für App, PostgreSQL und Vision sowie ein HTTPS-
   Aufruf von `/health/` über den Staging-Host.
4. Migrationslauf gegen die leere Staging-Datenbank mit anschließendem
   Smoke-Test für Anmeldung, MFA, Abmeldung und Passwortwechsel.

## Fachliche Abnahme

Die Geräteabnahme erfolgt danach mit Desktop, iPhone und Android und deckt
mindestens Start, Kalender, Chat, Kontaktliste, Familie, Profil, WebUntis-
Einrichtung, Rechtewechsel und den Widerruf von Kontaktfreigaben ab. Für jeden
Test wird der eingeloggte Nutzer und die sichtbare Personen-/Kindauswahl
protokolliert. Erst ein vollständig grünes Protokoll erlaubt einen separaten
Produktiv-Rollout.
