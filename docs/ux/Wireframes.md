# Low-Fidelity-Wireframes

Die Wireframes zeigen Hierarchie und Aktionen, keine fertige Gestaltung.
`[M]`, `[S]` und `[Später]` entsprechen Muss, Soll und Später aus der
[UX-Spezifikation](UX-Spezifikation.md).

## Dashboard – Smartphone

```text
┌ Klasse 5e                         Profil ○ ┐
│ Guten Morgen, Alex                         │
│ ‹  Mittwoch, 26. August  ›   Nächster Tag │
├ Heute / nächster Schultag [M] ────────────┤
│ Stundenplan · Stand 07:45                  │
│ 08:00 Mathematik · R 204                   │
│ 08:50 ✕ Entfällt · Englisch                │
│ 10:00 ⇄ Vertretung · Biologie · R 12       │
│                         Ganzen Tag ansehen ›│
├ Speiseplan [Später] ───────────────────────┤
│ Menü 1 …     Menü 2 …     Allergene öffnen │
│ Quelle/Stand · Original-PDF ›              │
├ Wichtig ───────────────────────────────────┤
│ ! Prüfung Freitag · Details ›              │
│ 🗓 Schulfest · Meine Zusage: 2 Flaschen ›  │
│ ● 2 neue Beiträge · 4 Chatnachrichten ›    │
└ Start      Kalender      Chat       Mehr ──┘
```

## Dashboard – Desktop

```text
┌ Navigation ─────┬ Guten Morgen, Alex · Mittwoch, 26. August ───────────┐
│ Start           │ [‹ Tag] [Heute] [Tag ›]             Stand 07:45      │
│ Aktuelles       ├──────────────┬──────────────┬────────────────────────┤
│ Dokumente       │ Stundenplan  │ Speiseplan   │ Wichtig                │
│ Kalender        │ 08:00 Mathe  │ [Später]     │ ! Prüfung Freitag      │
│ Veranstaltungen │ ✕ Entfall E  │ Menü 1 / 2   │ 🗓 Termin / Mitbringen │
│ Chat            │ ⇄ Bio R 12   │ Quelle/PDF   │ ● Neues                │
│ Fotos           ├──────────────┴──────────────┴────────────────────────┤
│ Lehrkräfte      │ Nächster Termin       Offene eigene Zusagen          │
│ Familie         │ Schulfest · 29.08.     2 Flaschen Saft · ändern ›    │
│                 │                                                  │
│ Arbeitsbereich  │                                          Profil ○   │
└─────────────────┴───────────────────────────────────────────────────────┘
```

## Mobile Hauptnavigation

```text
Unterer Balken: [⌂ Start] [▦ Kalender] [● Chat 4] [☰ Mehr]

Mehr
Klasse:  Aktuelles · Dokumente · Veranstaltungen · Speiseplan [Später]
         Fotos · Lehrkräfte
Familie: Familie & Profile · Einwilligungen
Konto:   Benachrichtigungen · Sicherheit & Sitzungen · Abmelden
```

## Dokumentencenter

```text
Dokumente                         [Suche 🔎____________]
[Aktuell] [Häufig] [Formulare] [Elternbriefe] [Alle]
┌ Anmeldung Klassenfahrt             Aktualisiert ┐
│ PDF · 240 KB · Version 2 · 25.08.              │
│ [Original öffnen] [Ausfüllbares Formular öffnen]│
└─────────────────────────────────────────────────┘
Leer: „In dieser Kategorie gibt es noch nichts.“ [Alle zeigen]
Fehler: „Download nicht möglich.“ [Erneut versuchen]
```

## Veranstaltungsdetail und Mitbringliste

```text
Schulfest · Sa 29.08. · 15:00–18:00 · Schulhof
Hinweise …    Organisiert von …    [Kalender] [Dokumente]
Meine Zusagen: 2 Flaschen Saft                 [Ändern]

Mitbringen   [Suche____________]
[Brot] [Brötchen] [Salat] [Obst] [Getränke] [Hilfe]
┌ 🍎 Äpfel       ┐ ┌ 🥤 Saft             ┐
│ noch 2 Körbe   │ │ von mir reserviert  │
│ [Auswählen]    │ │ 2 Flaschen [Ändern] │
└────────────────┘ └──────────────────────┘
[Eigenen Beitrag hinzufügen]
```

## Mobile Mitbringauswahl

```text
‹ Mitbringen              Kategorie: [Getränke ▼]
[🔎 Saft oder Getränk suchen____________________]
Häufig: [🥤 Saft] [💧 Wasser]
┌ 🥤 Saft ─────────────────────────────────────┐
│ Noch benötigt: 3 Flaschen                    │
│ Menge [−] 2 [+]   Einheit [Flaschen ▼]       │
│ [Weiter zur Bestätigung]                     │
└───────────────────────────────────────────────┘
Bestätigung: „Du reservierst 2 Flaschen Saft.“
[Zurück]                         [Verbindlich reservieren]
```

