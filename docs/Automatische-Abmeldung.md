# Automatische Abmeldung

Stand: 08.09.2026. Jede authentifizierte KlassID-Sitzung besitzt eine zentrale
Inaktivitätsgrenze. Der Standard beträgt 15 Minuten. Nach Ablauf ohne Bedienung
endet die Sitzung, der Browser zeigt wieder die Anmeldung und der Server
verweigert beim nächsten Zugriff den bisherigen Zugang.

Portaladministratoren finden die Einstellung unter **Verwaltung → Automatische
Abmeldung**. Erlaubt sind 1 bis 120 ganze Minuten. Die Einstellung gilt global
für alle Klassen, Schulen, Rollen und Geräte; sie lässt sich nicht je Klasse
abschwächen. Jede Änderung erzeugt ein Audit-Ereignis ohne personenbezogene
Inhalte außer dem authentisierten Administrator.

Die Frist wird durch konkrete Bedienung (`pointerdown`, Tastatureingabe oder
Berührung) erneuert. Reines Anzeigen, Laden im Hintergrund oder Chat-Polling
verlängern sie nicht. Der Browser meldet sich am Ablauf per CSRF-geschütztem
Endpunkt ab und leitet zur Anmeldung weiter. Unabhängig davon speichert Django
das Sitzungsablaufdatum und die Middleware prüft den Zeitpunkt auf jeder
Anfrage. Das schützt auch, wenn ein Browser-Timer etwa bei einem verlorenen
oder gesperrten Gerät nicht mehr ausgeführt wird.

Die Konfiguration liegt als globaler `PortalConfigurationKey`
`session_idle_timeout_minutes` vor. Migration `core.0025` legt ihn mit dem
Default 15 an. Fehlt der Konfigurationseintrag während einer Migration oder ist
er ungültig, greift sicherheitshalber weiterhin der Default. Ein Zurückrollen
auf `core.0024` entfernt nur die Konfigurationsdefinition; die bestehende
Sitzungslogik der vorherigen Version kennt den Wert nicht mehr. Vor einem
produktiven Migrationsrollback gelten der vorhandene Backup-/Restore-Prozess
und ein kontrollierter Wartungszeitraum.

Abnahme: `pytest app/tests/test_idle_session_timeout.py` prüft Standard,
Administrationsrechte, Grenzen, Audit, serverseitiges Ablaufen,
Hintergrund-Polling und den CSRF-geschützten Browser-Logout. Der kombinierte
Regressionslauf deckt zusätzlich Anmeldung, Sitzungswiderruf, MFA, Onboarding,
Chat und Portalverwaltung ab.
