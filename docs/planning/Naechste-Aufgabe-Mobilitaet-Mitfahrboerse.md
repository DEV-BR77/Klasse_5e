# Phase 2 / nicht umgesetzt

## Mobilität, Mitfahrbörse und sichere Schulweggruppen

> Dieses Dokument ist ausschließlich ein ausführbarer Folgeauftrag. Im
> aktuellen Arbeitspaket werden keine Modelle, Migrationen, Views, URLs,
> Menüpunkte, Karten oder Demo-Funktionen hierfür umgesetzt.

## Ziel und Umfang

Baue einen freiwilligen, klassenbezogenen Bereich „Mobilität“ für
Fahrgemeinschaften, Fahrradgruppen und Laufgruppen. Verifizierte erwachsene
Sorgeberechtigte mit aktiver Klassenmitgliedschaft können Einträge vom Typ
„Ich biete“ oder „Ich suche“ erstellen. Verkehrsmittel umfassen mindestens
Auto, Fahrrad und Zu Fuß; das Modell muss weitere Arten erlauben.

Angebote können freie Plätze, ungefähren Startbereich, Zielschule, Wochentage,
Zeitfenster, maximalen Umweg, Gültigkeitszeitraum und Hinweise enthalten.
Suchen beschreiben Bedarf, Zeitfenster und ungefähren Bereich. Fahrrad- und
Laufgruppen planen freiwillige sichere Treffpunkte und eine Reihenfolge
gemeinsamer Sammelpunkte. Fahrgemeinschaften können eine unverbindliche
Wochenrotation führen; das System erzeugt keine automatische Verpflichtung.

## Lebenszyklus und Reaktionen

Jeder Eintrag speichert Erstell- und Änderungszeitpunkt, Ablaufdatum, Status
`aktiv`, `pausiert`, `vermittelt`, `abgelaufen` oder `zurückgezogen` sowie
anonymisierte, deduplizierte Aufruf- und Reaktionszahlen. Reaktionen umfassen
mindestens `interessiert`, `Platz angeboten`, `Rückfrage`, `angenommen`,
`abgelehnt` und `zurückgezogen`. Statusänderungen bleiben für Ersteller und
Reagierende nachvollziehbar.

Private Rückfragen sollen möglichst den bestehenden Klassenchat verwenden,
ohne Telefonnummern oder E-Mail-Adressen automatisch offenzulegen. Optionale
Push-Kategorien für passende Angebote, Reaktionen und Änderungen bleiben
getrennt aktivierbar und enthalten keine sensiblen Standort- oder Kontaktdaten.

## Standort- und Kartenpolicy

Die Karte ist hochsensibel. Exakte Wohnadressen oder Wohnpunkte von Kindern
und Familien erscheinen niemals standardmäßig auf einer Klassenkarte. Es gibt
keine Live-Ortung, Hintergrundstandorte, Bewegungsprofile oder automatische
Übernahme aus Benutzerprofilen. Standorte werden nur von Sorgeberechtigten
freiwillig und zweckgebunden freigegeben.

Standard ist ein grober, gerasterter oder gerundeter Bereich beziehungsweise
ein selbst gewählter öffentlicher Treffpunkt. Eine exakte Abholadresse darf
erst nach beiderseitiger Zustimmung in einem geschützten privaten Vorgang
geteilt werden und bleibt widerrufbar. Vor dem Speichern erklärt die Oberfläche
Reichweite, Genauigkeit und Empfängerkreis anschaulich.

Treffpunkte besitzen Name, Koordinate, Beschreibung, Zeitfenster,
Verkehrsmittel, verantwortliche erwachsene Kontaktperson und Status. Routen
dürfen keine stillen Rückschlüsse auf einzelne Kinderadressen ermöglichen.
Kartenfilter zeigen ausschließlich Einträge der eigenen aktiven Klasse und nur
im freigegebenen Genauigkeitsgrad. Schuladministratoren erhalten keinen
automatischen Zugriff auf private exakte Adressen. Für jede Standortabfrage und
-freigabe sind Policy, Löschfrist und Negativtests gegen IDOR und Klassenwechsel
zu dokumentieren.

## Sicherheit, Moderation und Verantwortung

Ergänze Melden, Moderieren, Sperren, Ablauf und Löschung. Nur verifizierte
erwachsene Sorgeberechtigte mit aktiver Klassenmitgliedschaft dürfen Einträge
erstellen oder freigegebene Kontaktdaten sehen. Kinderkonten dürfen keine
Fahrten allein vereinbaren. Jeder Eintrag benötigt eine kurze Sicherheits- und
Verantwortungserklärung: Das Portal vermittelt Kontakte, aber keine
automatische Beförderungszusage. Fahrerlaubnis, Versicherung, Kindersitze und
Aufsicht bleiben Verantwortung der beteiligten Erwachsenen und werden nicht
ungeprüft als verifiziert dargestellt.

