# KlassenCMS – Arbeitsaufträge für Datenschutz, Einwilligungen und Onboarding

Stand: 27. August 2026

## Zweck dieses Dokuments

Dieses Dokument enthält aufeinanderfolgende Arbeitsaufträge für die Erstellung und technische Umsetzung der Datenschutz-, Einwilligungs-, Lösch-, Pilot- und Onboarding-Unterlagen des KlassenCMS.

Die Ergebnisse sind Entwürfe und müssen vor einem breiteren Produktivbetrieb durch die tatsächlich verantwortliche Stelle und bei Bedarf durch eine fachkundige Datenschutzberatung geprüft werden.

## Übergreifende Regeln für alle Aufgaben

Arbeite jeden Auftrag vollständig und eigenständig ab.

Vor jedem Auftrag vollständig lesen:

- `C:\Users\Bjoern\.homeops\codex-instructions.md`
- `AGENTS.md`
- `PROJECT.md`
- `docs/Architecture.md`
- `docs/DecisionLog.md`
- `docs/Roadmap.md`
- `docs/TechnicalOverview.md`
- vorhandene Datenschutz-, Sicherheits-, Rollen- und Einwilligungsdokumente
- relevante Modelle, Migrationen, Views, Formulare, Templates und Tests

Zusätzlich beachten:

- Bestehende Benutzerarbeit erhalten.
- Keine echten Zugangsdaten, Einwilligungen oder Personendaten in Git speichern.
- Keine echten Namen von Kindern in Demo-, Test- oder Dokumentationsdaten verwenden.
- Die Freigabe von Björn Radke für seine Person und seine Tochter Mila ist eine reale Pilotentscheidung, aber nicht als personenbezogener Datensatz in Git abzulegen.
- Diese Freigabe muss später innerhalb der laufenden Anwendung versioniert und revisionssicher erfasst werden.
- Weitere Personen werden erst nach eigener beziehungsweise durch ihre Sorgeberechtigten erteilter Einwilligung aktiviert.
- Jede freiwillige Einwilligung beginnt standardmäßig deaktiviert.
- Ablehnung und Widerruf dürfen die normalen Kernfunktionen des KlassenCMS nicht unnötig einschränken.
- Biometrische Funktionen bleiben für alle nicht ausdrücklich freigegebenen Personen deaktiviert.
- Keine öffentliche Bereitstellung durchführen.
- Keine Kommunikation oder Dokumente automatisch an Schule, Eltern oder externe Stellen versenden.
- Nur offizielle und aktuelle Rechtsquellen verwenden.
- Rechtliche Annahmen, offene Verantwortlichkeiten und erforderliche externe Prüfungen eindeutig kennzeichnen.
- Keine rechtliche Verbindlichkeit behaupten.
- Änderungen in kleinen Commits festhalten.
- Nach jedem Auftrag Tests, `git diff --check`, Secret-Prüfung und Dokumentationsprüfung durchführen.

---

# Aufgabe 1 – Datenschutz-Bestandsaufnahme und Verantwortlichkeit

## Ziel

Ermittle und dokumentiere, welche personenbezogenen Verarbeitungen das KlassenCMS bereits enthält oder zukünftig enthalten soll.

## Zu untersuchende Bereiche

Mindestens erfassen:

- Benutzerkonten
- Einladungen und Anmeldung
- Zwei-Faktor-Authentifizierung und Passkeys
- Personen- und Schülerprofile
- Familien- und Sorgebeziehungen
- Kontaktdaten
- Rollen und Klassenmitgliedschaften
- Einwilligungen
- Audit-Protokolle
- Dokumente und geschützte Downloads
- Beiträge und Kommentare
- Veranstaltungen und Mitbringaktionen
- Chat
- Kalender und Stundenplan
- Push-Abonnements
- Galerie und Fotos
- Gesichtserkennung und biometrische Merkmale
- WebUntis
- Wollino-Speisepläne
- Backups
- Protokolle und Sicherheitsdaten
- Schuljahreswechsel und Löschung

## Offene Verantwortlichkeit

