# Startseite, Kalender und Speiseplan – Korrekturen vom 06.09.2026

- Tagesauswahl bleibt auf der Startseite; Wochenleiste bleibt Montag bis Sonntag.
- Tagesmenü folgt dem ausgewählten Datum, Speiseplan-Reiter zeigt Montag bis Freitag mit Leerzuständen.
- Gemeinsame ausgeschriebene Allergen-/Zusatzstoffanzeige auch unter „Alle Wochen“.
- Kalenderpositionen werden ohne lokalisierte Dezimalkommas ausgegeben.
- Kalenderfarben folgen dem Theme; Filterzustände haben Hintergrund und Häkchen.
- Filter verwenden Location.replace, damit Umschalten keine zusätzlichen Zurück-Schritte erzeugt.
- Oberer Rückweg führt zur Startseite; Aktualisieren ist 32 × 32 Pixel groß.
- Erledigte Hausaufgaben erhalten einen durchgehenden grünen Hintergrund.

Prüfung: 11 gezielte Django-Tests bestanden (Kalender, Hausaufgabenstatus und neue
Regressionstests). Tailwind-Build erfolgreich. Keine Migration, keine neuen externen
Datenquellen; bestehende Zugriffsprüfungen und CSRF bleiben erhalten.
Ein zusätzlich geprüfter bestehender Familientest erwartet den aktuell fehlenden
Bereich „Familie im Blick“ und schlägt weiterhin fehl. Browser-Sichtprüfung und
produktive Bereitstellung sind noch nicht erfolgt.

## Bereinigung der Portalverwaltung

Schulportaladapter sind direkt in der administrativen Menügruppe erreichbar.
Die Verwaltungsübersicht enthält keine doppelten Kacheln für Schulen/Klassen,
Registrierungen, QR-Familieneinladungen oder Schulportaladapter mehr. Auch die
separate Terminumfrage-Kachel entfällt; Veranstaltungen bleiben im Klassenleben.
Die vorhandenen Zielseiten und Berechtigungsprüfungen bleiben erhalten.