## Matching

Ermögliche später Vorschläge anhand von Verkehrsmittel, Wochentag, Zeitfenster,
grober Entfernung und maximalem Umweg. Matching-Ergebnisse sind unverbindliche
Vorschläge und dürfen keine sensiblen Profile bilden. Barrierefreiheit und
besondere Bedarfe sind ausschließlich freiwillige, zweckgebundene Angaben;
Gesundheitsdiagnosen werden nicht erfasst.

## Vorgeschaltetes UX- und Datenschutzgate

Erstelle vor Implementierung mobile Wireframes und eine Datenschutz-/
Bedrohungsanalyse für:

- Kacheln „Ich suche“ und „Ich biete“,
- Kartenansicht mit Listenfallback,
- Eintragsdetail und Reaktionsablauf,
- gemeinsamen Treffpunkt und Rotation,
- Rückgängig- und Löschabläufe.

Pflichtprüfungen umfassen Klassenisolation, Standortgenauigkeit,
Einwilligung/Widerruf, Ablauf/Löschung, Aufrufzählung ohne Selbst- oder
Botverzerrung, Reaktionsstatus, Chat-/Push-Datensparsamkeit, Moderation sowie
mobile Bedienung mit und ohne Karte.

## Späterer separater Punkt: öffentliche Demo

Eine mögliche öffentliche Demo verwendet ausschließlich synthetische Schulen,
Klassen, Familien, Standorte und Nachrichten. Sie darf niemals produktive
Konten, Datenbank, WebUntis-Zugänge, Push-Abonnements oder Mailverteiler nutzen.
Werbung, öffentliches Marketing und Demo-Betrieb sind nicht Bestandteil des
aktuellen Auftrags und benötigen eine eigene Freigabe.

## Kurzfristiger Fahrtausfall, Push-Reaktion und gesicherte Ersatzkoordination

Für eine vereinbarte Fahrt oder Fahrrad-/Laufgruppe kann die aktuell
verantwortliche erwachsene Person kurzfristig „Ich kann diese Fahrt nicht
übernehmen“ melden. Optionale Gründe sind ausschließlich neutrale Kategorien
wie `krank`, `verhindert`, `Termin` oder `sonstiges`; medizinischer Freitext und
Diagnosen sind ausgeschlossen. Die Meldung referenziert eindeutig Gruppe,
Datum, Fahrtabschnitt und Zeitfenster. Eine fachliche Idempotenzkennung
verhindert doppelte Ausfälle durch Doppeltipp oder erneuten Versand.

Nur tatsächlich betroffene, aktiv teilnehmende Sorgeberechtigte erhalten einen
Push. Auf dem Sperrbildschirm stehen keine Kinder-, Adress-, Gesundheits- oder
Routendetails, sondern nur ein neutraler Hinweis wie „Änderung bei einer
vereinbarten Fahrt“ mit geschütztem Deep Link. Nach Anmeldung zeigt die PWA
berechtigte Details und große Aktionen:

- „Ich übernehme die Fahrt“,
- „Gelesen – ich kümmere mich selbst“,
- „Ich kann nicht übernehmen“,
- optional „Rückfrage“ im geschützten Gruppenchat.

Push-Aktionsbuttons dürfen, soweit unterstützt, nur als Abkürzung dienen. Eine
verbindliche Übernahme erfolgt niemals durch einen unbestätigten
Notification-Klick oder zustandsändernden GET. Sie öffnet eine authentisierte,
CSRF-geschützte Bestätigung mit Fahrt, Datum, Uhrzeit, benötigter Kapazität und
Konsequenz. Aktionsnachweise sind kurzlebig, benutzergebunden, gehasht,
einmalig, widerrufbar und auditierbar. Ohne Push-Aktionssupport bleibt der
vollständige Ablauf in der PWA verfügbar.

### Gruppenstatus und Frist

Nur Beteiligte sehen, wer die Änderung zur Kenntnis genommen hat, selbst eine
Lösung organisiert, die komplette Fahrt oder einzelne Plätze übernimmt, eine
Ersatzfahrt verbindlich bestätigt hat oder noch nicht reagiert hat. Diese
Information ist keine allgemeine Anwesenheits- oder Verhaltenskontrolle.

