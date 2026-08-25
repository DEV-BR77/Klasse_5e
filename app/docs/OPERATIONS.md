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
