# Abnahmeszenarien für die spätere UI-Umsetzung

Die Szenarien prüfen die [UX-Spezifikation](UX-Spezifikation.md) und
[Informationsarchitektur](Informationsarchitektur.md). Beispieldaten sind
synthetisch. Fachliche Zugriffstests bleiben zusätzlich erforderlich.

## Personen und Rollen

1. **Muss – Elternteil, ein Kind:** Nach Login sieht Alex nur das verknüpfte
   synthetische Kind, den relevanten Schultag, eigene Zusagen und erlaubte
   Profildaten. Von Dashboard zu Stundenplan, Event und Einwilligung sind je
   höchstens drei eindeutige Aktionen nötig.
2. **Muss – zwei getrennte Elternkonten:** Beide Konten sehen dasselbe Kind,
   handeln aber unter eigener Identität. Einwilligungen werden getrennt
   dargestellt; fehlende oder widersprüchliche sensible Zustimmung ergibt
   `Klärung nötig`, nicht automatische Freigabe.
3. **Muss – mehrere Kinder:** Der Familienumschalter verändert ausschließlich
   schülerbezogene Karten. Klasse, Hausaufgaben und Prüfungen werden nicht
   vermischt; allgemeine Kontoeinstellungen bleiben gleich.
4. **Später – Schülerkonto:** Falls später aktiviert, sieht das Konto nur das
   eigene Profil und freigegebene schülerbezogene Daten. Nutzen: eigenständiger
   altersangemessener Zugriff; Phase dieses Gates aktiviert kein Konto.
5. **Muss – Klassenlehrkraft:** Sie sieht die eigene Klasse und nur
   freigegebene Kontaktdaten, kann vorgesehene Beiträge pflegen, aber keine
   Rollen oder technischen Einstellungen verändern.
6. **Muss – Content-Bearbeiter:** `Arbeitsbereich` öffnet Dokumente, Beiträge,
   Lehrerprofile und erlaubte Events. Konten, Beziehungen und Systembetrieb
   sind weder in Navigation noch Aktionen erreichbar.
7. **Muss – Moderator:** Meldungen aus Kommentaren, Chat und Galerien sind
   getrennt sortiert; eine Entscheidung zeigt Wirkung und Audit-Hinweis. Die
   normale öffentliche Darstellung verrät keine internen Actor-Daten.
8. **Muss – Administrator:** Nach MFA sind administrative Bereiche klar von
   der Familienansicht getrennt. Nur Hauptadministratoren sehen kritische
   Rollen, Exporte und sensible Löschaktionen.

## Datenschutz und Berechtigungen

9. **Muss – keine Fotoeinwilligung:** Galerie zeigt kein betroffenes Foto;
   Upload/Moderation erklärt neutral `Einwilligung fehlt`. Es gibt keine
   Umgehung über Thumbnail-, Bild- oder Download-URL.
10. **Muss – Widerruf:** Nach Widerruf verschwindet das Foto sofort aus Raster,
    Detail und Download. Der Dialog erklärt Nachprüfung/Löschung; eine spätere
    biometrische Suche bleibt gesperrt.
11. **Muss – abgelaufene Mitgliedschaft:** Bereits geöffnete Links zu Beitrag,
    Dokument, Chat, Kalender, Event und Foto liefern keinen Inhalt. Die PWA
    zeigt keine dauerhaft gecachten geschützten Daten.
12. **Muss – getrennte Familienbeziehung:** Ein gemeinsamer Haushalt oder
    Nachname erzeugt weder Schülerzugriff noch sichtbare Familienbezeichnung.
13. **Muss – biometrische Funktion:** Bei Standardkonfiguration ist kein
    aktiver Suchaufruf sichtbar. Eine Informationsansicht bezeichnet sie als
    deaktiviert/nicht produktiv freigegeben und erklärt lokale Verarbeitung,
    Vorschläge, menschliche Bestätigung und Löschung.

## Geräte und Barrierefreiheit

14. **Muss – schmales Smartphone (320 CSS-px):** Navigation bleibt bedienbar,
    Texte überdecken keine Aktionen, Mitbringkacheln sind mindestens 44 px
    hoch, der verbindliche Schritt ist ohne horizontales Scrollen erreichbar.
15. **Muss – Smartphone quer/Tablet:** Tageskarten wechseln sinnvoll auf zwei
    Spalten, ohne die Desktop-Wochentabelle zu erzwingen. Fokus bleibt nach
    Drehung logisch.
