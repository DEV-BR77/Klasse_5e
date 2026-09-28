# Django-Datenmodell und Entscheidungslogik

Stand: 13.09.2026  
Status: Bestandsaufnahme und Zielentwurf; keine zusätzliche Implementierungs- oder Migrationsfreigabe.

Dieses Dokument trennt den vorhandenen Django-Modellbestand von fachlichen
Erweiterungen, die aus den Projektentscheidungen und den bisherigen
Anforderungen folgen. Es beschreibt Felder, Beziehungen und die Kriterien,
nach denen Daten gelesen, angezeigt, aktiviert oder abgelehnt werden.

## 1. Architekturrahmen

KlassID bleibt ein modularer Django-/Wagtail-Monolith mit PostgreSQL. Die
fachliche Trennung erfolgt über Django-Apps und Policies, nicht über
Microservices.

```text
UserAccount
├── Person ── Household
│   ├── GuardianChildRelationship ── StudentProfile
│   └── ClassMembership ── SchoolClass ── School ── SchoolYear
├── Rollen / Einwilligungen / Audit
├── Benachrichtigungen / Onboarding
└── Fachmodule: Content, Events, Media, Chat, Kalender, Adapter, Meals
```

Verbindliche Grundsätze:

- Jeder geschützte Zugriff benötigt ein aktives Konto und einen gültigen
  Klassenkontext.
- Kinder sind `Person`-Datensätze; Sorgeberechtigte besitzen getrennte Konten.
- Beziehungen, Rollen, Einwilligungen und Sichtbarkeit werden getrennt und
  zeitlich geprüft.
- Zugangsdaten werden verschlüsselt oder gehasht und niemals protokolliert.
- `status`, `state`, Gültigkeits- und Zeitfelder sind fachliche Daten und
  dürfen nicht nur aus einer UI-Farbe abgeleitet werden.

## 2. Feldkonventionen

| Feld | Bedeutung |
|---|---|
| `public_id` / UUID | nicht erratbare externe Kennung |
| `ForeignKey` | fachliche Zuordnung mit bewusstem Löschverhalten |
| `OneToOneField` | genau eine Konfiguration je Besitzer |
| `ManyToManyField` | Mehrfachzuordnung ohne Stammdatenkopie |
| `*_encrypted` / `*_ciphertext` | verschlüsseltes Geheimnis, nur kurzzeitig entschlüsselt |
| `*_hash` / `fingerprint` | Vergleichs-, Token- oder Idempotenzwert |
| `valid_from` / `valid_until` | zeitliche Berechtigung oder Gültigkeit |
| `*_at` | Erstellung, Änderung, Prüfung, Synchronisation, Widerruf oder Löschung |
| `JSONField` | strukturierte Zusatzdaten; nicht für Kernbeziehungen |

## 3. Identität, Schule und Berechtigungen (`core`)

