# Einwilligungen beim Kind

Familien-Zentrale → Kind → Datenschutz zeigt eine Tabelle mit Funktion,
persönlicher Entscheidung, wirksamem Status und einer expliziten Speichern-Aktion.
Freigabe, Ablehnung und Widerruf funktionieren ohne JavaScript. Die Details enthalten
den versionierten Einwilligungstext. Die eigene Zustimmung ist nicht automatisch
eine wirksame Gesamtfreigabe: Weitere erforderliche Sorgeberechtigte entscheiden
unabhängig. Zentral deaktivierte Biometrie bleibt gesperrt; Widerruf ist weiter möglich.

Die serverseitige Prüfung verwendet die bestehenden zweckbezogenen Entscheidungsrechte.
Ein Profilbearbeitungsrecht ist keine Voraussetzung und ersetzt auch kein
Einwilligungsrecht. Änderungen werden über die bestehenden versionierten Entscheidungs-
und Widerrufsdienste einschließlich Audit und Funktionsfolgen gespeichert.

Die CSS-Regel für Schalter adressiert jetzt das Element unmittelbar nach dem Input.
Zuvor traf sie bei Schaltern mit Screenreader-Label das versteckte Label und ließ
den sichtbaren Schalter leer. Das betrifft auch die Schalter unter Schulzugänge.

Adapter werden aktuell unter `/verwaltung/adapter/` schulgebunden angelegt und
freigeschaltet. Familien wählen freigegebene Module unter Kind → Schulzugänge.
Der vollständige zentrale Katalog mit Schulzuordnung und direkter persönlicher
Zugangspflege beim Kind ist als separate **BL-16 in [Backlog.md](Backlog.md)** dokumentiert.

Regressionen: `test_family_privacy_table.py`, `test_family_centre.py` und
`test_onboarding.py` prüfen Darstellung, Speichern, Widerruf und Berechtigungen.