16. **Muss – Tastatur:** Sprunglink erreicht den Inhalt; Tab-Reihenfolge folgt
    visueller Reihenfolge; jeder Dialog hält Fokus, schließt per Escape nur
    ohne Datenverlust und gibt Fokus an den Auslöser zurück.
17. **Muss – Screenreader:** Seitentitel und Landmarken sind eindeutig;
    Statusänderungen werden knapp angekündigt; Icons besitzen Text; Kalender-
    und Mitbringkarten nennen Fach/Artikel, Zustand und Aktion zusammen.
18. **Muss – 200 % Zoom/reduzierte Bewegung:** kein Informationsverlust oder
    überlappender fixer Button; Animationen werden entfernt.

## Netz, Offline und externe Quellen

19. **Muss – langsames Netz:** bestehende Inhalte bleiben stehen, Aktion zeigt
    `Wird gespeichert`; doppelte Reservierungs-/Kommentar-Requests werden
    verhindert. Nach Timeout gibt es Wiederholen ohne doppelte Fachhandlung.
20. **Muss – offline:** neutrale Offline-Seite erklärt, dass geschützte Daten
    nicht offline gespeichert werden. Navigation bietet Wiederholen; keine
    Profile, Chattexte oder Fotos erscheinen aus dem Service-Worker-Cache.
21. **Später – WebUntis unerreichbar:** manueller Phase-8-Plan bleibt sichtbar
    mit letztem erfolgreichen Stand und `derzeit nicht aktualisierbar`. Kein
    Loginversuch, Scraping oder erfundener neuer Stand findet statt.
22. **Später – veraltete WebUntis-Daten:** Status und Zeitstempel sind vor den
    Details wahrnehmbar. Entfallene Stunden bleiben als Entfall erhalten.
23. **Später – Wollino-PDF nicht auslesbar:** Tageskarte zeigt `Prüfung
    erforderlich`, Quelle und Original-Link, aber kein geratenes Menü oder
    Allergen. Andere Dashboardkarten bleiben funktionsfähig.

## Fachabläufe

24. **Muss – gleichzeitige letzte Mitbringreservierung:** Konto A erhält
    Erfolg und sieht `von mir reserviert`; Konto B erhält `Gerade vollständig
    vergeben`, keine Reservierung und aktualisierte Alternativen. Wiederholung
    desselben Requests erzeugt keinen Doppelbestand.
25. **Muss – freie Mitbringposition:** Kategorie, Bezeichnung, Menge und Einheit
    werden validiert; Bestätigung zeigt den verbindlichen Satz. Rücknahme gibt
    die Menge erst nach Bestätigung frei.
26. **Muss – Dokument:** angemeldetes Klassenmitglied findet ein aktualisiertes
    Formular, erkennt Größe/Version und öffnet Original oder SmartForm über
    geschützte Aktion. Fremde Klasse und direkter Medienpfad bleiben gesperrt.
27. **Muss – Beitrag/Kommentar:** Familienbezeichnung stammt aus verifizierter
    Beziehung. Zurückzug und Moderation bleiben als Zustand sichtbar; ein
    geschlossenes Thema bietet keinen aktiven Editor.
28. **Muss – Chatpolling unterbrochen:** sichtbarer Verlauf bleibt, Status
    meldet Unterbrechung, `Erneut versuchen` setzt Polling fort. Push zeigt
    keinen Nachrichtentext; es existieren weder DM- noch Anhang-Aktionen.
29. **Muss – Fotoablauf:** JPEG/PNG durchläuft Personenangabe, Regeln,
    Verarbeitung und Pending-Moderation. Nach Rückzug sind alle Varianten
    unzugänglich; UI verspricht keinen Screenshot-Schutz.
30. **Muss – Push abgelehnt:** Nach einer bewussten Ablehnung fragt die App
    nicht erneut ungefragt. Einstellungen erklären Browserweg und funktionieren
    vollständig ohne Push.
31. **Muss – gelöschte/stale Subscription:** Abmeldung zeigt Erfolg auch bei
    bereits fehlendem Browserabo. Eine stale serverseitige Subscription wird
    entfernt; andere Einstellungen bleiben unverändert.

## Dokumentationsgate

- Alle 31 Szenarien müssen vor UI-Abnahme einem Wireframe oder einer
  spezifizierten Zustandsregel zuordenbar sein.
- `Muss` wird auf Smartphone und Desktop geprüft; Tastatur/Screenreader sind
  keine getrennte spätere Optimierung.
- WebUntis/Wollino-Szenarien bleiben synthetische Spezifikation, bis die
  jeweilige Integration ausdrücklich freigegeben ist.