| Modell | Variablen / Inhalte | Zweck |
|---|---|---|
| `UserAccount` | E-Mail, Verifizierung, Sperrzeit, E-Mail-/Passwort-Leakstatus, Leakanzahl und Prüfzeiten, ausgewähltes Theme | Login und persönlicher Sicherheitsstatus |
| `Person` | Konto, Namen, Geschlecht, Geburtsdatum, Telefon, alternative Kontakte, Adresse, optionale grobe Wohnkoordinaten, Chatname, Listenmodus, Foto/Avatar, Kontakt-E-Mail, Feld-/Kontakt-Sichtbarkeit | fachliche Person und Profil |
| `Household` | Bezeichnung, Mitglieder | Familienhaushalt; allein keine Berechtigung |
| `StudentProfile` | Person, Profilfoto-Referenz | Schülerkennzeichnung |
| `GuardianChildRelationship` | erwachsene Person, Kind, Beziehungstyp, gesetzliche Sorge, Ansichts-/Profil-/Einwilligungsrechte, Status, gültig von/bis, Prüfer und Prüfzeit | ausdrückliche Eltern-/Sorgeberechtigten-Kind-Zuordnung; niemals automatisch für Geschwister |
| `AdditionalAuthorizedPerson` | erwachsene Person, Haushalt, Status, Verifizierungsdaten, eingeladen durch, Zeitpunkte | weitere berechtigte Person ohne automatische Elternrechte |
| `ChildAccessGrant` | berechtigte Person, Kind, Rolle, sicht-/les-/nutz-/bestätigbare Module oder Rechte, Status, gültig von/bis, vergeben durch, Widerruf | explizite Einzelzuweisung je Kind |
| `AdditionalAuthorizedPerson` | erwachsene Person, Haushalt, Status, Verifizierungsdaten, eingeladen durch, Zeitpunkte | weitere berechtigte Person ohne automatische Elternrechte |
| `ChildAccessGrant` | berechtigte Person, Kind, Rolle, sicht-/les-/nutz-/bestätigbare Module oder Rechte, Status, gültig von/bis, vergeben durch, Widerruf | explizite Einzelzuweisung je Kind |
| `ClassMembership` | Klasse, Person, Status, gültig von/bis | Klassenmitgliedschaft |
| `Role` | Schlüssel, Anzeigename, Beschreibung, Systemrolle, zulässige Aktionen, aktiv | fachliche Rolle wie Elternteil, Kind, Stiefelternteil, Großelternteil, Lehrkraft oder Admin |
| `RoleAssignment` | Benutzer/Person, Haushalt, optionale Schule/Klasse, Rolle, aktiv, gültig von/bis, vergeben durch, Zeitpunkt | konkrete Rollenvergabe in einem klaren Geltigkeitsbereich |
| `RoleModulePermission` | Rolle, Modul, sichtbar, lesbar, nutzbar, erstellen, bearbeiten, bestätigen, verwalten, aktiv | Standardrechte einer Rolle je Modul |
| `PrincipalModulePermission` | Benutzer/Person, Modul, optionaler Haushalt/Schule/Klasse, sicht-, les- und nutzbare Aktionen, erlaubt/verweigert, Begründung, gültig von/bis, vergeben durch | individuelle Ausnahme oder Einschränkung gegenüber der Rollenberechtigung |
| `SchoolYear` | Label, Start, Ende, aktiv | Schuljahreskontext |
| `School` | Quellkennung, Name/Suchname/Kürzel/Slug, Adresse/Kontakte, Schulart/Träger, Quelle/Rohdaten, Koordinaten, Logo, aktivierte Module/Menüpunkte, aktiv, Zeitpunkte | Schulstammdaten |
| `SchoolClass` | Schule, Name, Code, Schuljahr, Displayname, Logo, aktivierte Module/Menüpunkte, Jahrgang, Status, gültig von/bis | Klassenmandant |
| `ClassDomain` | Klasse, Hostname, reservierte Ausnahme, aktiv | Domainrouting |
| `BrandingAsset` | Schule/Klasse, Art, Bild/Preview, Alttext, Rechtehinweis, Rechte bestätigt, Status, Ersteller, Zeitpunkte | freigegebene Gestaltung |
| `LogoRequest` | Schule/Klasse, Antragsteller, Wunschtext, Farben, Motive, Stil, Referenzen, transparenter Hintergrund, Verwendungszweck, Status, Adminnotiz, Zeitpunkte | Logo-Briefing und Freigabe |

### Registrierung und Lebenszyklus

| Modell | Variablen / Inhalte | Zweck |
|---|---|---|
| `RegistrationApplication` | E-Mail, Name, Passwort-Hash, Status, E-Mail-Token/-ablauf/-bestätigung, Schule/Klasse, Prüfer, Grund, Prüfzeit, Familienantrag, Zeitpunkte | Antrag vor Aktivierung |
| `ActivationGrant` | Antrag, Token-Hash, Ablauf, Nutzung, Widerruf, Erstellung | einmalige Aktivierung |
| `Invitation` | E-Mail, Token-Hash, Ablauf/Nutzung, Einladender, Namen, Klasse, Haushalt, Familienantrag, Erstellung | persönliche Einladung |
| `FamilyAccessCode` | Batch/Seriennummer, Token-Hash, Klasse, Ablauf, Eingangs-/Abschluss-/Widerruf, Ersteller, bestehender Sorgeberechtigter, Beziehungstyp, Familienname, Nutzungsgrenzen | Familienzugang |
| `FamilyRegistrationRequest` | Zugangscode, Haushaltsname, weitere Erwachsene, Kinder, Haushalt, Status, Zeitpunkte | Familienantrag |
| `FamilyChildAccount` | Familienantrag, Namen, E-Mail, Passwort-Hash, aktiviertes Konto, Erstellung | separater Kinderzugang |
| `ChildJoinRequest` | Sorgeberechtigter, Name, Klasse, Status, Erstellung, Prüfer | nachträgliche Kinderzuordnung |
| `AccountDeletionRequest` | Konto, Antrag, frühester Ausführungszeitpunkt, Status, Bearbeitung, Fehlergrund | kontrollierte Löschung |
| `DepartureRetentionCase` | Kind, Klasse, Austritt, Löschtermin, Zugriffs- und Bearbeitungszeit | Austritt und Restaufbewahrung |

