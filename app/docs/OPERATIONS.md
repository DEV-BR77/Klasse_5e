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