Eine klare Frist begrenzt die Koordination. Vor Ablauf darf bei aktivierter
Push-Kategorie genau einmal datensparsam erinnert werden. Bleibt die Fahrt
ungelöst, lautet der eindeutige Endzustand: „Keine gemeinsame Ersatzfahrt
bestätigt – bitte selbst organisieren“. Das System nimmt niemals still an,
dass die Fahrt stattfindet.

Nach bestätigter Übernahme erhalten alle Betroffenen genau eine neutrale
Aktualisierung; Details sind erst nach Anmeldung sichtbar. Parallele
Übernahmeversuche werden transaktionssicher über Kapazität, vollständige oder
teilweise Übernahme, Priorität und Rücknahme entschieden. Widersprüchliche
Zusagen sind unzulässig. Eine kontrollierte Rücknahme deaktiviert die alte
Zusage und startet denselben Ausfallprozess erneut mit neuer Idempotenzperiode.

### Mobile Wireframes für die Folgephase

```text
[← Vereinbarte Fahrt]
[Ausfall melden]
Datum / Abschnitt / Zeitfenster
[neutraler Grund, optional]
[Konsequenz erklärt]                 [Ausfall bestätigen]
```

```text
[Änderung bei einer vereinbarten Fahrt]
Nach Anmeldung: Datum, Zeit, benötigte Kapazität
[Ich übernehme] [Ich kümmere mich selbst]
[Kann nicht]    [Rückfrage]
```

```text
[Ersatzkoordination]
Bestätigt: … Plätze / komplette Fahrt
Gelesen: …   Selbst organisiert: …   Offen: …
[Keine gemeinsame Ersatzfahrt bestätigt – bitte selbst organisieren]
```

### Zusätzliche Pflichtprüfungen

- ausschließlich betroffene Empfänger und klassen-/gruppenisolierter Status,
- Push deaktiviert, abgelehnt oder nicht unterstützt,
- datensparsamer Sperrbildschirmtext,
- Authentisierung, CSRF sowie abgelaufene oder erneut verwendete Aktionen,
- Doppeltipp und idempotenter erneuter Versand,
- konkurrierende vollständige und teilweise Übernahmen samt Kapazität,
- kontrollierte Rücknahme ohne fortwirkende alte Zusage,
- genau eine Abschlussmitteilung und höchstens eine Erinnerung,
- Lesestatusrechte ohne allgemeine Verhaltenskontrolle,
- klarer PWA-Fallback und eindeutiger Endzustand ohne Ersatzfahrt.

## Priorisierte Ausnahmekachel auf Home (nur spätere Phase)

Für jeden konkret betroffenen Benutzer erscheint bei einem kurzfristigen
Fahrtausfall oberhalb normaler Home-Kacheln eine priorisierte Ausnahmekachel.
Sie ist ausschließlich für aktive Mitglieder der betroffenen Fahrgruppe
sichtbar und verschwindet nach Abschluss entsprechend der festgelegten
Aufbewahrungsregel.

- Rot, Warnsymbol und „Fahrt ungeklärt“, solange keine Lösung vorliegt.
- Gelb, Statussymbol und „Antworten vorhanden – noch nicht bestätigt“, sobald
  Reaktionen oder Teilangebote existieren, die benötigte Kapazität aber nicht
  verbindlich vollständig decken.
- Grün, Bestätigungssymbol und „Ersatzfahrt bestätigt“, sobald eine
  transaktionssicher vollständige Lösung besteht.
- Neutral warnend und ausdrücklich „Keine Ersatzfahrt – bitte selbst
  organisieren“, wenn die Frist abläuft oder alle ablehnen; dieser Zustand darf
  nicht grün erscheinen.

Die Kachel zeigt nur Datum/Zeitfenster, eine neutrale Fahrtenbezeichnung,
Reaktionsstand und die große Aktion „Details und reagieren“. Kinderadressen,
Gesundheitsangaben und sensible Routendetails bleiben von Home fern. Das Öffnen
erzeugt keine Zusage. Nach bestätigter Lösung bleibt die grüne Kachel bis zur
persönlichen Kenntnisnahme beziehungsweise kurz bis zum Fahrttermin sichtbar
und wechselt anschließend in Verlauf/Benachrichtigungen. Icon, Text und
ARIA-Status tragen die Bedeutung unabhängig von Farbe.

Das spätere Gate testet ausschließlich Betroffene, Rot → Gelb → Grün,
Teilkapazität, konkurrierende Übernahmen, Fristablauf ohne Lösung, persönliche
Kenntnisnahme, mehrere Ausfälle, Priorisierung vor normalen Kacheln, mobile
Darstellung sowie Farbsehschwäche und Screenreader.