## 4. Portalsteuerung und Adapter

| Modell | Variablen / Inhalte | Zweck |
|---|---|---|
| `PortalTheme` | Schlüssel, Name, Beschreibung, Zielgruppe, hell/dunkel, aktiv, Primär-/Akzent-/Hintergrund-/Oberflächen-/Textfarben, Radius, Schattenstärke, Zeitpunkte | Theme-Tokens |
| `PortalConfigurationKey` | Schlüssel, Version, Datentyp, Standardwert, Schule/Klasse überschreibbar, aktiv | erlaubte Konfiguration |
| `PortalConfigurationValue` | Schlüssel, Schule/Klasse, JSON-Wert, Änderer, Zeitpunkt | konkreter Override |
| `PortalModule` | Schlüssel, Label, Stabilität, Standardaktivierung, Abhängigkeiten, letzter Test | verfügbares Modul |
| `ModuleRequirement` | Modul, Schlüssel, Label, Datentyp, Pflichtfeld, Zielbereich, Validierungsregel, Fehlermeldung, Reihenfolge, aktiv | maschinenprüfbare Voraussetzungen für Einrichtung und Nutzung |
| `ModuleConfiguration` | Modul, Schule/Klasse/Haushalt/Person, verschlüsselte Werte oder sichere Referenzen, Vollständigkeitsstatus, geprüft durch, Prüfzeit, gültig von/bis | konkrete Konfiguration eines Moduls ohne unvollständige Aktivierung |
| `PortalModuleOverride` | Modul, Schule/Klasse, aktiv, Begründung, Änderer, Zeitpunkt | fachliche Freigabe eines Moduls im Schul- oder Klassenkontext |
| `SchoolModuleSource` | Schule/Klasse, fachliches Modul, Adapter, Adaptermodul, Priorität, Zugangsscope, Fallbackregel, aktiv, gültig von/bis | legt fest, welcher Adapter eine Funktion für diese Schule liefert |
| `ModuleAccessPolicy` | Modul, Schule/Klasse, Rolle, sichtbar, lesbar, nutzbar, schreibbar, bestätigbar, aktiv, gültig von/bis | rollenbezogene Freigabe im konkreten Schulkontext |
| `DashboardPlacement` | Benutzer/Person, optional Schule/Klasse, Modul/Kachel, Position, Bereich, sichtbar, Darstellung, aktiv | persönliche Zusammenstellung und Reihenfolge des Dashboards |
| `MenuItem` | Name, Route, Icon-Schlüssel, Elternpunkt, Reihenfolge | Menübaum |
| `PortalAdapter` | Schule, Provider, Name, Basis-URL, Projekt-/Institutionskennung, Schulnummer, Konfigurationsnotiz, aktiv, Kinderzugang erforderlich, letzte Prüfung/Status/Meldung, Zeitpunkte | Adapterkatalog |
| `PortalAdapterModule` | Adapter, Schlüssel, Label, Beschreibung, aktiv, Kinderzugang erforderlich, erlaubte Klassen, Konfiguration, Status, Synczeit/Meldung, Zeitpunkte | einzelne Adapterfunktion |
| `ChildModuleConnection` | Kind, Modul, aktiv, Verbindungsstatus, eingerichtet durch, Zeitpunkt | kindbezogene Modulaktivierung |
| `SchoolmanagerConnection` | Konto, Kind, verschlüsselter Benutzername/Passwort, Status/Detail, Prüf-/Synczeiten, Zeitpunkte | Schulmanager-Verbindung |

