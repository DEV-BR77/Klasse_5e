# Redesign: Mandanten, URLs und Identitäten

## Status

Erste Architekturentscheidung für die Erweiterung über die Klasse 5e hinaus.
Die Umsetzung erfolgt erst innerhalb der jeweils freigegebenen Projektphase.

## Zielbild

`classid.de` bleibt ein gemeinsames Portal für mehrere Schulen, Klassen und
Schuljahre. Die Klasse 5e ist der erste Bereich, aber kein Sonderfall im
Datenmodell. Schulen und Klassen werden als getrennte, historisch verwaltbare
Mandantenbereiche modelliert.

Eltern besitzen ein persönliches Konto und können mehrere Kinder verwalten,
auch wenn diese unterschiedliche Schulen oder Klassen besuchen. Der Wechsel
zwischen Kindern erfolgt im persönlichen Bereich über einen sichtbaren
Kontextwechsel. Jeder Kontextwechsel wird serverseitig geprüft.

## URLs

Die URLs enthalten keine lesbaren Schul-, Klassen- oder Personennamen. Sie
verwenden stabile, nicht erratbare technische Schlüssel, zum Beispiel:

```text
classid.de/app/s/7k4m2/c/q9t5x/
```

Die Schlüssel bestehen aus einer kurzen Kombination aus Buchstaben und Zahlen.
Sie sind eindeutig, zufällig bzw. kryptografisch sicher erzeugt und werden
nicht aus Schule, Ort, Klasse oder Personennamen ableitbar gebildet. Damit
spiegeln URLs keine sensiblen Zugehörigkeiten wider und lassen sich nicht
verlässlich durch Raten durchsuchen.

Die lesbaren Bezeichnungen erscheinen ausschließlich in der angemeldeten
Oberfläche, beispielsweise „Theodor-Heuss-Gymnasium · Klasse 5e“. Die URL ist
jedoch niemals ein Berechtigungsnachweis.

## Berechtigungsprüfung

Bei jedem geschützten Zugriff werden mindestens diese Beziehungen geprüft:

1. Das Konto ist authentifiziert.
2. Das Konto darf das ausgewählte Kind verwalten.
3. Das Kind besitzt eine aktive Mitgliedschaft im angeforderten Kontext.
4. Die Rolle des Kontos erlaubt die konkrete Aktion und das konkrete Objekt.

Das gilt auch für Beiträge, Dokumente, Medien, Suchfunktionen und Downloads.
Ein manipuliertes oder fremdes URL-Segment führt nicht zu einer Anzeige fremder
Daten. Die Anwendung antwortet mit einer neutralen Nichtverfügbarkeit bzw.
`404`, ohne zu verraten, ob der angefragte Bereich existiert.

## Identitäten im Datenmodell

Jede zentrale Entität erhält eine eigene stabile interne Identität:

- Benutzerkonto (`User-ID`)
- Familie bzw. Sorgeberechtigtenbeziehung
- Kind
- Schule
- Klassenbereich
- Schuljahr
- Mitgliedschaft und Rolle
- Dokument, Beitrag und sonstige geschützte Objekte

Die interne `User-ID` ist unabhängig von E-Mail-Adresse, Namen und Rolle. Sie
wird für Administration, Audit-Protokolle, Verknüpfungen und spätere
Änderungen der Kontaktdaten verwendet. E-Mail-Adressen sind Kontaktdaten bzw.
Anmeldemerkmale, aber keine dauerhafte Identität.

Öffentliche bzw. in URLs verwendete Schlüssel werden getrennt von internen
Primärschlüsseln behandelt. Dadurch können interne Datenbank-IDs, E-Mail-
Adressen und personenbezogene Informationen nicht aus einer URL abgeleitet
werden.

## Schuljahre und Klassenwechsel

Klassen werden nicht einfach umbenannt. Für jedes Schuljahr entsteht ein
eigener historischer Klassenbereich:

```text
Schule
└── Schuljahr 2025/26
    └── Klasse 5e
└── Schuljahr 2026/27
    └── Klasse 6e
```

Mitgliedschaften werden zeitlich begrenzt. So bleiben frühere Beiträge,
Dokumente und Berechtigungen nachvollziehbar, während der aktive Kontext für
das neue Schuljahr separat verwaltet wird.

## Individuelle Darstellung

Schule und Klassenbereich dürfen begrenzte Branding- und Inhaltseinstellungen
besitzen, zum Beispiel Name, Logo, Farbe, Begrüßungstext und Ansprechpartner.
Die Seitenstruktur und Sicherheitslogik bleiben zentral und einheitlich. Das
Logo oder ein Klassenname darf niemals als Sicherheitsgrenze betrachtet werden.

## Festgelegte Leitplanken

- Eine gemeinsame Domain und ein gemeinsamer Login sind der Startpunkt.
- Subdomains pro Schule sind zunächst nicht erforderlich.
- Schlüssel sind nicht sprechend, nicht personenbezogen und nicht erratbar.
- Sichtbarkeit und Zugriff werden immer aus aktiven Mitgliedschaften abgeleitet.
- Historische Schuljahre bleiben unverändert und getrennt abrufbar.
- Zentrale Administration darf Konten über interne IDs verwalten, ohne diese
  IDs in der normalen Oberfläche unnötig offenzulegen.

## Offene Umsetzungspunkte

- Format und Erzeugung der öffentlichen Schlüssel festlegen.
- Lebenszyklus abgelaufener Mitgliedschaften definieren.
- Rollenmodell für zentrale, schulweite und klassenbezogene Administration
  konkretisieren.
- Tests für URL-Manipulation, Klassenisolation, Schulisolation und
  abgelaufene Mitgliedschaften ergänzen.