Freier Beitrag:

```text
Eigener Beitrag
Kategorie [Hilfe ▼]  Bezeichnung [Aufbau helfen______]
Menge [1] Einheit [Person/Stunde ▼]
Bemerkung [optional____________________________]
Hinweis: Freie Beiträge können moderiert werden.
[Abbrechen] [Prüfen und reservieren]
```

Konflikt und Rücknahme:

```text
! Gerade vollständig vergeben
Jemand war einen Moment schneller. Deine Reservierung wurde nicht angelegt.
[Liste aktualisieren] [Alternativen ansehen]

Zusage zurücknehmen?
2 Flaschen Saft werden wieder als benötigt angezeigt.
[Behalten] [Zusage zurücknehmen]
```

## Stundenplan – Smartphone

```text
‹ Dienstag  26.08.  Mittwoch ›       Stand 07:45
08:00–08:45  Mathematik · Frau S. · R 204   Regulär
08:50–09:35  Englisch                         ✕ Entfällt
              Ursprünglich: Englisch · R 110
10:00–10:45  Biologie · Herr K. · R 12       ⇄ Vertretung
12:00         ! Klassenarbeit Deutsch         Details ›
[Manueller Plan] [Quelle WebUntis: Später]
```

## Stundenplan – Desktop

```text
[‹ Woche]   24.–28. August   [Diese Woche] [Woche ›]   Stand 07:45
Zeit     Mo              Di               Mi              Do/Fri
08:00    Mathe R204      Deutsch          Mathe           …
08:50    Englisch        ✕ Englisch       ⇄ Bio R12       …
10:00    Sport           ! Prüfung        Ferien/Info     …
Legende: ✕ Entfall · ⇄ Vertretung · ↔ Änderung · ! Prüfung
```

## Speiseplan-Tageskarte [Später]

```text
Speiseplan · Mittwoch 26.08. · KW 35
Menü 1  Pasta · Tomatensauce · Salat       [A, G]
Menü 2  Gemüsepfanne · Reis                [F]
[Allergene und Zusatzstoffe aufklappen]
Stand 26.08., 06:10 · Änderungen möglich
[Original-PDF bei Wollino]    [Aktuelle Menüpläne]
Fehlerzustand: ! Prüfung erforderlich · [Nur Original-PDF öffnen]
```

## Galerie

```text
Schulfest-Fotos                         [Fotos hochladen]
Privat im Klassenbereich · Screenshots sind technisch möglich.
[Foto] [Foto: wartet auf Moderation] [Foto]
Detail: Bildbeschreibung · Event · [Melden] [Eigenes Foto zurückziehen]
[Herunterladen] nur bei aktueller Freigabe
! Nicht verfügbar: Einwilligung wurde widerrufen.
```

## Chat

```text
Räume: [Klassenraum ●4] [Schulfest 🔕]
Klassenraum                         Aktualisiert 14:32
──────── Erste ungelesene Nachricht ────────
Alex · Vater von Kim      14:30
  Bezug: „Treffen ist um 15 Uhr …“
  Danke, wir kommen direkt zum Schulhof. [Antworten] [Melden]
Eigene Nachricht · Bearbeitet          [Bearbeiten] [Zurückziehen]
[Nachricht schreiben________________] [Senden]
Offline: „Verbindung unterbrochen.“ [Erneut versuchen]
```

## Familienprofil

```text
Familie & Profile                       [Kind: Kim ▼]
Mein Profil: Alex Beispiel · eigenes persönliches Konto
E-Mail: nicht sichtbar [Freigabe ändern]
Telefon: Klassenlehrkräfte [Freigabe ändern]

Verknüpfte Kinder
Kim Beispiel · Beziehung verifiziert · Vater
Rechte: Profil ansehen · allgemeine Einwilligungen
Weiteres Elternkonto: getrennte Entscheidung erforderlich
[Schülerprofil ansehen] [Einwilligungen]
```

## Einwilligungsdialog

```text
Veranstaltungsfotos anzeigen
Worum geht es? Fotos im geschlossenen Klassenbereich.
Wer sieht sie? Aktive Mitglieder der Klasse.
Wie lange? Bis zur angegebenen Galeriefrist.
Widerruf: Betroffene Fotos werden sofort ausgeblendet und geprüft.
Textversion: Entwurf 2 · Stand 26.08.2026   [Langfassung]
[Nicht zustimmen]                         [Zustimmen]
Danach: „Deine Entscheidung wurde gespeichert. Du kannst sie widerrufen.“
```
