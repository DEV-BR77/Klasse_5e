# Backup und Restore

`scripts/backup.py --data DATA_DIR --models MODEL_DIR --manifest MANIFEST
--output BACKUP_DIR` erstellt über die SQLite-Backup-API
einen konsistenten Dump, kopiert erforderliche Imports/Crops, das
Modellmanifest sowie nicht geheime Konfiguration und schreibt Prüfsummen,
Schema-Revision und die benötigte Secret-Referenz. Tokens und Schlüssel werden
nicht gesichert.

`scripts/restore.py --backup BACKUP_DIR --target EMPTY_DATA_DIR` prüft zuerst
alle Prüfsummen und
stellt nur in ein leeres Ziel wieder her. Danach: Modellpaket anhand Manifest
prüfen, Migration ausführen, Compose starten, Healthcheck und Funktionstest
ausführen und erst dann den Reverse Proxy umschalten.

Portabler Ablauf: `backup → Integritätsprüfung → Übertragung → restore →
Migration → Start → Healthchecks → Funktionstest → Proxy-Umschaltung`.
Alte verschlüsselte Backups können gelöschte biometrische Daten bis zum Ablauf
der festgelegten Backup-Frist enthalten und müssen dann ebenfalls gelöscht
werden. Ein Produktivstart setzt einen erneut auf frischem Docker-Host geübten
Restore voraus.

Die Skripte sind im Image enthalten und benötigen keine Host-Python-Installation.
Ein Betreiber bindet ein geschütztes relatives Exportverzeichnis nur für den
jeweiligen `docker compose run --rm`-Aufruf unter `/backup` ein. Restore erfolgt
analog in ein frisches, leeres Datenvolume; niemals in das aktive Volume.
