# WebUntis Betrieb

Die Compose-App benötigt für diesen Adapter ausschließlich ausgehenden HTTPS-Zugriff auf `thgwob.webuntis.com`. Der normale Compose-Betrieb veröffentlicht keine Host-Ports. Der manuelle Abruf ist auf einen Lauf pro Klick, DB-Lock und zehn Minuten Mindestabstand begrenzt. Automatik bleibt aus, bis ein Administrator `SyncSchedule.enabled` aktiviert.

Beispiele (nur mit synthetischen Laufzeitgeheimnissen):

```text
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py sync_webuntis --automatic
```

Ein automatischer Tagesumfang beträgt bei fünf Beispielzeiten höchstens fünf Läufe je Verbindung; die Default-Konfiguration begrenzt zusätzlich auf zwei. Bei vielen Familien bleibt der Abruf pro Verbindung seriell und wird durch den Mindestabstand gedrosselt.