Kläre dokumentarisch, ohne eine rechtlich ungesicherte Festlegung zu treffen:

- Wer betreibt das KlassenCMS?
- Erfolgt der Betrieb privat durch den Elternvertreter?
- Erfolgt er im Auftrag oder unter Verantwortung der Schule?
- Welche Rolle haben Klassenlehrkräfte?
- Ist eine Vereinbarung oder ausdrückliche Freigabe der Schule erforderlich?
- Wer bearbeitet Auskunfts-, Berichtigungs-, Widerrufs- und Löschanfragen?
- Wer entscheidet über Datenschutzverletzungen?

Erstelle eine Entscheidungsvorlage mit mindestens diesen Varianten:

1. privates, geschlossenes Elternprojekt
2. gemeinsam mit der Schule verantworteter Betrieb
3. Betrieb im Auftrag der Schule

Beschreibe Auswirkungen und Risiken. Triff keine endgültige rechtliche Festlegung, wenn die tatsächliche Verantwortlichkeit nicht geklärt ist.

## Ergebnisdateien

Erstelle beziehungsweise aktualisiere:

- `docs/privacy/Datenschutz-Bestandsaufnahme.md`
- `docs/privacy/Verantwortlichkeit-Entscheidungsvorlage.md`
- `docs/privacy/Datenflussuebersicht.md`
- `docs/DecisionLog.md`
- `docs/Roadmap.md`

## Qualitätsgate

- Alle vorhandenen Module berücksichtigt
- Verantwortlichkeit nicht erfunden
- Datenquellen, Empfänger, Speicherorte und Löschwege beschrieben
- keine echten Personendaten
- offene Entscheidungen deutlich markiert

---

# Aufgabe 2 – Allgemeine Datenschutzinformation

## Ziel

Erstelle eine verständliche Datenschutzinformation für Eltern, Schüler, Lehrkräfte und weitere berechtigte Klassenmitglieder.

## Anforderungen

Die Datenschutzinformation muss mindestens erläutern:

- Verantwortlicher beziehungsweise noch zu klärende Verantwortlichkeit
- Kontaktmöglichkeit
- Zweck des KlassenCMS
- verarbeitete Datenkategorien
- Rechtsgrundlagen
- Empfänger und Benutzergruppen
- geschlossener Benutzerkreis
- lokale beziehungsweise selbst betriebene Verarbeitung
- eingesetzte technische Dienstleister
- Speicherdauer
- Löschkonzept
- Backups
- Protokollierung
- Betroffenenrechte
- Auskunft
- Berichtigung
- Löschung
- Einschränkung
- Datenübertragbarkeit, soweit anwendbar
- Widerspruch, soweit anwendbar
- Widerruf von Einwilligungen
- Beschwerderecht bei der Aufsichtsbehörde
- Schutz von Minderjährigen
- keine öffentliche Galerie
- keine garantierte Zustellung von Push-Nachrichten
- Status externer Integrationen
- Kontakt bei Datenschutzverletzungen

Erstelle zwei Fassungen:

1. vollständige Datenschutzinformation für Erwachsene
2. kurze, kindgerechte Erklärung in einfacher Sprache

## Ergebnisdateien

- `docs/privacy/Datenschutzinformation.md`
- `docs/privacy/Datenschutzinformation-fuer-Schueler.md`
- `docs/privacy/Quellen-und-Pruefhinweise.md`

## Qualitätsgate

- klare und verständliche Sprache
- keine pauschalen oder ungesicherten Rechtsbehauptungen
- Hinweise nach Art. 13 DSGVO berücksichtigt
- kindgerechte Fassung ohne Angst erzeugende Formulierungen
- Version und Gültigkeitsdatum vorgesehen

---

# Aufgabe 3 – Einwilligungsmatrix

## Ziel

Erstelle eine verbindliche fachliche Matrix aller freiwilligen Entscheidungen.

## Einzeln zu behandelnde Entscheidungen

Mindestens getrennt aufführen:

