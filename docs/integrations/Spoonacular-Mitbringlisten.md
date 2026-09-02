# Spoonacular als Rezeptdatenbasis für Mitbringlisten

Stand: 02.09.2026

Organisatoren einer Veranstaltung können auf der geschützten Eventseite nach
neutralen Rezeptvorlagen suchen. Erst nach einer ausdrücklichen Auswahl werden
bis zu 50 Zutaten als lokale Mitbringpositionen übernommen. Eltern reservieren
diese Positionen anschließend ausschließlich innerhalb von KlassID.

## Datenschutz und Grenzen

- An Spoonacular gehen ausschließlich der vom Organisator eingegebene
  Suchbegriff oder eine ausgewählte numerische Rezept-ID.
- Namen, Klassen, Kinder, Veranstaltungen, Reservierungen und Standorte werden
  nicht übertragen.
- API-Antworten werden nicht gecacht. Erst die bewusste Auswahl erzeugt eine
  lokale Beitragsliste mit Quellenreferenz und Auditereignis.
- Allergie- und Ernährungsinformationen werden nicht als medizinisch
  verlässlich dargestellt oder automatisch übernommen.
- Nur eingetragene Eventorganisatoren dürfen suchen und importieren.
- Derselbe Rezeptdatensatz kann je Event nur einmal importiert werden.

Der API-Key liegt als `secret://klasse5e/spoonacular-api-key` im lokalen
DPAPI-Speicher. `tools/Deploy-Klasse5e.ps1` gibt ihn nur für die Laufzeit des
Docker-Compose-Aufrufs als Prozessvariable weiter und entfernt ihn danach.

## Betrieb

Deployment:

```powershell
.\tools\Deploy-Klasse5e.ps1
```

Der Adapter arbeitet mit einem Timeout von fünf Sekunden und höchstens zwölf
Suchergebnissen. Bei Provider-Ausfall bleibt die vorhandene manuelle
Mitbringliste vollständig nutzbar.
