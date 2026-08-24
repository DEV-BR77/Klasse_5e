# Sicherheit und Datenschutz

Lokale Verarbeitung bedeutet Verarbeitung im selbst betriebenen Container,
nicht auf dem Endgerät. Es gibt keine Cloud-KI, Telemetrie oder öffentlich
erreichbare API. Das interne Bearer-Token kommt ausschließlich aus der lokalen
Secret-Verwaltung; Vergleiche erfolgen zeitkonstant.

JPEG/PNG werden anhand des Inhalts geprüft, größen- und pixelbegrenzt,
EXIF-orientiert und ohne Metadaten neu codiert. Benutzerpfade sind verboten.
Logs enthalten weder Request-Bodies noch Token, Medienreferenzen, Bilder,
Crops, Embeddings oder Scores.

Collection-Isolation wird durch zusammengesetzte Primär-/Fremdschlüssel und
collection-gebundene Abfragen erzwungen. Dateien liegen in validierten
ID-Verzeichnissen. Löschungen entfernen Datenbankabhängigkeiten und Dateien
kontrolliert und idempotent. Gesichtscrops und Embeddings sind biometrische
Daten; auch Backups können sie bis zum Ende ihrer Aufbewahrungsfrist enthalten.

Das Modell erzeugt nur Vorschläge. Externe Fachlogik entscheidet über
Einwilligung und Berechtigung; sie wird in dieser Phase nicht implementiert.