- eigene E-Mail-Adresse für Klassenmitglieder sichtbar
- eigene Telefonnummer sichtbar
- eigenes Profilfoto sichtbar
- freiwillige Profilinformationen sichtbar
- Schülerfoto sichtbar
- Fotos in Galerien anzeigen
- Namen als geschützte Fotometadaten hinterlegen
- Gesicht lokal analysieren
- biometrische Referenz erzeugen
- lokale Gesichtssuche aktivieren
- Suchergebnisse für bestätigte Sorgeberechtigte anzeigen
- Push-Benachrichtigungen
- einzelne Push-Kategorien
- WebUntis-Verbindung
- Stundenplanimport
- Prüfungsimport
- Hausaufgabenimport
- Abwesenheitsimport
- persönliche Mitteilungen
- Wollino-Speiseplan
- Anzeige von Familienbeziehungen
- Kontaktaufnahme durch Klassenmitglieder

Für jede Entscheidung dokumentieren:

- Zweck
- betroffene Person
- entscheidungsberechtigte Person
- Datenarten
- Empfänger
- Standardwert
- Widerruf
- technische Folgen des Widerrufs
- Löschfolgen
- Abhängigkeiten
- notwendige Textversion
- Audit-Anforderung

## Ergebnisdateien

- `docs/privacy/Einwilligungsmatrix.md`
- `docs/privacy/Einwilligungs-Versionierung.md`

## Qualitätsgate

- keine gebündelte Generaleinwilligung
- alle optionalen Funktionen standardmäßig aus
- Ablehnung ohne unnötige Nachteile
- Elternteil und Kind technisch unterscheidbar
- mehrere Sorgeberechtigte berücksichtigt
- Konfliktfälle zwischen Sorgeberechtigten dokumentiert

---

# Aufgabe 4 – Kontakt- und Profilfreigaben

## Ziel

Erstelle die konkreten Einwilligungstexte für Profile und Kontaktdaten.

## Benötigte Texte

Jeweils einzeln:

- E-Mail-Adresse sichtbar machen
- Telefonnummer sichtbar machen
- eigenes Profilfoto anzeigen
- Schülerfoto anzeigen
- freiwillige Profilbeschreibung anzeigen
- bestätigte Familienbezeichnung anzeigen

Jeder Text muss enthalten:

- konkreten Zweck
- konkreten Empfängerkreis
- Freiwilligkeit
- Standardwert „nicht freigegeben“
- jederzeitigen Widerruf
- Folgen des Widerrufs
- keine öffentliche Darstellung
- keine Freigabe an externe Plattformen

## Ergebnisdateien

- `docs/privacy/Einwilligung-Kontaktdaten-und-Profile.md`
- geeignete versionierte Seed- oder Konfigurationsdaten ohne reale Entscheidungen

## Qualitätsgate

- getrennte Schalter
- verständliche Kurz- und Langtexte
- serverseitige Sichtbarkeitsprüfung
- Tests gegen unberechtigte Anzeige

---

# Aufgabe 5 – Foto- und Galerieeinwilligung

## Ziel

Erstelle die Einwilligungstexte und technischen Regeln für geschützte Klassenfotos.

## Entscheidungen

Mindestens getrennt behandeln:

- Aufnahme beziehungsweise Hochladen
- Darstellung im geschützten KlassenCMS
- Zuordnung eines Namens als Metadatum
- Downloadberechtigung
- Löschanforderung
- Verwendung in lokalen Vorschaubildern
- Verwendung in lokalen Screenshots ausdrücklich ausschließen
- keine öffentliche Veröffentlichung
- keine sozialen Netzwerke
- keine Weitergabe außerhalb der berechtigten Klasse

## Besondere Anforderungen

- Gruppenfotos berücksichtigen
- unterschiedliche Entscheidungen mehrerer abgebildeter Personen berücksichtigen
- gesperrte Personen technisch markieren
- Veröffentlichung bei fehlender Einwilligung verhindern
- Moderations- und Löschablauf definieren
- Schuljahreswechsel berücksichtigen
- Originaldateien und Vorschaubilder berücksichtigen