## 5. Kalender, Stundenplan und WebUntis

| Modell | Variablen / Inhalte | Zweck |
|---|---|---|
| `TimeGrid` | Schule, Name, gültig von/bis | Zeitraster |
| `LessonPeriod` | Zeitraster, Nummer, Beginn, Ende | Unterrichtsperiode |
| `SchoolBreak` | Zeitraster, Bezeichnung, Beginn/Ende, nach Periode | Pausen |
| `TimetableEntry` | Klasse, Schuljahr, Wochentag, Beginn/Ende, Fach, Raum, Lehrer, Änderung | sichtbarer Stundenplan |
| `CalendarEntry` | Klasse, Schuljahr, Art, Titel, Beginn/Ende, Raum, Details, Revision, Änderung | Termine und Kalender |
| `CalendarChange` | Eintrag, Revision, geänderte Felder, Änderer, Zeitpunkt | Änderungsvergleich |
| `CalendarDelivery` | Eintrag, Revision, Benutzer, Zeitpunkt | doppelte Hinweise verhindern |
| `ICalSubscription` | Benutzer, Klasse, Token-Hash, aktiv, Erstellung, Widerruf | widerrufbarer Feed |
| `WebUntisConnection` | Konto, optionales Kind, Adapter, Server/Schule, verschlüsselter Benutzername/Passwort, externe Schüler-ID, Status/Detail, Prüf-/Erfolgszeiten, Sync aktiv, Zeitpunkte | aktuelle Verbindung |
| `WebUntisFeaturePreference` | Verbindung, Funktionsschlüssel, aktiv, Status, Änderung | getrennte Freigabe je Kategorie |
| `WebUntisLesson` | Verbindung, externe Signatur, Fach-/Lehrercode, Beginn/Ende, ausgeschriebenes Fach, Raum, Lehrername, Status, Quell-/Abrufzeit, Sichtbarkeit, Löschzeit | importierter Stundenplan |
| `WebUntisHomework` | Verbindung, externe Signatur, Fach, Aufgabedatum, Fälligkeit, Text, Quellstatus, Abrufzeit, Sichtbarkeit, Löschzeit | Hausaufgaben |
| `WebUntisAbsence` | Verbindung, externe ID, Datum/Uhrzeit von/bis, Quellstatus, Abrufzeit | gelieferte Abwesenheit |
| `AbsenceDraft` | meldendes Konto, Kind, Datum/Uhrzeit von/bis, Grund, Notiz, Erstellung | Formularentwurf |
| `AbsenceSubmission` | einmaliger Token, Konto, Kind, Fingerprint, Status, Erstellung, Abschluss | einzelner Sendeversuch |
| `HomeworkProgress` | Kind, externe Aufgabe, erledigt, erledigt durch, Zeitpunkte | Erledigungsstatus |
| `SyncSchedule` | Quelle, aktiv, Modus/Intervall, Zeitzone, Zeiten, Wochentage/Ferien, Laufgrenzen, nächste/gesperrte/letzte Laufdaten, Fehlerklasse | Synchronisationsplanung |
| `SyncRun` | Verbindung, Auslöser, Status, Idempotenzschlüssel, Start/Ende, Änderungsanzahl, Kategorien, Fehlercode, Versuche, Terminalhinweis | nachvollziehbarer Sync-Lauf |
| `WebUntisSubjectMapping` | Adapter, Fachcode, Anzeigename, Änderung | lesbare Fächer |
| `WebUntisTeacherMapping` | Adapter, Lehrercode, Anzeigename, Änderung | lesbare Lehrer |
| `WebUntisCalendarSubscription` | Verbindung, Token-Hash, aktiv, Erstellung, Widerruf | Adapterkalenderfeed |

### Geplante Ergänzung: Familienzugang

Die gewünschte Priorität „Familienzugang zuerst, Kinderzugang als Fallback“ ist
im aktuellen Modell noch nicht vollständig abgebildet. Dafür ist ein eigenes
`WebUntisFamilyConnection` mit Haushalt/Familienbesitzer, Adapter, Server,
Schule, verschlüsseltem Benutzernamen/Passwort, Status, Prüf-/Erfolgszeiten und
`sync_enabled` erforderlich.

