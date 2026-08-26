# Betrieb Phase 2

Der normale Start erfolgt als Compose-Projekt `klasse-5e` und veröffentlicht
keinen Host-Port. Secrets werden als Prozessumgebung aus der lokalen
Geheimnisverwaltung gesetzt: `secret://projects/klasse-5e/postgres_password`,
`secret://projects/klasse-5e/django_secret_key` und
`secret://projects/klasse-5e/vision_service_token`.

Der Development-Override bindet App `127.0.0.1:8085` und Vision
`127.0.0.1:8091`. PostgreSQL bleibt intern. Produktion bindet später nur die
App an das externe Caddy-Netz; HomeInfrastructure wird dabei nicht kopiert.

Persistenz liegt in `klasse-5e-postgres-data`, `klasse-5e-app-media`,
`klasse-5e-vision-data` und `klasse-5e-vision-models`. Ein Backup umfasst
`pg_dump`, Medienvolume und den dokumentierten Vision-Export. Restore erfolgt
in frische Volumes, anschließend Migration, Healthchecks und Funktionstest.
# Backup und Restore

PostgreSQL wird mit `pg_dump --format=custom` aus `klasse-5e-db` exportiert;
das Medienvolume wird getrennt als Archiv gesichert. Vision-Daten folgen dem
Ablauf in `services/vision/docs/BACKUP_RESTORE.md`. Ein Restore verwendet ein
frisches Volume, `pg_restore`, danach `manage.py migrate`, Healthchecks und
einen Funktionstest. Secrets sind nie Teil dieser Archive und werden am Ziel
neu aus `secret://projects/klasse-5e/...` bereitgestellt.

Der Abnahmelauf vom 25.08.2026 stellte einen Custom-Format-Dump in einem frisch
erzeugten PostgreSQL-17.6-Volume wieder her und fand dort 232 angewandte
Migrationszeilen. Nach Neustart des regulären Datenbank- und App-Containers war
dieselbe Anzahl vorhanden. Dieser lokale synthetische Test ersetzt nicht die
vor Produktivbetrieb geforderte Umzugsübung auf einem zweiten Docker-Host.

## Galerie-Medien

Galerien liegen im Volume `klasse-5e-app-media`; temporäre Uploads gehören
nicht ins Backup. Der Export archiviert das Volume und erzeugt ein SHA-256-
Dateimanifest. Nach Restore werden Datenbank, Volume, Manifest, geschützter
Thumbnail-/Bildabruf und Berechtigungen gemeinsam geprüft. Aufbewahrung wird
mit `manage.py purge_expired_photos` als Dry-Run und explizit mit `--delete`
vollzogen.

Der Phase-5-Abnahmelauf vom 25.08.2026 restaurierte einen PostgreSQL-Dump mit
synthetischem Galerie-/Fotodatensatz und drei bereinigte Medienableitungen in
frische Volumes. Die Datenbank enthielt danach den erwarteten Datensatz; die
SHA-256-Werte von Anzeige, Thumbnail und Download stimmten vor und nach Restore
überein. Ein Containerneustart erhielt Datensatz und Medienvolume.

## Biometrie-Betrieb

`BIOMETRIC_SEARCH_ENABLED` bleibt ohne explizite Setzung `0`. Für den
freigegebenen technischen Test wird es kontrolliert auf `1` gesetzt; das
Vision-Diensttoken stammt ausschließlich aus
`secret://projects/klasse-5e/vision_service_token`. Vision bleibt ohne
Host-Port im internen Netz.

`manage.py purge_biometric_data` ist ein Dry-Run. Mit `--execute` entfernt es
fällige Vision-Quelldateien und anschließend abgelaufene, nicht mehr benötigte
Zuordnungen. `manage.py reconcile_biometric_consents` sperrt Profile mit
fehlender oder widerrufener Zustimmung und wiederholt ausstehende Remote-
Löschungen. Beide Befehle sind mindestens täglich auszuführen; so wird die
24-Stunden-Frist eingehalten. Bei dokumentierter manueller Prüfung darf die
Quelle höchstens sieben Tage verbleiben.

Bei Testende oder Abschaltung wird zuerst der Feature-Schalter auf `0` gesetzt
und danach `manage.py disable_biometrics` geprüft und explizit mit `--execute`
ausgeführt. Fehlgeschlagene Collections verbleiben sichtbar als
`deletion_pending` und werden erneut verarbeitet.

Das Vision-Volume ist biometrischer Sicherungsbestand. Alte Backups können bis
zum Ende ihrer verschlüsselten Aufbewahrungsfrist bereits widerrufene Daten
enthalten und müssen beim Restore unmittelbar durch Consent-Abgleich und Purge
bereinigt werden. Ein unverschlüsselter Export ist unzulässig.

Der Phase-6-Abnahmelauf vom 26.08.2026 baute App und Vision neu, migrierte vier
Biometrie-Migrationen in einem frischen PostgreSQL-Volume und startete App,
PostgreSQL und Vision gesund ohne Host-Port. Nach einem vollständigen Neustart
blieben die Migrationen vorhanden. Ein Custom-Format-Dump wurde in ein zweites
frisches PostgreSQL-17.6-Volume restauriert; alle fünf biometrischen Tabellen
einschließlich Referenzen waren vorhanden. Der Vision-Backup-/Restore-Test
lief zusätzlich mit der vollständigen Vision-Suite erfolgreich.