## Ergebnisdateien

- `docs/privacy/Einwilligung-Fotos-und-Galerie.md`
- `docs/privacy/Fotoregeln-fuer-Eltern-und-Schueler.md`
- `docs/privacy/Gruppenfoto-und-Loeschkonzept.md`

## Qualitätsgate

- kein öffentliches Medienverzeichnis
- Zugriff serverseitig geprüft
- Gruppenbildrisiken dokumentiert
- Widerruf praktisch ausführbar
- Vorschaubilder und Backups in Löschung einbezogen

---

# Aufgabe 6 – Biometrische Gesichtssuche

## Ziel

Erstelle die gesonderte ausdrückliche Einwilligung und Datenschutzdokumentation für die lokale Gesichtssuche.

## Pilotfreigabe

Die technische Vorbereitung und der Pilot sind für Björn Radke und seine Tochter Mila freigegeben.

Diese reale Entscheidung:

- nicht in Git speichern
- erst im laufenden System erfassen
- mit Textversion, Datum, Umfang und handelnder Person dokumentieren
- jederzeit widerrufbar gestalten

Für alle anderen Personen bleibt die Funktion deaktiviert, bis eine eigene wirksame Entscheidung erfasst wurde.

## Einzeln abzufragende Entscheidungen

- Gesicht in einem Foto erkennen lassen
- Gesichtsausschnitt lokal verarbeiten
- biometrisches Embedding erzeugen
- Embedding als Referenz speichern
- Namensvorschläge erzeugen
- nach Fotos des eigenen Kindes suchen
- bestätigte Zuordnungen speichern

## Klar zu erklären

- Verarbeitung ausschließlich in der privaten technischen Umgebung
- keine öffentliche KI-Plattform
- keine automatische endgültige Identifikation
- menschliche Bestätigung erforderlich
- mögliche Fehlzuordnungen
- besondere Sensibilität biometrischer Daten
- verwendetes Modell
- Speicherort
- Löschfrist
- Empfängerkreis
- Widerrufs- und Löschablauf
- keine Nachteile bei Ablehnung

## Zusätzlich erstellen

- Vorprüfung einer Datenschutz-Folgenabschätzung
- vollständiger DSFA-Entwurf, falls die Vorprüfung einen hohen Risikograd ergibt
- Missbrauchs- und Bedrohungsmodell
- Lösch- und Neuaufbauverfahren
- Prozess bei Fehlzuordnungen
- Prozess bei kompromittierten Embeddings
- Regelung für Referenzbilder
- kindgerechte Erklärung

## Ergebnisdateien

- `docs/privacy/Einwilligung-Biometrische-Gesichtssuche.md`
- `docs/privacy/Gesichtssuche-fuer-Kinder-erklaert.md`
- `docs/privacy/DSFA-Vorpruefung-Gesichtssuche.md`
- `docs/privacy/DSFA-Gesichtssuche.md`
- `docs/privacy/Bedrohungsmodell-Gesichtssuche.md`

## Qualitätsgate

- ausdrückliche Einwilligung getrennt von Fotoanzeige
- keine echte Aktivierung ohne gültige Entscheidung
- Widerruf löscht Referenzen, Embeddings und Zuordnungen
- Vision-Dienst kann Löschung vollständig ausführen
- keine echten Bilder oder Embeddings in Tests
- Audit ohne biometrische Nutzdaten
- rechtliche Fachprüfung als offen kennzeichnen

---

# Aufgabe 7 – WebUntis-Datenschutz und Einwilligung

## Voraussetzung

Erst beginnen, nachdem die technische WebUntis-Untersuchung abgeschlossen und die Architekturentscheidung dokumentiert wurde.

## Ziel

Erstelle Texte und technische Regeln für freiwillige, familiengetrennte WebUntis-Verbindungen.

## Grundregeln

- jedes Elternkonto verwendet eigene Zugangsdaten
- Zugangsdaten verschlüsselt speichern
- niemals in Git, Logs, Fehlerausgaben oder Screenshots
- Zugriff ausschließlich auf bestätigte zugehörige Kinder
- keine gemeinsame globale Anmeldung
- Funktionen einzeln aktivierbar
- vollständiges Löschen und Trennen möglich