Die Verbindung darf nicht selbst die Berechtigung ersetzen. Sie ist nur eine
technische Datenquelle. Welche Person sie verwenden darf, wird über
`RoleModulePermission` und `ModuleAccessPolicy` entschieden. Dadurch kann zum
Beispiel der Zugang für Abwesenheiten technisch vorhanden sein, aber nur
Elternteilen die Funktion „Abwesenheit melden“ angeboten werden.

Die Auswahl soll lauten:

1. fachliches Modul und Schule des Kindes bestimmen;
2. wirksame Rollen- und individuelle Modulrechte prüfen;
3. aktive Familienverbindung für dieselbe Schule und Funktion auswählen;
4. sonst aktive Kinderverbindung des betreffenden Kindes auswählen;
5. niemals Kinderzugangsdaten überschreiben;
6. Abwesenheiten nur bei aktivem Adapter, aktivierter Funktion und gültiger
   Berechtigung anzeigen oder senden.

Das ist eine eigene Migration mit Policy-, Sicherheits- und Fallbacktests.

## 6. Inhalte, Events und Chat

| App / Modellgruppe | Modelle und wesentliche Inhalte |
|---|---|
| `content` | `ProtectedDocument` (Klasse/Jahr, Titel, Beschreibung, Kategorie, Gültigkeit, Version, Dateien, Status, Ersteller), `TeacherProfile` (Person, Klasse, Fächer, Funktion, Schul-E-Mail, Sprechzeiten, Einführung und Sichtbarkeit), `Post`, `Comment`, `CommentReport` |
| `events` | `Event`, `ContributionCategory`, `ContributionItem`, `Reservation`, `EventParticipation`, `ReminderDelivery`, `EventPoll`, `EventPollOption`, `EventPollVote`; Zeiten, Klassenkontext, Status, Organisatoren, Mitbringmengen, Reservierungen und Abstimmungen |
| `chat` | `ChatRetentionCategory`, `ChatRoom`, `DirectConversation`, `ChatMessage`, `ChatReadState`, `ChatReport`, `ChatPreference`; Räume, zwei private Teilnehmer, Nachrichtentext/Anhänge, Lesestand, Meldungen, Filter- und Aufbewahrungsstatus |

Für alle drei Gruppen gilt: Klasse und aktive Mitgliedschaft werden vor dem
Lesen geprüft. Private Gespräche sind paarweise geschützt; Moderationsrechte
öffnen nicht automatisch fremde Verläufe.

## 7. Medien, Speiseplan, Lernportale, Mobilität und Vision

| App | Modelle | Entscheidungsregeln |
|---|---|---|
| `media` | `Gallery`, `Photo`, `PhotoSubjectDeclaration`, `PhotoReport`, `PhotoModerationDecision` | Medienzugriff benötigt Klasse, Status und ggf. Consent; Originale bleiben geschützt |
| `meals` | `MealPlan`, `MealDay`, `MealOption` | Quelle, Woche, Gültigkeit, Veröffentlichung, Komponenten-, Zusatzstoff- und Allergen-Codes |
| `itslearning` | `ItslearningConnection`, `ItslearningCourse`, `ItslearningUpdate`, `ItslearningCalendarItem`, `WebDavSpace` | externe IDs und verschlüsselte Verbindung; Klasse/Kind bleibt lokaler Scope |
| `mobility` | `MobilityListing`, `MeetingPoint`, `MobilityReaction`, `PickupDisclosure`, `MobilityReport`, `MobilityListingView` | grobe Bereiche öffentlich im Klassenkontext; exakte Abholadresse nur verschlüsselt, befristet und widerrufbar |
| `biometrics` | `BiometricCollection`, `BiometricProfile`, `VisionPhotoSubmission`, `BiometricMatch`, `BiometricReference` | nur opaque IDs, aktuelle Einwilligung, manuelle Bestätigung; standardmäßig deaktiviert |

Die Fahrgemeinschaft kann aus der Oberfläche entfernt werden, ohne historische
Datensätze automatisch zu löschen. Eine solche Datenlöschung wäre eine eigene
fachliche Entscheidung.

## 8. Consent, Audit, Monitoring und Push

