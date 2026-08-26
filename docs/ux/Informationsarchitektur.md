# Informationsarchitektur

Diese Struktur konkretisiert die [UX-Spezifikation](UX-Spezifikation.md). Sie
ändert keine Berechtigungen: aktives Konto, aktive Mitgliedschaft, Rolle,
Objektrecht, verifizierte Beziehung und Einwilligung bleiben maßgeblich.

## Navigation für Klassenmitglieder

| Priorität | Mobil | Desktop | Inhalt |
|---|---|---|---|
| Muss | `Start` | Start | persönliches Dashboard |
| Muss | `Kalender` | Kalender | Tages-/Wochenplan, Termine, später Aufgaben/Prüfungen |
| Muss | `Chat` | Chat | Klassen- und Eventräume |
| Muss | `Mehr` | Aktuelles | Beiträge und Kommentare |
| Muss | unter `Mehr` | Dokumente | geschützte PDFs/Formulare |
| Muss | unter `Mehr` | Veranstaltungen | Events und Mitbringen |
| Später | unter `Mehr`, nur bei Freigabe | Speiseplan | Wollino-Tages-/Wochenplan; täglicher Nutzen |
| Muss | unter `Mehr` | Fotos | geschützte Galerien |
| Muss | unter `Mehr` | Lehrkräfte | freigegebene Lehrerprofile |
| Muss | Profilmenü | Familie & Profile | eigene und verknüpfte Profile |
| Muss | Profilmenü | Einwilligungen | einzelne Entscheidungen/Widerruf |
| Muss | Profilmenü | Benachrichtigungen | Push-Kategorien und Browserstatus |
| Muss | Profilmenü | Konto | Anmeldung, MFA, Sitzungen, Abmelden |

Mobile `Mehr` ist eine beschriftete Seite mit Gruppen `Klasse`, `Familie` und
`Mein Konto`, kein Hamburger-Menü mit zwölf gleichwertigen Zeilen. Ein
sichtbarer Seitentitel, Zurücknavigation und Breadcrumbs auf Desktop geben
Orientierung. Ein Familienumschalter erscheint nur bei mehreren verknüpften
Kindern und beeinflusst ausschließlich schülerbezogene Karten.

## Rollenbezogene Arbeitsbereiche

| Bereich | Zugang | Abgrenzung |
|---|---|---|
| Nutzeroberfläche | aktive Mitglieder; abonnierende Konten nur zu ausdrücklich erlaubten Einstellungen | keine technischen Verwaltungsbegriffe |
| Inhalte bearbeiten | Redakteure, Lehrkräfte entsprechend Fachrecht, zugewiesene Organisatoren | Beiträge, Dokumente, Lehrerprofile, eigene Events; keine Konten/Rollen |
| Moderation | Moderatoren und zulässige Adminrollen | Kommentare, Chatmeldungen, Fotos; Actor bleibt auditierbar |
| Administration | Haupt-/stellvertretende Admins; Wagtail nur vertrauenswürdige Rollen | Konten, Beziehungen, Mitgliedschaften; kritische Rollen/Exporte nur Hauptadmin |

Der Wechsel erfolgt über einen klaren Link `Arbeitsbereich`, nicht durch
zusätzliche normale Navigationspunkte. Kritische Administration darf optisch
nüchterner sein, muss aber dieselben Fokus-, Kontrast- und Sprachregeln
erfüllen.

## Seitenhierarchie

```text
Start
├── Tagesauswahl
├── Stundenplan / Änderungen
├── Speiseplan (Später)
├── Prüfung / Hausaufgabe (Später)
├── nächster Termin / Mitbringzusage
└── Neues: Beiträge / Chat
Kalender
├── Tag (mobil)
├── Woche (Desktop)
└── iCal verwalten
Aktuelles ─ Beitrag ─ Kommentare
Dokumente ─ Kategorie/Suche ─ geschützter Download
Veranstaltungen ─ Detail ─ Mitbringen ─ eigene Zusagen
Chat ─ Raum ─ Nachricht/Antwort/Meldung
Fotos ─ Galerie ─ Foto/Upload/Meldung
Mehr
├── Speiseplan (Später)
├── Lehrkräfte
├── Familie & Profile
├── Einwilligungen
├── Benachrichtigungen
└── Konto
```

## Gemeinsame Zustandsregeln

- **Muss:** `Lädt`, `Keine Inhalte`, `Nicht berechtigt`, `Nicht verfügbar`,
  `Veraltet`, `Offline` besitzen jeweils verständlichen Text und nächste
  Aktion.
- **Muss:** fremde Klassenobjekte und deaktivierte sensible Funktionen bleiben
  neutral nicht auffindbar (404), nicht erklärend ausgeleuchtet.
- **Muss:** jede Hauptseite nennt Datenstand, wenn externe/manuelle Aktualität
  fachlich relevant ist.
- **Soll:** Filterzustand in der URL, sofern keine Geheimnisse/Personenbezüge
  entstehen; Nutzen: Zurücknavigation und Lesezeichen.
- **Kann:** zuletzt genutzten harmlosen Navigationsbereich lokal merken;
  Nutzen: schneller Wiedereinstieg, keine geschützten Inhalte offline cachen.

## Bestehende versus geplante Inhalte

Aktuell vorhanden sind Konten/Familien/Einwilligungen, CMS, Events,
Mitbringlisten, Galerien, Chat und manueller Phase-8-Kalender. Lehrkräfte sind
im Content-Modell vorbereitet. WebUntis-Hausaufgaben/-Prüfungen und Wollino-
Menüs sind ausschließlich spezifizierte Zukunftsinhalte. Die biometrische
Suche ist technisch vorhanden, standardmäßig deaktiviert und nicht produktiv
freigegeben.