## Einzeln aktivierbare Datenarten

- Stundenplan
- Änderungen und Ausfälle
- Prüfungen
- Hausaufgaben
- Abwesenheiten
- persönliche Mitteilungen
- Schuljahr
- Ferien
- Stundenraster

## Pilot

Der erste reale Pilot erfolgt ausschließlich mit dem freigegebenen Elternkonto und dem zugeordneten Kind Mila.

Vor dem Livezugriff prüfen:

- verschlüsselte Secret-Verwaltung
- keine Klartextprotokolle
- Host-Allowlist
- TLS
- Zeitüberschreitungen
- Rate Limits
- Sitzungsbeendigung
- Rechteisolation
- Datenminimierung
- Löschung
- Tests mit synthetischen Antworten

## Ergebnisdateien

- `docs/privacy/Datenschutz-WebUntis.md`
- `docs/privacy/Einwilligung-WebUntis.md`
- `docs/integrations/WebUntis-Funktionskatalog.md`
- `docs/integrations/WebUntis-Datenfluss.md`
- `docs/integrations/WebUntis-Pilotplan.md`

## Qualitätsgate

- keine Vorfestlegung auf eine Bibliothek entgegen der Architekturentscheidung
- persönliche Daten je Familie isoliert
- jede Datenart einzeln deaktivierbar
- klare Anzeige von Quelle und Aktualitätszeitpunkt
- kein Zugriff auf nicht freigegebene Kinder
- keine echten Ergebnisse in Git

---

# Aufgabe 8 – Push-Benachrichtigungen

## Ziel

Erstelle die Datenschutzinformation und Auswahltexte für Push-Nachrichten.

## Kategorien

- wichtige Klassenhinweise
- Terminänderungen
- Ausfälle
- Prüfungen
- neue Dokumente
- Mitbring-Erinnerungen
- Chat-Aktivität
- Galeriehinweise
- später WebUntis-Aktualisierungen

## Anforderungen

- Browserberechtigung erst nach ausdrücklicher Nutzeraktion
- Kategorien einzeln wählbar
- vollständige Abmeldung
- veraltete Subscriptions entfernen
- keine sensiblen Detailinformationen auf dem Sperrbildschirm
- Push nicht als garantierter Kommunikationskanal darstellen

## Ergebnisdateien

- `docs/privacy/Datenschutz-Push.md`
- `docs/privacy/Einwilligung-Push.md`

---

# Aufgabe 9 – Lösch-, Widerrufs- und Aufbewahrungskonzept

## Ziel

Definiere nachvollziehbare Fristen und technische Abläufe.

## Zu berücksichtigen

- Benutzerkonten
- Einladungen
- Sitzungen
- Profile
- Kontaktdaten
- Sorgebeziehungen
- Einwilligungen
- Audit-Daten
- Dokumente
- Beiträge und Kommentare
- Chatnachrichten
- Veranstaltungen und Reservierungen
- Fotos
- Vorschaubilder
- biometrische Referenzen
- Embeddings
- Zuordnungen
- WebUntis-Zugangsdaten
- importierte WebUntis-Daten
- Push-Abonnements
- Backups
- Protokolle
- Schuljahresarchive

Unterscheide:

- Widerruf einer Einwilligung
- Löschen einzelner Inhalte
- Austritt aus der Klasse
- Ende des Schuljahres
- vollständige Kontolöschung
- gesetzlich oder organisatorisch notwendige Restaufbewahrung
- Löschung aus Backups

## Ergebnisdateien

- `docs/privacy/Loesch-und-Aufbewahrungskonzept.md`
- `docs/privacy/Widerrufsprozess.md`
- `docs/operations/Loeschlauf-und-Nachweis.md`

## Qualitätsgate

- jede Datenkategorie besitzt eine Regel
- technische Löschung praktisch prüfbar
- Backups berücksichtigt
- Audit enthält keine unnötigen Inhaltsdaten
- keine unbegrenzte Vorratsspeicherung