| Modell | Variablen / Inhalt | Regel |
|---|---|---|
| `ConsentType` | Schlüssel, Label, Kategorie, Zweck, Empfänger | Zweckdefinition |
| `ConsentTextVersion` | Typ, Version, Text, Wirksamkeitsbeginn | nachvollziehbare Textversion |
| `ConsentDecision` | Typ/Version, betroffene und entscheidende Person, Entscheidung, Gültigkeit, Widerruf, Quelle | nur aktuelle positive Entscheidung zählt |
| `AuditEvent` | Zeitpunkt, Akteur, Aktion, Zieltyp/-ID, Metadaten | Sicherheitsnachweis ohne Geheimnisse |
| `MonitoringSnapshot` | Quelle, Zeitpunkt, Messwerte | Health, Speicher, Traffic und Verlauf |
| `MonitoringComponent` | Komponente, Zustand, Wechselzeit, letzte Meldung | aktuelle Systemampel |
| `PushSubscription` | Benutzer, Endpoint-Hash/Endpoint, Browser-Schlüssel, aktiv, Gerät, Erstellung | Pushgerät |
| `PushPreference` | Benutzer, Kategorie, aktiv, Zeitpunkt | persönliche Push-Auswahl |
| `UserNotification` | Benutzer, Klasse, Kategorie, Objekt/Revision, Titel, Kurztext, Ziel, Erstellung, gelesen | In-App-Postfach und Zähler |
| `PilotReport` | Meldender, Klasse, Art, Seitenpfad, Beschreibung, Screenshot, Erstellung, Erledigung | Testfeedback |
| `OnboardingState` / `TutorialState` | Benutzer, Schritt, Abschluss, Ausblenden, Policyversion, Zeitpunkte | fortsetzbarer Einstieg |

## 9. Entscheidungs- und Abfragelogik

### Geschützter Zugriff

```text
angemeldet?
  nein → Login
  ja → Konto aktiv und nicht gesperrt?
        nein → Zugriff verweigern
        ja → aktive Klassenmitgliedschaft im Kontext?
              nein → Zugriff verweigern
              ja → Rollen-/Objektpolicy erfüllt?
                    nein → 403 oder erlaubter leerer Zustand
                    ja → Daten nach Klasse, Zeitraum und Sichtbarkeit laden
```

### Elternzugriff auf ein Kind

`GuardianChildRelationship` muss aktiv sein, das aktuelle Datum muss im
Gültigkeitsbereich liegen, `may_view_student_profile` muss wahr sein und die
Klassenmitgliedschaft des Kindes muss aktiv sein. Für Profil- und
Einwilligungsänderungen gilt zusätzlich das jeweils passende `may_manage_*`-
Recht. Ein Haushalt allein berechtigt nicht. Für weitere berechtigte Personen
ist stattdessen ein aktiver `ChildAccessGrant` mit passender Rolle und passendem
Modulrecht erforderlich.

### Personen- und kindbezogene Rollen

Die Rolle wird nicht allein am Haushalt oder am Benutzerkonto festgemacht.
Entscheidend ist immer die konkrete Zuordnung zur einzelnen Person und zum
einzelnen Kind.

Vorgesehen sind drei fachliche Gruppen:

1. `Erziehungsberechtigte`: Vollzugriff nur für die Kinder, für die eine
   aktive und geprüfte `GuardianChildRelationship` besteht.
2. `Kinder`: Zugriff auf die eigenen Funktionen, aber kein Elternrecht.
3. `Weitere berechtigte Personen`: zum Beispiel Lebensgefährte, Großmutter,
   Großvater oder Pflegeperson. Diese erhalten nur ausdrücklich vergebene
   `ChildAccessGrant`-Rechte.

Ein Grant gilt immer für ein konkretes Kind. Soll eine Person zwei Kinder sehen,
werden zwei Grants angelegt. Ein gemeinsamer Haushalt, ein gleicher Nachname,
eine Einladung oder die Beziehung zu einem Geschwisterkind erzeugen keinen
Zugriff auf ein anderes Kind.

Beispiel einer Patchwork-Familie:

