# Löschlauf und Nachweis

## Runbook

1. offenen Auftrag und Objektumfang ohne Inhaltsausgabe prüfen;
2. Funktion/Anzeige bereits vor physischer Löschung sperren;
3. Primärdatensatz und abhängige Dateien, Vorschaubilder, Embeddings, Endpunkte und Caches idempotent entfernen;
4. Suchindex/Exports bereinigen;
5. Ergebnis mit Auftrag-ID, Objektart, pseudonymisierter Referenz, Zeitpunkt, Ergebnis und Fehlerklasse dokumentieren;
6. bei Fehlern begrenzt erneut versuchen und danach manuell eskalieren;
7. Backup-Tombstone in Wiederherstellungsprüfung berücksichtigen.

Der Nachweis enthält keine gelöschten Inhalte, Dateinamen mit Klarnamen, Passwörter, Token, WebUntis-Antworten oder biometrische Vektoren. Stichprobenweise Restore-Tests bestätigen, dass Tombstones vor Wiederfreigabe erneut angewandt werden.