---

# Aufgabe 10 – Verzeichnis der Verarbeitungstätigkeiten

## Ziel

Erstelle einen vorläufigen Entwurf eines Verzeichnisses der Verarbeitungstätigkeiten.

## Für jede Verarbeitung aufführen

- Bezeichnung
- Zweck
- betroffene Personengruppen
- Datenkategorien
- Rechtsgrundlage
- Empfänger
- Drittlandübermittlung
- Speicherort
- Löschfrist
- technische und organisatorische Maßnahmen
- verantwortliche Rolle
- Risikoeinstufung

## Ergebnisdateien

- `docs/privacy/Verzeichnis-Verarbeitungstaetigkeiten.md`
- `docs/privacy/Technische-und-organisatorische-Massnahmen.md`

---

# Aufgabe 11 – Pilotvereinbarung

## Ziel

Erstelle eine verständliche Vereinbarung für den geschlossenen Testbetrieb.

## Pilotumfang

- Betreiber beziehungsweise Administrator
- Mila als erstes freigegebenes Kind
- anschließend höchstens ein bis zwei befreundete Testfamilien
- nur nach deren ausdrücklicher Anmeldung und Einwilligung
- keine öffentliche Freigabe
- keine Weitergabe von Screenshots
- nur eigene beziehungsweise ausdrücklich freigegebene Daten
- Fehler und Datenschutzprobleme direkt melden
- Testzugang jederzeit entziehbar
- Daten nach Pilotende löschen oder nach erneuter Zustimmung übernehmen

## Ergebnisdateien

- `docs/privacy/Pilotvereinbarung.md`
- `docs/privacy/Pilot-Checkliste.md`
- `docs/privacy/Pilot-Abschlussbewertung.md`

---

# Aufgabe 12 – Erstlogin und Welcome-Onboarding spezifizieren

## Ziel

Spezifiziere einen freundlichen, mobilen und barrierefreien Erstlogin-Ablauf.

## Schritte

1. Willkommen
2. Identität und Familienzuordnung
3. Kontakt- und Profilfreigaben
4. Foto- und Galeriefreigaben
5. gesonderte Gesichtssuchfreigaben
6. Push-Auswahl
7. später optionale WebUntis-Einrichtung
8. Funktionsübersicht
9. Zusammenfassung
10. Abschluss

## Anforderungen

- Fortschrittsanzeige
- Zurück und Weiter
- Zwischenspeicherung
- freiwillige Entscheidungen überspringbar
- notwendige Informationen nicht überspringbar
- Einwilligungen standardmäßig aus
- Kurztext und aufklappbarer Langtext
- Textversion und Datum speichern
- Zusammenfassung vor Abschluss
- spätere Änderung unter „Mehr → Datenschutz und Freigaben“
- erneute Bestätigung bei wesentlichen Textänderungen
- Smartphone zuerst
- vollständige Tastaturbedienung
- Screenreader-Unterstützung
- verständliche Fehlermeldungen
- keine manipulativen Dark Patterns

## Ergebnisdateien

- `docs/ux/Erstlogin-und-Onboarding.md`
- `docs/ux/Onboarding-Wireframes.md`
- `docs/ux/Onboarding-Abnahmeszenarien.md`

---

# Aufgabe 13 – Interaktives Tutorial und lokales Erklärvideo

## Ziel

Erstelle eine wartbare interaktive Produkttour mit synthetischen Daten.

## Kapitel

- Startseite
- Kalender
- Mitbringaktion
- Chat
- Dokumente
- Galerie
- Datenschutz und Einwilligungen
- Benachrichtigungen

## Technische Leitplanken

- serverseitiges HTML
- zentrales CSS
- möglichst wenig JavaScript
- keine neue SPA
- keine externen Video-, Tracking- oder Analysedienste
- keine echten Personen oder Daten
- lokal eingebundene Grafiken
- erneut aufrufbar unter „Mehr → Hilfe“
- pausieren, zurück, weiter und überspringen
- ohne Ton vollständig verständlich
- Untertitel und Texttranskript
- reduzierte Bewegung berücksichtigen
- optional später lokaler Export als WebM oder MP4