```text
Mutter       ── Erziehungsberechtigte ── Kind 1
Mutter       ── Erziehungsberechtigte ── Kind 2
Lebensgefährte ── ChildAccessGrant     ── Kind 1
Vater        ── Erziehungsberechtigte ── Kind 2
Vater        ── kein Grant             ── Kind 1
```

Die Vollrechte des Lebensgefährten für Kind 1 werden nicht aus seiner
Partnerschaft zur Mutter abgeleitet, sondern durch eine geprüfte, explizite
Zuweisung. Ob er dieselben Rechte wie die Mutter erhält, wird zusätzlich über
die Modulrechte der zugewiesenen Rolle festgelegt.

### Modul- und Menüaktivierung

```text
Klassenoverride > Schuloverride > PortalModule.default_enabled
→ Abhängigkeiten prüfen
→ Adapterstatus und Berechtigung prüfen
→ erst dann Menüpunkt und Funktion als aktiv anzeigen
```

Die Anzeige im Menü ist niemals Ersatz für eine serverseitige Policy.

### Vollständigkeit und Formularabschluss

Ein Modul, Zugang, Rollenprofil oder `ChildAccessGrant` darf erst als aktiv
oder nutzbar gelten, wenn alle fachlichen Pflichtangaben vollständig und
valide gespeichert wurden. Pflichtangaben werden nicht nur im HTML-Formular,
sondern zusätzlich durch Django-Form-, Modell- und Policy-Validierung geprüft.

Beispiele für Anforderungen:

- eine weitere berechtigte Person benötigt Identität, Kontakt, Verifizierung,
  Rolle und mindestens eine konkrete Kindzuweisung;
- eine Familienverbindung benötigt Haushalt, Schule/Adapter, verschlüsselten
  Benutzernamen, verschlüsseltes Passwort und einen gültigen Status;
- ein Adaptermodul benötigt eine aktive Schulfreigabe, eine unterstützte
  Quelle und alle in `ModuleRequirement` definierten Konfigurationswerte;
- eine schreibende oder bestätigende Funktion benötigt zusätzlich das passende
  Modulrecht und gegebenenfalls eine Einwilligung.

Unvollständige Datensätze dürfen als Entwurf existieren, aber nicht als aktive
Verbindung, sichtbares nutzbares Modul oder wirksame Berechtigung erscheinen.
Der Speichervorgang muss atomar sein: Entweder werden alle zusammengehörigen
Daten gespeichert oder keine teilweise aktivierte Konfiguration bleibt zurück.

Bei „Speichern“ werden die Anforderungen erneut serverseitig geprüft. Bei
Fehlern bleibt das Formular geöffnet, die betroffenen Felder werden markiert
und eine verständliche Meldung wird angezeigt, zum Beispiel „Die Daten sind
unvollständig. Bitte ergänze die markierten Angaben.“

Bei „Abbrechen“ wird vor dem Verwerfen ungespeicherter Änderungen bestätigt:
„Sind Sie sicher? Die Daten werden verworfen.“ Erst nach Bestätigung wird der
Entwurf geschlossen. Bereits gespeicherte Daten werden dadurch nicht gelöscht.

Erfolg, Validierungsfehler und Abbruch verwenden ein einheitliches, dezentes
Toast-/Hinweis-Element: ungefähr zwei Sekunden sichtbar, anschließend über
etwa eine Sekunde ausblendend. Die Meldung darf nicht die einzige
Fehlerinformation sein; sie ergänzt Feldmarkierungen und eine verständliche
Fehlerbeschreibung.

### Fachliche Module, Datenquellen und Rollen

Adaptermodule werden nicht direkt als Menüpunkte an Familien weitergereicht.
Stattdessen wird zuerst die fachliche Funktion ermittelt, zum Beispiel
`timetable`, `homework`, `exams`, `substitutions`, `absences` oder
`contract_signing`. `SchoolModuleSource` ordnet diese Funktion dem an der
Schule tatsächlich verwendeten Adapter und dessen Adaptermodul zu.

Die effektive Berechtigung wird danach in dieser Reihenfolge berechnet:

```text
Schul-/Klassenmodul aktiv?
→ Quelle/Adapter für die Funktion aktiv und gesund?
→ Rolle der Person im aktuellen Haushalt-/Schulkontext ermitteln
→ Rollenstandard anwenden
→ individuelle Erlaubnis oder Sperre anwenden
→ Gültigkeitszeitraum und Einwilligung prüfen
→ Modul sichtbar, lesbar, nutzbar oder bearbeitbar anbieten
```

