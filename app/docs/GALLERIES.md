# Geschützte Galerien (Phase 5)

Galerien gehören genau einer Klasse und einem Schuljahr; optional einem Event
derselben Klasse. Administratoren und Redakteure verwalten Galerien,
Event-Organisatoren ausschließlich die ihres Events. Zugriff setzt aktuelle
Klassenmitgliedschaft beziehungsweise eine berechtigte Klassenrolle voraus.

Uploads sind auf JPEG/PNG, 20 MB, 40 Megapixel und 25 Dateien je Aktion
begrenzt. Pillow decodiert und codiert vollständig neu. Orientierung wird
angewendet; EXIF, GPS, IPTC/XMP, Profile und andere Zusatzdaten werden nicht
übernommen. Pfade verwenden zufällige Photo-IDs. HEIC und ZIP sind nicht
unterstützt.

Der Uploader erklärt manuell: keine erkennbare Person, nur Erwachsene,
bekannte Klassenpersonen oder unklare Personen. Unklare Personen blockieren
Veröffentlichung. Für jede bekannte Person müssen aktuelle, widerspruchsfreie
Einwilligungen für Veranstaltungsfoto und manuelle Zuordnung vorliegen;
Download prüft zusätzlich die Download-Einwilligung. Widerruf sperrt Abruf
unmittelbar. Ein Uploader kann niemals für fremde Personen zustimmen.

Jedes Foto beginnt `pending`. Nur Moderatoren veröffentlichen, lehnen ab,
fordern Klärung, blenden aus oder löschen. Datenschutz-/Zustimmungsmeldungen
blenden vorsorglich aus. Uploader können eigene Fotos zurückziehen.

Alle Varianten werden durch Django nach Berechtigungsprüfung mit `private,
no-store` und `nosniff` ausgeliefert. Download ist standardmäßig aus. Es gibt
keine `MEDIA_URL`, öffentlichen Links oder Caddy-Direktpfade. Screenshots
können technisch nicht zuverlässig verhindert werden.

`python manage.py purge_expired_photos` ist Dry-Run und gibt nur opaque IDs
aus; `--delete` löscht Dateien und Bezüge idempotent. Standardaufbewahrung ist
Schuljahresende plus 30 Tage. Backups umfassen PostgreSQL und Medienvolume mit
SHA-256-Manifest, aber keine temporären Uploads oder Secrets.

Phase 5 ruft die Vision-API nicht auf. Gesichtserkennung, Embeddings und
biometrische Suche bleiben Phase 6 vorbehalten und deaktiviert.
