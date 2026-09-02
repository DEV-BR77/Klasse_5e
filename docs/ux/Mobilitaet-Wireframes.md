# Mobilität – mobile Wireframes

Stand: 02.09.2026. Diese Entwürfe gelten für den geschlossenen Bereich einer aktiven Klasse und verwenden ausschließlich synthetische Angaben.

## Übersicht und Listenfallback

```text
[Mobilität]                                      [Karte | Liste]
Gemeinsam sicher zur Schule

[ Ich suche ]              [ Ich biete ]
Fahrt oder Gruppe finden    Plätze oder Begleitung anbieten

Filter: [Hinweg v] [Auto, Fahrrad, zu Fuß v] [Mo–Fr v]

Fahrradgruppe Nord                         Heute · 07:35–07:50
Öffentlicher Treffpunkt: Stadtbibliothek   4 Familien interessiert
Rad · zur Schule                           [Details]

PKW · 2 Plätze frei                        Mo, Mi, Fr · 07:25–07:45
Grober Bereich: Nordwest                   [Details]

Karte nicht verfügbar? Alle Treffpunkte und Bereiche sind in dieser Liste
vollständig erreichbar. Exakte Adressen werden nie hier gezeigt.
```

Die Karte zeigt nur Schule, freiwillig gewählte öffentliche Treffpunkte und gerasterte Bereiche. Routen beginnen und enden nie an Wohnadressen. Ein gleichwertiger Listenfallback ist Pflicht.

## „Ich suche“ und „Ich biete“

```text
[← Mobilität]  Ich biete
Was bietest du?  ( ) Auto  (•) Fahrradgruppe  ( ) Zu Fuß
Fahrtrichtung:   [Hinweg zur Schule v]
Tage:             [Mo] [Di] [Mi] [Do] [Fr]
Zeitfenster:      [07:35] bis [07:50]
Treffpunkt:       [Stadtbibliothek, Haupteingang             ]
                   [Treffpunkt auf Karte wählen]
Hinweis, optional [Helm bitte mitbringen                     ]
Gültig bis:       [30.09.2026]

☐ Das Portal vermittelt Kontakte, nicht Beförderung. Aufsicht, Versicherung,
  Fahrerlaubnis und Kindersitze klären Erwachsene untereinander.

[Entwurf verwerfen]                             [Angebot veröffentlichen]
```

Eine private Abholadresse wird nie hier eingegeben. Sie wird erst in einem angenommenen privaten Vorgang nach Erklärung von Empfänger, Genauigkeit, Widerruf und Löschzeitpunkt freigegeben.

## Detail und Reaktion

```text
[← Mobilität] Fahrradgruppe Nord                         [Melden]
Hinweg · Mo–Fr · 07:35–07:50 · aktiv
Treffpunkt: Stadtbibliothek, Haupteingang
Reihenfolge: Stadtbibliothek → Schulhof
Verantwortlich: verifizierte Sorgeberechtigte Person

[Ich bin interessiert]  [Platz anbieten]
[Rückfrage im Gruppenchat]
```

Reaktionen haben den sichtbaren Status gesendet, angenommen, abgelehnt oder zurückgezogen. Push-Mitteilungen bleiben neutral; ohne Push ist der Ablauf vollständig in der PWA nutzbar.

## Treffpunkt, Rotation und Rücknahme

```text
[← Gruppe bearbeiten]  Treffpunkte
1  Stadtbibliothek, Haupteingang   07:35  [Bearbeiten]
2  Schulhof                        07:50  [Bearbeiten]
[Sammelpunkt hinzufügen]

Wochenrotation (unverbindlich)
Mo: Familie A   Di: Familie B   Mi: offen
[Rotation ändern]

[Gruppe pausieren] [Gruppe zurückziehen]
```

Eine Rotation bleibt ein Vorschlag. Rückzug und Pausieren erklären die Wirkung auf offene Reaktionen; Beteiligte erhalten nur eine neutrale Änderungsinformation.