Dabei werden mindestens Sichtbarkeit und fachliche Aktionen getrennt:

- `visible`: Das Modul darf im Menü, Dashboard oder Profil erscheinen.
- `read`: Die Person darf Daten sehen.
- `use`: Die Person darf eine Funktion ausführen.
- `create`/`edit`: Die Person darf Daten erfassen oder ändern.
- `confirm`: Die Person darf verbindliche Aktionen wie Unterschriften oder
  Abwesenheitsmeldungen bestätigen.
- `manage`: Die Person darf Freigaben und andere Benutzerrechte verwalten.

Beispiel: Eine Oma kann die Module Kalender und Stundenplan sehen und lesen,
aber das Vertragsmodul sowie „Abwesenheit melden“ bleiben unsichtbar oder nur
lesbar. Ein Elternteil kann im Vertragsmodul zusätzlich `confirm` erhalten.
Ein einzelnes Kind kann Stundenplan und Hausaufgaben verwenden, aber keine
Elternfunktion ausführen.

Das Dashboard verwendet anschließend nur noch die erlaubten fachlichen
Module. `DashboardPlacement` speichert lediglich die persönliche Darstellung;
eine Platzierung kann niemals ein fehlendes Modulrecht umgehen.

### Zeitliche Daten und Synchronisation

Klasse, Schuljahr, Zeitraum, Verbindung und Funktionsfreigabe müssen passen.
Externe Fingerprints/IDs deduplizieren Importe. Bei Revisionen gewinnt die
höhere gültige Revision bzw. der neueste bestätigte Quellzeitpunkt; lokale
Bearbeitungen dürfen nicht blind überschrieben werden.

### Abwesenheiten

1. Beziehung, Klasse und Berechtigung prüfen;
2. Adapter und Funktion `absences` prüfen;
3. Familienzugang verwenden, sonst Kinderzugang als Fallback;
4. externe Abwesenheiten über ID aktualisieren;
5. Formular als `AbsenceDraft` speichern;
6. einzelnen Sendeversuch mit `AbsenceSubmission` sperren;
7. Erfolg nur nach frischem Rücklesen eines passenden externen Eintrags;
8. Fehler sichtbar melden und nicht automatisch wiederholen.

### Sichtbarkeit und Einwilligung

Ein Feld ist sichtbar, wenn die Person es freigegeben hat und der Betrachter
die Klassen-/Beziehungspolicy erfüllt. Foto und Biometrie benötigen zusätzlich
die aktuelle, nicht widerrufene Einwilligung aller erforderlichen
Sorgeberechtigten. Ein Widerruf schlägt einen früheren positiven Stand.

### Löschung und Austritt

Der Zugriff endet beim Austritt sofort über Mitgliedschaft und Policy.
`DepartureRetentionCase` steuert die Restaufbewahrung. Kontolöschung läuft
über `AccountDeletionRequest`, Audit und die jeweils dokumentierten Fristen.

## 10. Offene Zielmodellpunkte

- `WebUntisFamilyConnection` und sichere Priorisierung vor Kinder-Fallback.
- Rollen- und Modulrechte als echte Modelle statt pauschaler
  Adapter-/Menüfreigaben.
- fachliche Modulschlüssel und `SchoolModuleSource` je Schule/Klasse.
- UI für Rollenvergabe, individuelle Modulfreigaben und Dashboard-Platzierung.
- einheitliche Quelle für ausgeschriebene Fächer und Lehrernamen;
- zentrale effective-config-Abfrage für Standard, Schule und Klasse;
- Aufbewahrungsfristen je importierter Kategorie;
- Löschung oder nur UI-Ausblendung historischer Mobilitätsdaten;
- endgültige Adapterstatus- und Fehlerwerte;
- endgültige Theme-Tokens unabhängig vom Fachmodell.

Diese Punkte werden vor einer Modellmigration entschieden. Danach folgen
Migration, Datenübernahme, Policy-/Isolations-/Löschtests und erst anschließend
die Anpassung der UI-Abfragen.
