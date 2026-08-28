# WebUntis-Datenfluss

```text
bestätigte sorgeberechtigte Person
  └─ wählt Kind + einzelne Kategorie, bestätigt aktuelle Einwilligung
      └─ Django prüft Beziehung, Verwaltungsrecht, Textversion und Sperre
          └─ entschlüsselt Zugang nur im Arbeitsspeicher
              └─ HTTPS → thgwob.webuntis.com
                  └─ Antwort klassifizieren, im Pilot nicht fachlich speichern
                      └─ logout, Sitzung verwerfen, minimierten Laufstatus sichern
```

Die Host-Allowlist verhindert freie Zielwahl. Logs enthalten weder Zugang, Session-ID noch personenbezogene Antwort. Gleichzeitige Läufe werden pro Verbindung gesperrt; Wiederholungen verwenden einen Idempotency-Key.
