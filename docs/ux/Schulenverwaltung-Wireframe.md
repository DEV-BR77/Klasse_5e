# Schulenverwaltung – Layout und Akzeptanz

## Liste

Titel und knapper Importstatus stehen über einer einzeiligen, kombinierbaren
Such-/Filterleiste. Darunter folgt ausschließlich eine serverseitig paginierte
Tabelle für Name, PLZ, Ort, Bundesland, Schulart, Kürzel, Aktualität und
Dublettenstatus. Filter, Sortierung und Seite bleiben in der URL sichtbar.

```text
[Schulenverwaltung]                         [CSV importieren]
[Suche____] [PLZ] [Ort] [Bundesland] [Art] [Status] [Filtern]
Name              PLZ    Ort        Land       Art       Kürzel  Status
… serverseitig paginiert …                              [< 1 2 >]
```

## Detail und Klasse

Die Detailseite gruppiert nur befüllte Bereiche: Identität, Anschrift,
Organisation, Kontakt, Importnachweis und mögliche Dubletten. Karten-Tiles
laden erst nach bewusster Interaktion. Ohne validierte Koordinate erscheint
kein Marker. Unterhalb folgen Klassen; die Hostnamenvorschau steht direkt beim
stabilen Klassencode.

```text
[Schule / Kürzel] [Bearbeiten]
[Identität] [Anschrift] [Organisation] [Kontakt] [Import]
[Karte erst laden] oder [Kein Kartenstandort verfügbar]
[Klassen]
Code  Anzeige  Schuljahr  Status  Hostname                 Admins
5e    5e       2026/27    aktiv   https://5e.klassid.de    …
```

## Akzeptanz

- Nur globale oder explizit zugewiesene Schuladministratoren sehen den
  Bestand; normale Mitglieder erhalten auch über direkte IDs keinen Zugriff.
- Listen laden höchstens eine Seite und geben keine `raw`-Felder aus.
- Kürzel- und Hostkollisionen werden serverseitig abgewiesen.
- Klassenadmins verwalten ausschließlich explizit zugewiesene Klassen.
- Externe Karten erhalten keine Kontakt- oder Direktorenfelder und werden
  nicht ohne Interaktion angefordert.