## Ergebnisdateien

- `docs/ux/Interaktives-Tutorial.md`
- `docs/ux/Tutorial-Drehbuch.md`
- `docs/ux/Tutorial-Abnahmeszenarien.md`
- lokale Tutorial-Komponenten
- optional lokal erzeugtes Video, nicht öffentlich hochladen

---

# Aufgabe 14 – Technische Umsetzung des Onboardings

## Voraussetzung

Aufgaben 1 bis 13 sind fachlich abgeschlossen.

## Ziel

Implementiere den spezifizierten Erstlogin-Ablauf im bestehenden Django/Wagtail-Monolithen.

## Anforderungen

- vorhandene Benutzer-, Personen-, Schüler-, Familien- und Einwilligungsmodelle wiederverwenden
- keine parallelen Attrappenmodelle
- notwendige Erweiterungen über Migrationen
- versionierte Einwilligungen
- serverseitige Rechteprüfung
- sicherer Abbruch und Fortsetzung
- Onboarding-Status pro Benutzer
- erneutes Onboarding nach relevanter Textänderung
- bestätigte Sorgebeziehung als Voraussetzung für kindbezogene Entscheidungen
- Konfliktfälle mehrerer Sorgeberechtigter behandeln
- Widerruf praktisch umsetzen
- Audit ohne unnötige personenbezogene Inhalte
- Pilotfreigabe für Björn und Mila nur zur Laufzeit erfassen
- keinerlei reale Pilotdaten in Fixtures oder Git

## Tests

Mindestens:

- neuer Elternlogin
- Schülerlogin
- getrennte Elternkonten
- unbestätigte Sorgebeziehung
- Ablehnung aller optionalen Funktionen
- teilweise Zustimmung
- vollständiger Widerruf
- geänderte Textversion
- biometrische Funktion ohne Einwilligung gesperrt
- biometrische Funktion mit gültiger Pilotentscheidung
- serverseitige Rechteprüfung
- Tastaturbedienung
- 320 bis 1440 Pixel
- 200 Prozent Zoom
- keine Dark Patterns

---

# Aufgabe 15 – Gesamtes Datenschutz-Qualitätsgate

## Ziel

Prüfe Dokumentation und Implementierung gemeinsam.

## Prüfungen

- alle Texte versioniert
- Quellen aktuell und offiziell
- Verantwortlichkeit sichtbar offen oder verbindlich geklärt
- Einwilligungen granular
- Standardwerte deaktiviert
- Widerruf funktioniert
- Löschung funktioniert
- Familienisolation funktioniert
- keine echten Daten in Git
- keine Geheimnisse in Git oder Logs
- keine öffentlichen Medienpfade
- kein Biometriezugriff ohne Einwilligung
- keine WebUntis-Nutzung ohne Aktivierung
- Push vollständig abmeldbar
- Onboarding barrierefrei
- Tutorial ohne echte Daten
- Docker-Tests
- Migrationen ohne Drift
- Backup und Restore
- Non-root
- Read-only-Root-Dateisystem
- ausschließlich lokale Development-Ports
- `git diff --check`
- Secret-Scan
- Dokumentlinks

## Abschlussbericht

Liefere:

- erstellte Dokumente
- implementierte Funktionen
- Testzahlen
- offene rechtliche Fragen
- offene organisatorische Entscheidungen
- bekannte technische Grenzen
- Pilotbereitschaft
- ausdrücklich noch nicht produktionsreife Bereiche
- Commit-IDs
- Push-Status
- Bestätigung, dass keine öffentliche Veröffentlichung erfolgt ist

## Abschlussbedingung

Das Qualitätsgate darf nicht allein deshalb als bestanden gelten, weil Dokumente vorhanden sind. Widerruf, Rechteisolation, Löschung und Sperrung biometrischer Funktionen müssen technisch nachgewiesen sein.