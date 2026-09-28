# Fachliche Modellinventarisierung

Stand: 13.09.2026  
Status: Arbeitsdokument – Ist-Aufnahme, keine automatische Zielmodellentscheidung

## Zentrale Arbeitsgrundlage

Dieses Dokument ist die zentrale laufende Arbeitsgrundlage für die fachliche
Zielstruktur des Datenmodells. Es verbindet die fortlaufenden Modellabschnitte
mit den offenen Punkten, Auslagerungskandidaten, Abhängigkeiten und späteren
Umsetzungsschritten.

Ergänzende verbindliche Quellen bleiben:

- `PROJECT.md` für Ziel und Leitplanken;
- `docs/Architecture.md` für Architektur und Modulgrenzen;
- `docs/DecisionLog.md` für bestätigte Architekturentscheidungen;
- `docs/Roadmap.md` für Reihenfolge und Qualitätsgates.

Dieses Dokument beschreibt zunächst die fachliche Planung. Eine besprochene
Struktur wird erst nach ausdrücklicher Bestätigung als final markiert und erst
danach technisch umgesetzt.

## Offene Punkte und spätere Umsetzungsbausteine

Die folgenden Themen werden zentral gesammelt und erst nach eigener Prüfung
und Abnahme aktiviert:

- Retention- und Bereinigungspolitik je Datenkategorie;
- konfigurierte Bereinigungsläufe für Chats, Adapter-/Sync-Logs,
  Healthchecks, Monitoring und Benachrichtigungen;
- Vorschau, begrenzte Verarbeitungspakete, Auditnachweis und Fehlerbericht je
  Bereinigungslauf;
- Schutz aktiver, rechtlich relevanter oder gesperrter Daten;
- Konsistenzprüfung nach einem Testlauf und vor jeder Automatisierung;
- Backup-/Exportmöglichkeit vor einer tatsächlichen Löschung;
- getrennte Aufbewahrungsregeln für Audit- und Sicherheitsdaten;
- Verwaltungsoberfläche unter `Mehr → Portalverwaltung → Datenpflege`;
- eigenständiges Modul `Einrichtungsassistent` für die geführte Ersteinrichtung;
- verbindliche Modul- und Connector-Dokumentation;
- Modellmigrationen und Datenübernahme erst nach Qualitätsgate.

Ein Bereinigungslauf darf zunächst nur als Vorschau oder ausdrücklich
manueller Testlauf ausgeführt werden. Eine automatische Ausführung wird erst
freigegeben, wenn Umfang, Konsistenz, Wiederherstellung und Abnahmekriterien
dokumentiert und geprüft sind.

## Git-, Teilmodul- und Release-Struktur

Die Umsetzung wird in nachvollziehbaren Teilmodulen und Releases organisiert.
Jeder Umsetzungsschritt verweist auf die betroffenen Modellabschnitte und
die zugehörigen Abnahmekriterien.

```text
Modellentscheidung
→ Teilmodul-Implementierung
→ Migration und Datenübernahme
→ Tests und Sicherheitsprüfung
→ Konsistenz-/Betriebsprüfung
→ dokumentiertes Qualitätsgate
→ Release nächste Version
```

Für jeden Release werden mindestens festgehalten:

- enthaltene Modelle und Relationen;
- geänderte oder neue Modul-/Connector-Funktionen;
- Migrationen und Rückfallmöglichkeit;
- Tests, Sicherheits- und Konsistenzprüfungen;
- offene Restpunkte;
- Abnahmestatus.

Die Git-Historie soll dadurch den fachlichen Aufbau sichtbar machen. Große
unverbundene Umbauten werden vermieden; nicht entschiedene Modelle und
Automatismen bleiben außerhalb des produktiven Releases.

## Neue fachliche Struktur – Besprechungsreihe

Die Zielstruktur wird ab hier ausschließlich fortlaufend dokumentiert:

1. Modell `School`
2. Modell `SchoolClass`
3. Modell `SchoolYear`
4. weitere Modelle nach gemeinsamer Festlegung

Jedes Modell erhält zunächst nur die aktuelle Feld- und Relationsliste. Erst
danach werden fehlende oder zu ändernde Bestandteile gemeinsam besprochen.

## Modell 1: `core.School`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | aktueller Primary Key |
| `source_id` | `CharField` | optional |
| `source_name` | `CharField` | optional |
| `source_imported_at` | `DateTimeField` | optional |
| `name` | `CharField` | Pflichtfeld |
| `search_name` | `CharField` | technisch geführt |
| `short_name` | `CharField` | optional |
| `slug` | `SlugField` | optional |
| `address` | `CharField` | optional |
| `address2` | `CharField` | optional |
| `postal_code` | `CharField` | optional |
| `city` | `CharField` | optional |
| `federal_state` | `CharField` | optional |
| `website` | `URLField` | optional |
| `email` | `EmailField` | optional |
| `school_type` | `CharField` | optional |
| `legal_status` | `CharField` | optional |
| `provider` | `CharField` | optional |
| `fax` | `CharField` | optional |
| `phone` | `CharField` | optional |
| `director` | `CharField` | optional |
| `source_raw` | `JSONField` | optional |
| `latitude` | `DecimalField` | optional |
| `longitude` | `DecimalField` | optional |
| `location_valid` | `BooleanField` | Pflichtfeld |
| `possible_duplicate_group` | `CharField` | optional |
| `logo` | `ImageField` | optional |
| `enabled_features` | `JSONField` | technisch vorhanden |
| `visible_menu_items` | `JSONField` | technisch vorhanden |
| `is_active` | `BooleanField` | Pflichtfeld |
| `created_at` | `DateTimeField` | automatisch |
| `updated_at` | `DateTimeField` | automatisch |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `registrationapplication` | `core.RegistrationApplication` | 1:n |
| `classes` | `core.SchoolClass` | 1:n |
| `branding_assets` | `core.BrandingAsset` | 1:n |
| `portalconfigurationvalue` | `core.PortalConfigurationValue` | 1:n |
| `portalmoduleoverride` | `core.PortalModuleOverride` | 1:n |
| `logorequest` | `core.LogoRequest` | 1:n |
| `roleassignment` | `core.RoleAssignment` | 1:n |
| `timegrid` | `schedule.TimeGrid` | 1:n |
| `portal_adapters` | `portal_adapters.PortalAdapter` | 1:n |

### Noch nicht besprochen

- endgültige Felder;
- Aufteilung von Stammdaten, Branding, Geodaten und Konfiguration;
- endgültiger Primary Key;
- Relation zu einem optionalen Organisations-/Kundenbereich;
- schulbezogene Rollen und Verwaltungsrechte.

### Fachlich festgelegt: Ziel von `School`

`School` wird auf reine schulische Stammdaten reduziert. Konfiguration,
Branding, Adapter, Module, Menüeinträge und Verwaltungsrechte gehören nicht in
dieses Stammdatenmodell.

Der fachliche Zielumfang umfasst voraussichtlich:

- eindeutige Identität;
- offizieller Schulname und optionaler Kurzname;
- Schulart und gegebenenfalls externe Institutionskennung;
- schulische Kontakt- und Adressstammdaten;
- Status `aktiv` oder `inaktiv`;
- technische Erstellungs- und Änderungszeitpunkte.

Importierte Bestandsdaten werden grundsätzlich als `inaktiv` angelegt. Eine
Schule wird erst durch eine ausdrückliche Verwaltungsaktion aktiviert, wenn
ihre Stammdaten geprüft und sie zur Bereitstellung freigegeben wurde. Dafür
muss noch keine Klasse angelegt sein.

Die Aktivierung ist unabhängig davon, ob die Konfiguration durch den
Plattformbetreiber, einen Schul-Administrator oder einen Klassen-Administrator
erfolgt. Fehlende Adapter-, Modul- oder Rechtekonfiguration kann dazu führen,
dass eine Schule weiterhin inaktiv bleibt. Die fachlichen Voraussetzungen für
die Aktivierung werden später als eigene Konfigurations- und Policy-Modelle
definiert und nicht in `School` als JSON-Felder abgelegt.

Eine inaktive Schule darf in öffentlichen oder normalen Nutzeransichten nicht
erscheinen. Sie bleibt für berechtigte Verwaltungsrollen in der
Verwaltungsmaske sichtbar und bearbeitbar.

### Verwaltungsoberfläche

Für `School` wird eine eigene, klar strukturierte Verwaltungsmaske vorgesehen.
Sie muss Stammdaten anzeigen, bearbeiten und den Status ausdrücklich setzen
können. Die konkrete Position, Gestaltung und CSS-Ausarbeitung wird später im
Rahmen des zentralen Designs festgelegt.

Die Maske ist fachlich von den späteren Bereichen getrennt:

```text
Schule – Stammdaten
├── Stammdaten bearbeiten
├── Status: aktiv / inaktiv
├── Konfiguration prüfen
├── Adapter und Module (separater Bereich)
└── Rollen und Rechte (separater Bereich)
```

Die Aktivierung darf keine halbfertige Konfiguration stillschweigend
veröffentlichen. Fehlende Pflichtkonfiguration muss vor der Aktivierung
verständlich angezeigt werden.

## Modell 2: `core.SchoolClass`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `school` | `ForeignKey` | Pflichtfeld, Ziel `core.School` |
| `name` | `CharField` | Pflichtfeld |
| `code` | `CharField` | optional |
| `school_year` | `ForeignKey` | Pflichtfeld, Ziel `core.SchoolYear` |
| `display_name` | `CharField` | optional |
| `logo` | `ImageField` | optional |
| `enabled_features` | `JSONField` | technisch vorhanden |
| `visible_menu_items` | `JSONField` | technisch vorhanden |
| `grade_level` | `CharField` | optional |
| `status` | `CharField` | Pflichtfeld |
| `valid_from` | `DateField` | optional |
| `valid_until` | `DateField` | optional |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `school` | `core.School` | n:1 |
| `school_year` | `core.SchoolYear` | n:1 |
| `familyphoto` | `core.FamilyPhoto` | 1:n |
| `childjoinrequest` | `core.ChildJoinRequest` | 1:n |
| `registrationapplication` | `core.RegistrationApplication` | 1:n |
| `domain` | `core.ClassDomain` | 1:1 |
| `branding_assets` | `core.BrandingAsset` | 1:n |
| `portalconfigurationvalue` | `core.PortalConfigurationValue` | 1:n |
| `portalmoduleoverride` | `core.PortalModuleOverride` | 1:n |
| `logorequest` | `core.LogoRequest` | 1:n |
| `classmembership` | `core.ClassMembership` | 1:n |
| `roleassignment` | `core.RoleAssignment` | 1:n |
| `invitation` | `core.Invitation` | 1:n |
| `familyaccesscode` | `core.FamilyAccessCode` | 1:n |
| `departureretentioncase` | `core.DepartureRetentionCase` | 1:n |
| `usernotification` | `core.UserNotification` | 1:n |
| `pilotreport` | `core.PilotReport` | 1:n |
| `protecteddocument` | `content.ProtectedDocument` | 1:n |
| `teacherprofile` | `content.TeacherProfile` | 1:n |
| `post` | `content.Post` | 1:n |
| `event` | `events.Event` | 1:n |
| `eventpoll` | `events.EventPoll` | 1:n |
| `mobilitylisting` | `mobility.MobilityListing` | 1:n |
| `gallery` | `media.Gallery` | 1:n |
| `biometriccollection` | `biometrics.BiometricCollection` | 1:1 |
| `chatroom` | `chat.ChatRoom` | 1:n |
| `directconversation` | `chat.DirectConversation` | 1:n |
| `timetableentry` | `schedule.TimetableEntry` | 1:n |
| `calendarentry` | `schedule.CalendarEntry` | 1:n |
| `icalsubscription` | `schedule.ICalSubscription` | 1:n |
| `available_portal_adapter_modules` | `portal_adapters.PortalAdapterModule` | n:m |

### Vorschlag für das Zielmodell

`SchoolClass` beschreibt eine konkrete Klasse innerhalb einer Schule und eines
Schuljahres. Es ist kein Sammelmodell für Konfiguration oder alle Funktionen
des Portals.

| Zielfeld | Vorgeschlagener Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` oder bestehender `BigAutoField` | eindeutige Identität; UUID ist für spätere Importe und externe Referenzen zu prüfen |
| `school` | `ForeignKey` → `School` | genau eine zugehörige Schule |
| `school_year` | `ForeignKey` → `SchoolYear` | genau ein schulischer Gültigkeitskontext |
| `name` | `CharField` | fachliche Bezeichnung, zum Beispiel `5e` oder `5.1` |
| `code` | `CharField` | technischer oder externer Schlüssel, sofern die Quelle einen benötigt |
| `grade_level` | `PositiveSmallIntegerField` | Jahrgang, zum Beispiel `5`; optional bei Sonder-/Kursklassen |
| `status` | `choices` über `CharField` | `inaktiv`, `aktiv`, `archiviert` |
| `valid_from` | `DateField` | optionaler Beginn der Nutzung |
| `valid_until` | `DateField` | optionales Ende der Nutzung |
| `created_at` | `DateTimeField` | automatische Erstellung |
| `updated_at` | `DateTimeField` | automatische Änderung |

Der sichtbare Klassenname soll grundsätzlich aus dem fachlichen Namen kommen.
Ein zusammengesetzter Text wie `THG · 5e` gehört in die Darstellung oder wird
aus Schule und Klasse gebildet, nicht als zusätzliche redundante Wahrheit im
Modell gespeichert.

### Beziehungen im Zielbild

Direkte Kernbeziehungen:

```text
SchoolClass
├── gehört zu genau einer School
├── gehört zu genau einem SchoolYear
├── hat viele ClassMemberships
└── kann viele scoped Rollen, Einladungen und fachliche Zuordnungen besitzen
```

Funktionen wie Kalender, Chat, Beiträge, Adapter, Modulfreigaben und
Benachrichtigungen werden fachlich auf den Klassenscope bezogen, aber nicht
als JSON- oder Menüfelder in `SchoolClass` gespeichert. Die jeweils
verantwortlichen Modelle erhalten dafür eine eindeutige Klassenrelation oder
eine klar definierte Scope-Zuweisung.

### Aus `SchoolClass` herauszulösende Bestandteile

`logo`, `enabled_features` und `visible_menu_items` werden in die zentrale
Auslagerungsliste aufgenommen. Das Logo gehört zum Branding; Funktionen und
Menüs gehören zur Modul- bzw. Policy-Konfiguration.

Die bestehenden vielen Rückrelationen sind nicht automatisch falsch. Sie
werden später pro Fachmodul darauf geprüft, ob sie direkt auf `SchoolClass`
zeigen müssen oder über eine gemeinsame Scope-/Policy-Schnittstelle geführt
werden sollten.

### Vorschlag: Zuordnung von Klassenlehrkräften

Die Zuständigkeit wird nicht als einzelnes Feld `teacher` an `SchoolClass`
gespeichert. Eine Lehrkraft kann mehrere Klassen betreuen und eine Klasse kann
mehrere verantwortliche Lehrkräfte haben. Dafür wird ein eigenes
Zuordnungsmodell vorgesehen, zum Beispiel `ClassTeacherAssignment`.

| Feld | Vorgeschlagener Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` oder bestehender Standard | Primary Key |
| `school_class` | `ForeignKey` → `SchoolClass` | konkrete Klasse |
| `teacher` | `ForeignKey` → `Person` oder `TeacherProfile` | zugeordnete Lehrkraft |
| `role` | `CharField` mit Auswahl | Klassenlehrer, stellvertretender Klassenlehrer, Vertretung |
| `is_primary` | `BooleanField` | Hauptzuständigkeit, sofern benötigt |
| `valid_from` | `DateField` | Beginn der Zuordnung |
| `valid_until` | `DateField` | Ende der Zuordnung |
| `status` | `CharField` mit Auswahl | Entwurf, aktiv, beendet |
| `created_at` / `updated_at` | `DateTimeField` | technische Zeitpunkte |

Damit bleiben Lehrkraft und Klassenmodell unabhängig. Vertretungen können
zeitlich begrenzt angelegt werden, mehrere Klassenlehrer sind möglich und die
Historie früherer Zuständigkeiten bleibt erhalten. Die konkrete Ausgestaltung
von `TeacherProfile` und schulübergreifenden Lehrertätigkeiten wird weiterhin
später entschieden.

Beim Schuljahreswechsel wird die Lehrerzuordnung nicht auf der alten Klasse
weitergeführt. Stattdessen wird die neue `SchoolClass` mit eigener ID angelegt
und eine neue `ClassTeacherAssignment` auf diese neue Klassen-ID erstellt.
Eine bisherige Zuordnung bleibt mit ihrer alten Klassen-ID und ihrem
Gültigkeitsende erhalten. Die Übernahme kann als Vorschlag vorbereitet,
bleibt aber vor der Aktivierung bestätigungspflichtig.

## Modell 3: `core.SchoolYear`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `label` | `CharField` | Pflichtfeld, z. B. `2026/27` |
| `starts_on` | `DateField` | Pflichtfeld |
| `ends_on` | `DateField` | Pflichtfeld |
| `is_active` | `BooleanField` | Pflichtfeld |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `schoolclass` | `core.SchoolClass` | 1:n |
| `protecteddocument` | `content.ProtectedDocument` | 1:n |
| `post` | `content.Post` | 1:n |
| `event` | `events.Event` | 1:n |
| `gallery` | `media.Gallery` | 1:n |
| `chatroom` | `chat.ChatRoom` | 1:n |
| `timetableentry` | `schedule.TimetableEntry` | 1:n |
| `calendarentry` | `schedule.CalendarEntry` | 1:n |

### Erste Empfehlung zur Länderabhängigkeit

`SchoolYear` bleibt unabhängig von einer einzelnen Schule, erhält aber eine
Relation zu einem standardisierten Bundesland-/Regionenmodell. Der gleiche
Schuljahresabschnitt kann dadurch von allen Schulen desselben Bundeslandes
geteilt werden.

```text
FederalState: Niedersachsen
└── SchoolYear: 2026/27
    ├── starts_on
    ├── ends_on
    └── viele Schulen und Klassen
```

Für ein anderes Bundesland kann derselbe Anzeigename `2026/27` mit einem
anderen Zeitraum existieren:

```text
Niedersachsen + 2026/27 → Zeitraum A
Bayern        + 2026/27 → Zeitraum B
```

Meine Empfehlung ist daher:

- eigenes Referenzmodell `FederalState` statt freiem Text;
- `SchoolYear.federal_state` als `ForeignKey` auf dieses Modell;
- eindeutige Kombination aus `federal_state` und `label`;
- Schulen erhalten weiterhin eine eigene Bundesland-Zuordnung;
- eine Schule verweist auf das passende `SchoolYear`, nicht auf ein neu
  angelegtes Schuljahr pro Schule;
- Klassen übernehmen das Schuljahr über ihre `SchoolClass`-Relation;
- Beginn und Ende werden am landesbezogenen `SchoolYear` gespeichert;
- Sommerferien und einzelne Ferientermine werden später als eigenes
  Ferien-/Kalendermodell geprüft, nicht als zusätzliche Felder im Schuljahr.

Damit bleiben historische Schuljahre eindeutig und mehrere Schulen können
denselben landesbezogenen Jahresdatensatz verwenden.

## Modell 4: `FederalState` (noch nicht vorhanden)

### Aktueller Ist-Zustand

Ein eigenes Django-Modell `FederalState` ist aktuell nicht registriert. Das
Bundesland wird derzeit als freies Textfeld geführt:

| Ursprungsmodell | Feld | Django-Typ | Aktuelle Wirkung |
|---|---|---|---|
| `core.School` | `federal_state` | `CharField` | speichert die Bundeslandbezeichnung als Text |

Eine aktuelle Relation zu einem standardisierten Bundeslandmodell besteht
nicht.

### Erste Empfehlung

Ein eigenes Referenzmodell `FederalState` sollte angelegt werden, damit
Schule und Schuljahr dieselbe standardisierte Zuordnung verwenden können.

| Feld | Vorgeschlagener Django-Typ | Zweck |
|---|---|---|
| `id` | `BigAutoField` oder `UUIDField` | Primary Key |
| `country_code` | `CharField` | zum Beispiel `DE` |
| `code` | `CharField` | standardisierter Schlüssel, zum Beispiel `NI` |
| `name` | `CharField` | zum Beispiel `Niedersachsen` |
| `is_active` | `BooleanField` | Referenzwert verwendbar oder archiviert |
| `created_at` / `updated_at` | `DateTimeField` | technische Zeitpunkte |

### Vorgesehene Relationen

```text
FederalState
├── viele Schools
└── viele SchoolYears
```

Die konkrete Entscheidung über Länder, Regionen außerhalb Deutschlands und
die endgültige Schlüsselstruktur wird später gemeinsam festgelegt. Das
bestehende Textfeld `School.federal_state` wird dafür zunächst nur als
Auslagerungskandidat vorgemerkt.

## Modell 5: `core.ClassMembership`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `school_class` | `ForeignKey` | Pflichtfeld → `core.SchoolClass` |
| `person` | `ForeignKey` | Pflichtfeld → `core.Person` |
| `status` | `CharField` | Pflichtfeld |
| `valid_from` | `DateField` | Pflichtfeld |
| `valid_until` | `DateField` | optional |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `school_class` | `core.SchoolClass` | n:1 |
| `person` | `core.Person` | n:1 |

Weitere Rückrelationen sind am aktuellen Django-Modell nicht registriert.

### Erste Empfehlung

`ClassMembership` sollte als eigenständige zeitlich gültige Zugehörigkeit
beibehalten werden. Sie verbindet eine Person mit einer konkreten
`SchoolClass`; beim Schuljahreswechsel wird eine neue Mitgliedschaft zur neuen
Klassen-ID angelegt. Die alte Mitgliedschaft endet und bleibt historisch
erhalten.

Die Mitgliedschaft sollte die Teilnahme an einer Klasse abbilden, nicht die
Rolle der Person. Schülerzugehörigkeit, Lehrkraft, Klassen-Admin und
Erziehungsberechtigung werden über getrennte Rollen- bzw. Beziehungsmodelle
geführt. Zu prüfen sind noch kontrollierte Statuswerte, eine Eindeutigkeitsregel
für überlappende Zeiträume sowie die Frage, ob das Modell künftig nur für
Schüler oder allgemein für teilnehmende Personen gilt.

### Datums- und Verwaltungsregel

`valid_from` und `valid_until` werden bei einer neuen Zuordnung automatisch aus
der Gültigkeit von `SchoolClass` vorbelegt. Sie müssen im Normalfall nicht
separat gepflegt werden.

Individuelle Abweichungen bleiben möglich:

```text
Klasse gültig:       01.08.2026 – 31.07.2027
Kind tritt später ein: 15.08.2026 – 31.07.2027
Kind scheidet früher aus: 01.08.2026 – 30.04.2027
```

Die tatsächlichen Mitgliedschaftsdaten werden für Historie und Berechtigungs-
prüfung in `ClassMembership` gespeichert. Eine spätere Änderung der
Klassen-Gültigkeit darf bereits abgeschlossene individuelle Mitgliedschaften
nicht unbemerkt verändern.

Für berechtigte Verwaltungsrollen wird eine eigene Übersicht
„Schul- und Klassenzugehörigkeiten“ vorgesehen. Dort können Personen bzw.
Kinder einer Klasse zugeordnet, Zuordnungen beendet und Wechsel in eine
andere Klasse nachvollziehbar durchgeführt werden. Eine Beendigung setzt ein
Enddatum und den Status beendet; der historische Datensatz wird nicht
gelöscht. Ein Klassenwechsel beendet die alte Mitgliedschaft und legt eine
neue Mitgliedschaft mit den neuen Klassendaten an.

## Modell 6: `core.Person`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `user` | `OneToOneField` | optional → `core.UserAccount` |
| `first_name` | `CharField` | Pflichtfeld |
| `last_name` | `CharField` | Pflichtfeld |
| `gender` | `CharField` | optional |
| `birth_date` | `DateField` | optional |
| `phone` | `CharField` | optional |
| `other_contact` | `CharField` | optional |
| `street` | `CharField` | optional |
| `postal_code` | `CharField` | optional |
| `city` | `CharField` | optional |
| `home_latitude` / `home_longitude` | `DecimalField` | optional |
| `chat_display_name` | `CharField` | optional |
| `contribution_name_mode` | `CharField` | Pflichtfeld |
| `profile_photo` | `ImageField` | optional |
| `profile_image_mode` | `CharField` | Pflichtfeld technisch |
| `avatar_key` | `CharField` | Pflichtfeld technisch |
| `avatar_seed` | `CharField` | optional |
| `contact_email` | `EmailField` | optional |
| `field_visibility` | `JSONField` | technisch vorhanden |
| `email_visibility` | `CharField` | Pflichtfeld technisch |
| `phone_visibility` | `CharField` | Pflichtfeld technisch |
| `relationship_visibility` | `CharField` | Pflichtfeld technisch |
| `created_at` | `DateTimeField` | automatisch |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `user` | `core.UserAccount` | 1:1 |
| `households` | `core.Household` | n:m |
| `studentprofile` | `core.StudentProfile` | 1:1 |
| `classmembership` | `core.ClassMembership` | 1:n |
| `guardian_relationships` / `student_relationships` | `core.GuardianChildRelationship` | 1:n |
| `teacherprofile` | `content.TeacherProfile` | 1:n |
| `consents_about` / `consent_decisions` | `core.ConsentDecision` | 1:n |
| `webuntis_connections` | `webuntis.WebUntisConnection` | 1:n |
| `module_connections` | `portal_adapters.ChildModuleConnection` | 1:n |
| `schoolmanager_connections` | `portal_adapters.SchoolmanagerConnection` | 1:n |
| `family_photos` | `core.FamilyPhoto` | n:m |
| `photosubjectdeclaration` | `media.PhotoSubjectDeclaration` | 1:n |
| `absencedraft` / `absencesubmission` | WebUntis-Abwesenheitsmodelle | 1:n |
| `homework_progress` | `webuntis.HomeworkProgress` | 1:n |

### Erste Empfehlung

`Person` sollte die neutrale Identität eines Menschen bleiben. Konto,
Familienzugehörigkeit, Schülerstatus, Lehrerfunktion und Berechtigungen werden
über eigene Relationen und Profile angebunden.

`Person` enthält neben der Grundidentität auch die persönlichen Stammdaten.
Dazu gehören zunächst `first_name`, `last_name`, gegebenenfalls `gender` und
`birth_date` sowie Straße, Postleitzahl, Ort, Telefonnummer und eine
Kontakt-E-Mail. Diese Daten werden in der persönlichen Profilverwaltung
gepflegt und bleiben zunächst im Modell `Person`.

Davon getrennt zu prüfen sind Geokoordinaten, Foto-/Avatarverwaltung und die
technische Sichtbarkeitskonfiguration. Diese Bereiche kommen als mögliche
Auslagerungskandidaten in die zentrale Liste. Die Login-E-Mail des
`UserAccount` bleibt von einer zusätzlichen Kontakt-E-Mail der Person
unterschieden, sofern beide fachlich benötigt werden.

### Fachlich bestätigt

`chat_display_name` und `contribution_name_mode` werden nicht in die
Zielstruktur übernommen. Stattdessen wird eine gemeinsame Auswahl
`display_name_mode` vorgesehen:

```text
first_name | last_name | full_name
```

Diese Auswahl gilt portalweit für die erlaubten Namensdarstellungen und
verhindert frei erfundene Anzeigenamen ohne Personenbezug.

Eine Person darf sowohl ein Profilfoto als auch einen Avatar hinterlegen. Die
beiden Darstellungen werden getrennt gespeichert und können jederzeit
gewechselt werden, ohne die jeweils andere Darstellung zu löschen. Dafür wird
ein eigener `ProfileVisual`-Bereich mit aktivem Modus vorgesehen:

```text
ProfileVisual
├── active_mode: photo | avatar
├── ProfilePhoto
└── AvatarSelection
```

Beim Öffnen des Profils wird immer die aktive Darstellung angezeigt. Die
konkreten Felder von `ProfilePhoto` und `AvatarSelection` werden in einem
späteren eigenen Modellabschnitt besprochen.

## Modell 7: `core.UserAccount`

### Fachlich bestätigt

`UserAccount` bleibt das Anmelde- und Sicherheitskonto. Die Login-E-Mail wird
nicht in `Person` dupliziert. Eine bestätigte E-Mail-Änderung aktualisiert
`UserAccount.email` und wird dort zur neuen Login- und
Passwort-zurücksetzen-Adresse.

`first_name` und `last_name` werden nicht als Kontostammdaten weitergeführt,
sondern gehören zu `Person`. Die Leak-Prüfung wird als eigenes
Sicherheitsmodell vorgesehen. `is_superuser` und `is_staff` bleiben zunächst
als technische Django-Felder bestehen und werden später mit dem Scope-
Rollenmodell abgeglichen. 2FA ist für normale Nutzer optional.

Tarife und Modulrechte werden nicht im Benutzerkonto gespeichert. Alle
Module/Funktionen erhalten von Anfang an eine stabile eindeutige Kennung. Die
Tarifmatrix wird separat über `Plan`, `PlanModuleEntitlement` und
`PlanAssignment` geführt. Für den aktuellen Betrieb wird jedes Modul zunächst
dem Tarif `Free` zugeordnet; `Pro` und `Premium` bleiben vorbereitete spätere
Tarife.

## Modell 8: `core.Household`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `label` | `CharField` | Pflichtfeld |
| `members` | `ManyToManyField` | Pflichtrelation → `core.Person` |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `members` | `core.Person` | n:m |
| `photos` | `core.FamilyPhoto` | 1:n |
| `invitation` | `core.Invitation` | 1:n |
| `familyregistrationrequest` | `core.FamilyRegistrationRequest` | 1:1 |

### Erste Empfehlung

`Household` sollte den privaten Familien-/Haushaltskontext abbilden. Das
`label` darf nur eine interne oder frei gewählte Bezeichnung sein und keine
Berechtigung oder rechtliche Familienidentität ersetzen.

Die direkte Many-to-Many-Relation `members` ist für das Zielmodell zu
ungenau, weil sie nicht festhält, ob eine Person erwachsen, Kind,
Erziehungsberechtigte oder weitere berechtigte Person ist. Sie sollte durch
eine eigene zeitlich gültige Zuordnung mit Rolle und gegebenenfalls konkreten
Kindrechten ersetzt oder ergänzt werden. Ein Haushalt allein darf niemals
automatisch Zugriff auf alle Kinder oder Module geben.

Die konkrete Zuordnung `HouseholdMembership` beziehungsweise die Verbindung
zwischen Erwachsenen und einzelnen Kindern wird im nächsten Familienmodell
detailliert besprochen.

## Modell 9: `core.StudentProfile`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `person` | `OneToOneField` | Pflichtfeld → `core.Person` |
| `profile_photo_reference` | `CharField` | optional |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `person` | `core.Person` | 1:1 |
| `biometricprofile` | `biometrics.BiometricProfile` | 1:n |
| `itslearningconnection` | `itslearning.ItslearningConnection` | 1:1 |
| `webdavspace` | `itslearning.WebDavSpace` | 1:1 |

### Erste Empfehlung

`StudentProfile` sollte als Ergänzung zu `Person` bestehen bleiben und nur
kindbezogene oder schülerspezifische Angaben aufnehmen. Name, Geburtsdatum,
Adresse und Kontaktstammdaten bleiben in `Person`; die Klassenzugehörigkeit
bleibt in `ClassMembership`.

`profile_photo_reference` ist als technischer Einzelverweis zu prüfen, weil
die allgemeine Profilbildlogik bereits über `ProfileVisual`, `ProfilePhoto`
und `AvatarSelection` vorgesehen ist. Schulportalzugänge und biometrische
Daten bleiben separate Relationen und dürfen nicht in das Schülerprofil
eingebettet werden.

### Fachlich festgelegt

Ein leeres `StudentProfile` wird nicht als notwendiges Zielmodell
weitergeführt. Die Schülerrolle ergibt sich zunächst aus `Person`,
`ClassMembership`, den geprüften Familienbeziehungen und den jeweiligen
kindbezogenen Modul-/Adapterverbindungen. `profile_photo_reference` wird nicht
übernommen und gegen den separaten Profilbildbereich ersetzt.

Schülerspezifische Leistungsdaten werden als eigener optionaler Modellbereich
vorgesehen.

## Modell 10: `StudentAssessment` / Leistungsdaten (noch nicht vorhanden)

### Aktueller Ist-Zustand

Ein Modell für Tests, Klausuren, Zeugnisse oder Zensuren ist aktuell nicht
registriert. Die Daten werden derzeit nicht als eigener fachlicher Bestand
geführt.

### Erste Empfehlung

Leistungsdaten werden unabhängig von `Person`, `ClassMembership` und
`StudentProfile` als eigener optionaler Modellbereich geführt. Der Datensatz
verweist auf die Person des Schülers und den damaligen Schul-/Klassen- und
Schuljahreskontext, damit auch historische Verläufe korrekt bleiben.

Vorgesehene fachliche Inhalte sind zunächst:

- Schüler/Person;
- Fach;
- Art: Test, Klausur, Halbjahreszeugnis oder Jahreszeugnis;
- Bezeichnung und Datum;
- Note oder Ergebnis, einschließlich nicht numerischer Werte;
- Schuljahr und gegebenenfalls Klasse;
- Quelle: manuell, importiert oder korrigiert;
- erfasst durch, erstellt/geändert und Sichtbarkeit.

Die Detailmodelle für Fächer, einzelne Prüfungen, Zeugnisse, Notenwerte,
Importquellen und Rollenrechte werden später separat besprochen. Eltern oder
Schüler können Daten – abhängig von Rolle und Freigabe – manuell erfassen;
Adapterdaten können zusätzlich importiert werden. Die Funktion bleibt
optional und darf ohne Leistungsdaten keinen Fehler im übrigen Portal
verursachen.

Leistungsdaten können künftig aus unterstützten Schuladaptern wie WebUntis
oder itslearning übernommen werden. Jeder Import benötigt eine externe Quelle,
eine stabile externe ID beziehungsweise einen Fingerprint, den Quellzeitpunkt
und einen nachvollziehbaren Importstatus. Wiederholte Abfragen müssen den
vorhandenen Datensatz aktualisieren oder unverändert lassen und dürfen keine
Dubletten erzeugen. Manuelle Einträge bleiben als eigene Quelle erkennbar und
dürfen nicht blind durch spätere Adapterimporte überschrieben werden.

## Modell 11: `Subject` / Fach (noch nicht vorhanden)

### Aktueller Ist-Zustand

Ein zentrales Fachmodell ist aktuell nicht registriert. Fächer werden derzeit
über fachmodul- oder adapterbezogene Felder und das Modell
`webuntis.WebUntisSubjectMapping` abgebildet.

### Erste Empfehlung

Für Leistungsdaten, Stundenplan und Hausaufgaben sollte ein neutrales
Fachmodell vorgesehen werden. Adapter liefern externe Fachcodes und Namen;
die Anwendung ordnet diese einem zentralen `Subject` zu.

Vorgesehene fachliche Inhalte sind zunächst:

- eindeutige Identität;
- standardisierter Fachname;
- optionales Kürzel;
- optionaler Fachbereich;
- Status aktiv/inaktiv;
- externe Fachzuordnungen je Adapter und Schule;
- Anzeige- und Sortierreihenfolge.

Die konkrete Frage, ob ein Fach global, schulbezogen oder klassenbezogen
geführt wird, sowie die Felder und Relationen von
`WebUntisSubjectMapping` werden im nächsten Schritt geprüft.

### Fachlich bestätigt: adapterneutrale Fachübersetzung

`webuntis.WebUntisSubjectMapping` wird fachlich als adapterneutrale
`ExternalSubjectMapping` weitergeführt. Die Tabelle übersetzt externe
Fachcodes und Bezeichnungen in das zentrale `Subject`-Modell.

Die Zuordnung kann optional auf ein `PortalModule` eingeschränkt werden. Eine
leere Modulzuordnung gilt als allgemeine Standardübersetzung des Adapters. Bei
der Auflösung gewinnt die spezifischste Zuordnung; wenn keine Zuordnung
existiert, wird der ungeprüfte Originalwert angezeigt.

So können beispielsweise `ENG` im Kalender und `EN` im Stundenplan auf das
zentrale Fach `Englisch` zeigen. Die Tabelle bleibt unabhängig vom Namen des
jeweiligen Adapters und kann von WebUntis, itslearning, Schulmanager oder
anderen Quellen verwendet werden.

### Fachlich bestätigt: Curriculum-Zuordnung

Curriculum-Daten werden später eindeutig nach Bundesland, Schulart,
Schulstufe, Fach und Jahrgangsbereich zugeordnet. Die Klassenstufe kommt aus
dem Klassenkontext; die Schulart aus der Schule beziehungsweise dem
Curriculum-Dokument.

Ein Curriculum-Dokument benötigt neben der Quelle und dem PDF einen
Qualitäts-/Veröffentlichungsstatus. Nur geprüfte Inhalte werden strukturiert
im Portal angezeigt. Wenn die Extraktion oder Qualitätsprüfung nicht
ausreicht, bleibt der offizielle PDF-Verweis als sichere Fallback-Anzeige
verfügbar.

```text
FederalState
└── CurriculumDocument
    ├── SchoolType / SchoolLevel
    ├── Subject
    ├── GradeRange
    ├── source_pdf / source_url
    └── review_status: importiert | geprüft | veröffentlicht
```

## Modell 13: `webuntis.WebUntisTeacherMapping`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `adapter` | `ForeignKey` | optional → `portal_adapters.PortalAdapter` |
| `code` | `CharField` | Pflichtfeld |
| `label` | `CharField` | Pflichtfeld |
| `updated_at` | `DateTimeField` | automatisch |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `adapter` | `portal_adapters.PortalAdapter` | n:1 |

Weitere Relationen bestehen aktuell nicht.

### Erste Empfehlung

Das Modell sollte analog zur Fachübersetzung adapterneutral als
`ExternalTeacherMapping` geführt werden. Es übersetzt externe Lehrercodes und
Namen in eine einheitliche Anzeige. Eine optionale Modulzuordnung sollte
ermöglichen, dass derselbe externe Code je nach Kalender, Stundenplan oder
anderem Modul unterschiedlich gepflegt wird.

Ein eigenes zentrales `Teacher`-Modell wird dadurch nicht vorweggenommen. Die
Übersetzung dient zunächst nur der Anzeige; eine echte Zuordnung zu einer
Person oder einem späteren `TeacherProfile` darf erst nach geprüfter
Identifikation erfolgen.

### Verwaltungsstruktur für Übersetzungen

Für `ExternalSubjectMapping` und `ExternalTeacherMapping` wird eine gemeinsame
Verwaltungsmaske vorgesehen. Die Verwaltung kann nach Schule, Klasse, Adapter
und optionalem Modul gefiltert werden und erlaubt das nachträgliche Ergänzen
oder Korrigieren neuer Codes, Kürzel und Namen.

```text
Schule
└── Klasse (optional)
    └── Adapter
        ├── Fachübersetzungen
        └── Lehrerübersetzungen
            └── optional je PortalModule
```

Neue oder unbekannte externe Werte dürfen zunächst als ungeprüft angezeigt
werden. Eine berechtigte Verwaltungsrolle kann sie anschließend zuordnen,
aktivieren, ändern oder deaktivieren. Änderungen werden mit Änderer und
Zeitpunkt nachvollziehbar protokolliert; geprüfte manuelle Zuordnungen dürfen
nicht durch einen normalen automatischen Import überschrieben werden.

## Modell 14: `portal_adapters.PortalAdapter`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `school` | `ForeignKey` | Pflichtfeld → `core.School` |
| `provider` | `CharField` | Pflichtfeld |
| `name` | `CharField` | Pflichtfeld |
| `base_url` | `URLField` | optional |
| `project_identifier` | `CharField` | optional |
| `institution_identifier` | `CharField` | optional |
| `school_number` | `CharField` | optional |
| `configuration_note` | `TextField` | optional |
| `is_enabled` | `BooleanField` | Pflichtfeld |
| `requires_child_credentials` | `BooleanField` | Pflichtfeld |
| `last_checked_at` | `DateTimeField` | optional |
| `last_check_status` | `CharField` | optional |
| `last_check_message` | `CharField` | optional |
| `created_at` / `updated_at` | `DateTimeField` | automatisch |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `school` | `core.School` | n:1 |
| `modules` | `portal_adapters.PortalAdapterModule` | 1:n |
| `webuntis_connections` | `webuntis.WebUntisConnection` | 1:n |
| `webuntis_subject_mappings` | Fach-Mapping-Bestand | 1:n |
| `webuntis_teacher_mappings` | Lehrer-Mapping-Bestand | 1:n |

### Erste Empfehlung

`PortalAdapter` ist aktuell an eine Schule gebunden und mischt damit
Adapterbeschreibung, Schulzuordnung, Aktivierung und Prüfstatus. Zu prüfen ist
eine spätere Trennung in eine allgemeine `AdapterDefinition` und eine
konkrete `SchoolAdapterAssignment`. Die Übersetzungsverwaltung kann dann den
Adapter zentral beschreiben und die Zuordnung je Schule, Klasse und Modul
pflegen, ohne allgemeine Daten zu duplizieren.

### Fachlich bestätigt: globale Modulbereitstellung

Adapter und Module können auch global bereitgestellt werden. Eine Schule oder
Klasse muss in diesem Fall nicht jeweils eine eigene Kopie oder Konfiguration
des Moduls anlegen.

Die Gültigkeit wird daher getrennt geführt:

```text
globaler Adapter / globales Modul
→ optionaler Filter: Land, Schulart, Schulstufe, Jahrgang, Fach
→ passende Anzeige für alle berechtigten Nutzer
```

Eine konkrete Schul- oder Klassenzuordnung bleibt möglich, wenn ein Adapter
oder Modul individuelle Zugangsdaten, Freigaben oder Einstellungen benötigt.
Die Auflösung folgt dabei der Spezifität:

```text
Klasse → Schule → global
```

Damit kann eine Lernplattform global verfügbar sein und trotzdem nur Inhalte
für `Gymnasium`, `Sekundarstufe I` oder Jahrgang `6` anzeigen. Die Filterung
ist keine Berechtigung; Rollen- und Datenschutzprüfungen bleiben zusätzlich
erforderlich.

## Modell 15: `PortalModule`

### Fachlich bestätigt

`PortalModule` ist die vollständig unabhängige Definition einer Portal-
Funktion. Das Modell enthält keine Schule, Klasse, Bundesland, Schulart oder
Adapterzuordnung.

Vorgesehen sind eine stabile eindeutige ID, technischer Schlüssel,
Bezeichnung, Beschreibung, Icon, Status und optionale Abhängigkeiten. Alle
Module werden zunächst dem Tarif `Free` zugeordnet; Tarifgrenzen werden
außerhalb des Modells gepflegt.

## Modell 16: `SchoolModuleSource` (noch nicht vorhanden)

### Aktueller Ist-Zustand

Ein eigenständiges Modell für die Zuordnung „fachliches Modul zu konkreter
Quelle je Schule oder Klasse“ ist aktuell nicht registriert. Diese Aufgabe ist
derzeit auf Adapter- und Adaptermodulmodelle verteilt.

### Erste Empfehlung

`SchoolModuleSource` soll festlegen, ob und über welchen Adapter eine Schule
oder Klasse ein bestimmtes Modul bezieht.

Vorgesehene Inhalte sind zunächst:

- Schule oder optional konkrete Klasse;
- `PortalModule`;
- konkrete Adapterzuordnung und technisches Adaptermodul;
- Priorität und Fallback;
- Status aktiv/inaktiv;
- Gültigkeitszeitraum;
- Prüfstatus und letzte erfolgreiche Prüfung.

Das Modul selbst bleibt überall identisch. Curriculum- und Inhaltsfilter wie
Bundesland, Schulart, Schulstufe und Jahrgang gehören nicht in `PortalModule`,
sondern in die jeweiligen Inhalte oder Curriculum-Dokumente.

## Modell 17: `portal_adapters.StudentModuleConnection`

### Vorhandene Felder

| Feld | Django-Typ | Aktueller Zustand |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `student` | `ForeignKey` | Pflichtfeld → `core.Person` |
| `module` | `ForeignKey` | Pflichtfeld → `portal_adapters.PortalAdapterModule` |
| `is_enabled` | `BooleanField` | Pflichtfeld |
| `connection_state` | `CharField` | Pflichtfeld |
| `configured_by` | `ForeignKey` | optional → `core.UserAccount` |
| `configured_at` | `DateTimeField` | automatisch |

### Aktuelle Relationen

| Relation | Zielmodell | Kardinalität |
|---|---|---|
| `student` | `core.Person` | n:1 |
| `module` | `portal_adapters.PortalAdapterModule` | n:1 |
| `configured_by` | `core.UserAccount` | n:1, optional |

Weitere Relationen bestehen aktuell nicht.

### Erste Empfehlung

Das Modell beschreibt eine konkrete technische Einrichtung für ein Kind und
ist damit von der allgemeinen Moduldefinition zu trennen. Im Zielbild sollte
die Verbindung auf `PortalModule` und optional auf `SchoolModuleSource`
verweisen. `is_enabled` (fachlich gewünscht) und `connection_state` (technisch
gesund/eingerichtet/gestört) bleiben getrennte Aussagen.

Zu prüfen sind außerdem Schul-/Klassenkontext, Status- und Prüfzeitpunkte,
Fallback-Quelle sowie die Abgrenzung zu Familienverbindungen. Eine aktivierte
Verbindung darf niemals fehlende Rollen- oder Modulrechte ersetzen.

### Fachlich bestätigt

Wenn eine neue Person beziehungsweise ein Kind einer Klasse beitritt, werden
die für Schule und Klasse konfigurierten Modulverbindungen automatisch als
Einrichtungsentwürfe angelegt. Der Nutzer muss nicht selbst Adapter und
Module zusammensuchen. Er entscheidet anschließend nur noch über
Freischalten oder Nicht-Freischalten.

Beim Freischalten wird der erforderliche Zugangsscope geprüft:

```text
child | household | school | shared
```

Fehlende Zugangsdaten oder unvollständige Konfiguration verhindern die
Aktivierung und werden verständlich angezeigt. Ein schulweiter Abruf mit Daten
für viele Klassen wird nach dem Import auf Schule, Schuljahr, Klasse, Kind und
Modul gefiltert; die vollständige Rohdatenliste wird keinem Nutzer angezeigt.

Der Erstlogin erhält einen geführten Einrichtungsmodus. Dieser führt
interaktiv durch Familie, Kinder, Schule/Klasse, vorhandene Adapter,
Zugangsdaten und Modulfreigaben. Der Ablauf findet in einer zentralen
Einrichtungsmaske statt; innerhalb dieser Maske wird jeweils nur die nächste
notwendige Kachel beziehungsweise Dateneingabe angezeigt. Dadurch entsteht
kein Wust aus parallel geöffneten Formularen und kein unnötiges Hin- und
Herspringen.

Der Einrichtungsassistent wird als eigenständiges Modul vorgesehen. Aufbau,
Schrittlogik, Kachelgestaltung, Validierung, Abbrechen und der optionale freie
Modus werden später in einem eigenen Modell-/UX-Baustein detailliert. Die
Umsetzung dieser Oberfläche bleibt bis dahin offen.

## Modell 18: `portal_adapters.AdapterConnection`

### Fachlich bestätigt: technische Adapterverbindung

Die technische Verknüpfung wird nicht in einem eigenen Modell je Adapter
abgebildet. `WebUntisConnection` ist eine bisherige, adapter­spezifische
Altstruktur und wird im Zielbild durch das allgemeine Modell
`AdapterConnection` ersetzt.

`StudentModuleConnection` beschreibt ausschließlich die fachliche
Modulfreigabe eines Schülers. `AdapterConnection` beschreibt die technische
Zuordnung von Adapter, Modul, Kontext und Zugang. Zugangsdaten werden separat
in `CredentialBinding` gespeichert; Gesundheits- und Störungsinformationen
bleiben im Healthcheck-/Adapterstatusbereich.

Die technische Verbindung wird aus diesen Zuordnungen automatisch hergestellt
und muss nicht von einer Person manuell gepflegt werden.

#### Zielmodell `AdapterConnection`

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Verbindungs-ID |
| `adapter` | Verweis auf den gewählten Adapter |
| `module` | Verweis auf das Portalmodul |
| `student` | optionaler Kindkontext |
| `household` | optionaler Familienkontext |
| `school` | optionaler Schulkontext |
| `credential_binding` | verwendeter Zugang |
| `external_identity` | externe Schüler-/Benutzer-ID |
| `state` | Entwurf, bereit, aktiv, deaktiviert oder Fehler |
| `created_at` / `updated_at` | Zeitstempel |

`AdapterConnection` erhält kein zusätzliches fachliches `is_enabled`; die
Freischaltung erfolgt über `StudentModuleConnection`.

`StudentModuleConnection` ist eine interne, systemverwaltete
Konfigurationstabelle. Nutzer greifen nicht direkt auf die Tabelle zu. Eine
Oberfläche kann zwar eine Freischaltung oder Deaktivierung auslösen, diese
Aktion wird aber über die Anwendung geprüft und in der Konfiguration
gespeichert.

## Modell 19: `CredentialBinding`

`CredentialBinding` ist die allgemeine, interne Konfiguration für technische
Zugänge. Ein eigenes Zugangsdatenmodell je Adapter wird nicht vorgesehen.

### Zielmodell – bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Zugang-ID |
| `scope` | `student`, `household`, `school` oder `shared` |
| `adapter` | zugehöriger Adapter |
| `owner_person` | optionaler Besitzer |
| `household` | optionaler Familienbezug |
| `school` | optionaler Schulbezug |
| `username_encrypted` | verschlüsselter Benutzername |
| `password_encrypted` | verschlüsseltes Passwort |
| `external_account_id` | optionale externe Konto-ID |
| `state` | Entwurf, bereit, aktiv, deaktiviert oder Fehler |
| `last_validated_at` | letzte erfolgreiche Zugangskontrolle |
| `created_at` / `updated_at` | Zeitstempel |

### Aktuelle Herkunft

Ein allgemeines Modell existiert aktuell noch nicht. Zugangsdaten liegen
teilweise in adapter­spezifischen Verbindungsmodellen, zum Beispiel als
verschlüsselter Benutzername, verschlüsseltes Passwort, Server- und
Schulbezug. Diese Bestandteile werden bei einer späteren Migration in
`CredentialBinding` überführt.

`CredentialBinding` bleibt eine interne Konfigurationstabelle. Nutzer greifen
nicht direkt auf sie zu, sondern ausschließlich über geprüfte Formulare und
Anwendungslogik. Klartextpasswörter werden weder exportiert noch in einer
Modellvisualisierung ausgegeben.

## Modell 21: `GuardianStudentRelationship`

Das Modell verbindet eine erwachsene beziehungsweise berechtigte Person mit
einem konkreten Schüler. Beide Seiten sind Fremdschlüssel auf `Person`; es
werden keine Personen dupliziert.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Beziehungs-ID |
| `guardian_person` | erwachsene oder berechtigte Person |
| `student_person` | zugeordneter Schüler |
| `relationship_type` | Erziehungsberechtigt, Pflegeperson, Stiefelternteil oder sonstige berechtigte Person |
| `is_legal_guardian` | gesetzliche Sorgeberechtigung |
| `valid_from` | Beginn der Beziehung |
| `valid_until` | optionales geplantes Ende |
| `ended_at` | tatsächliche Beendigung |
| `ended_by` | auslösende Person |
| `change_reason` | optionaler Änderungsgrund |
| `created_at` / `updated_at` | Zeitstempel |

Die Beziehung wird im Familienprozess durch einen bereits legitimierten
Erwachsenen angelegt und bearbeitet. Ein Status `offen / bestätigt /
widerrufen` sowie `verified_by` und `verified_at` gehören nicht in dieses
Modell. E-Mail-Bestätigung und Kontoaktivierung bleiben getrennte
Einladungsprozesse.

Die Verbindung zu `Household` entsteht indirekt über die jeweiligen
`HouseholdMembership`-Datensätze der beiden Personen. Eine gemeinsame
Haushaltszugehörigkeit erzeugt niemals automatisch Zugriff auf einen Schüler.

## Modell 22: `HouseholdMembership`

`HouseholdMembership` ersetzt die direkte Many-to-Many-Mitgliederliste am
Haushalt. Es verbindet eine `Person` mit einem `Household` und beschreibt die
Stellung dieser Person innerhalb des Haushalts.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Mitgliedschafts-ID |
| `household` | Fremdschlüssel auf `Household` |
| `person` | Fremdschlüssel auf `Person` |
| `role` | Erziehungsberechtigte Person, Schüler, Pflegeperson oder weitere berechtigte Person |
| `status` | aktiv, beendet oder widerrufen |
| `valid_from` | Beginn der Zugehörigkeit |
| `valid_until` | optionales Ende |
| `added_by` | anlegende Person beziehungsweise `UserAccount` |
| `created_at` / `updated_at` | Zeitstempel |

Die Haushaltsrolle, die konkrete `GuardianStudentRelationship` und eine
allgemeine Plattform-/Schul-/Klassenrolle bleiben getrennt. Ein autorisierter
Einrichtungsprozess legt die erforderlichen Datensätze automatisch an; eine
manuelle Übersetzung zwischen den Tabellen ist nicht erforderlich.

## Modell 23: `RoleAssignment`

`RoleAssignment` beschreibt organisatorische Rollen in einem Plattform-,
Schul- oder Klassenkontext. Es ist von Haushaltsrollen und konkreten
Schülerbeziehungen getrennt.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Rollenzuweisung |
| `user` | Konto, dem die Rolle zugewiesen ist |
| `school` | optionaler Schulkontext |
| `school_class` | optionaler Klassenkontext |
| `role` | zum Beispiel Hauptadministrator, Klassenadministrator, Lehrer oder Content Manager |
| `active` | Rolle aktiv/inaktiv |
| `assigned_by` | vergebende Person beziehungsweise `UserAccount` |
| `created_at` | Erstellungszeitpunkt |

Die Rolle wird ausschließlich für organisatorische Berechtigungen verwendet.
Haushalts- und Schülerrollen werden weiterhin über `HouseholdMembership` und
`GuardianStudentRelationship` abgebildet.

### Startumfang der aktuellen Ausbaustufe

Zum ersten Livegang wird nur der zentrale Plattformadministrator aktiv
verwendet. Zusätzlich sind redaktionelle und moderierende Rollen vorgesehen.
Im Code und in der Rollenpflege werden dafür die getrennten Rollen
`Content Manager`, `Editor` und `Moderator` verwendet: Der Content Manager
pflegt ausschließlich freigegebene Portal-Inhalte wie Veranstaltungen oder
Chat-Konfigurationen. Er erhält keinen Zugriff auf Schüler-, Familien-,
Kontakt- oder Abwesenheitsdaten. Der Editor bearbeitet redaktionelle Inhalte;
der Moderator prüft beziehungsweise moderiert ausdrücklich freigegebene
Bereiche wie Bild- und Chatmeldungen. `SchoolAdministrator` und `ClassAdministrator` bleiben als
vorbereitete Rollen im Modell dokumentiert, werden zunächst aber nicht
vergeben. Die aktuelle Plattform wird damit zentral durch den
Plattformadministrator betrieben; eine eigenständige Schul- oder
Klassenadministration gehört zu einer späteren Ausbaustufe.

Schüler-Stammdaten, Klassenwechsel und schulische Zuordnungen werden zum
Start ausschließlich durch den Plattformadministrator gepflegt. Adapterdaten
wie Stundenplan, Hausaufgaben und Vertretungen werden nur über die jeweilige
technische Verbindung abgerufen. Eine spätere Delegation an Schul- oder
Klassenadministratoren bleibt als Ausbaustufe offen.

## Modell 24: `Invitation`

`Invitation` ist das gemeinsame, zeitlich begrenzte Prozessmodell für
persönliche E-Mail-Links und offene Access Codes. Ein eigenes
`FamilyAccessCode`-Modell wird nicht vorgesehen.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Einladungs-ID |
| `type` | `email_link` oder `access_code` |
| `purpose` | `initial_registration` oder `person_activation` |
| `email` | Zieladresse |
| `token_hash` | gehashter Einladungs-Token |
| `expires_at` | Ablaufzeitpunkt |
| `used_at` | Zeitpunkt der Verwendung |
| `confirmation_token_hash` | gehashter Token für die E-Mail-Bestätigung |
| `confirmed_at` | Zeitpunkt der bestätigten E-Mail-Adresse |
| `account_activated_at` | Zeitpunkt der automatischen Kontoaktivierung |
| `invited_by` | einladende Person beziehungsweise `UserAccount` |
| `first_name` / `last_name` | optionale vorgeschlagene Namen |
| `school` | optionaler Schulbezug |
| `school_class` | optionaler Klassenbezug |
| `household` | optionaler Haushaltsbezug |
| `family_request` | optionaler Registrierungsantrag |
| `target_person` | optional vorgesehene Person |
| `intended_role` | optionale vorgesehene Rolle |
| `relationship_type` | optionale vorgesehene Schülerbeziehung |
| `batch_id` | optionale gemeinsame Access-Code-Serie |
| `serial_number` | optionale Seriennummer eines Access Codes |
| `max_uses` / `use_count` | Nutzungslimit und bisherige Nutzungen |
| `created_at` | Erstellungszeitpunkt |

Für `email_link` gilt: Der Link ist an die Zieladresse gebunden, 72 Stunden
gültig, einmalig verwendbar und widerrufbar. Nach der Bestätigung des
E-Mail-Links wird das Konto unmittelbar aktiviert; eine zusätzliche manuelle
Freigabe durch den Plattformadministrator ist nicht erforderlich.

Für `access_code` gilt: Der Code ist nicht personengebunden, aber immer an
eine konkrete Klasse gebunden. Er besitzt ein Ablaufdatum und zunächst ein
Nutzungslimit von drei Einlösungen. Nach der Dateneingabe wird an die
angegebene E-Mail-Adresse ein persönlicher Bestätigungslink gesendet. Erst
dessen Bestätigung aktiviert das jeweilige Konto automatisch.

Schule und Klasse werden beim Erstellen und Einlösen auf Konsistenz geprüft.
Kein Einladungslink und kein QR-Code gewährt unmittelbar Zugriff auf Schüler-
oder Familiendaten; beide starten ausschließlich den abgesicherten
Einrichtungsprozess.
Der erste Erwachsene erfasst beim initialen Einstieg ausschließlich sich
selbst. Weitere Personen werden erst nach dessen Aktivierung im Portal
angelegt und erhalten einen persönlichen Bestätigungslink. Nach der
Bestätigung entstehen die dauerhaften Datensätze wie `UserAccount`, `Person`,
`HouseholdMembership`, `GuardianStudentRelationship` oder `RoleAssignment`
getrennt vom Einladungsprozess.

## Modell 26: `FamilyRegistrationRequest` – entfällt

Das bisherige Familien-Registrierungsmodell wird nicht weitergeführt. Der
frühere Sammelantrag für Access Code, Haushalt, mehrere Erwachsene und
mehrere Kinder widerspricht dem bestätigten einheitlichen Prozess.

Der erste Erwachsene registriert ausschließlich sich selbst. Haushalt,
weitere Personen und Beziehungen werden danach über den Einrichtungsprozess
und `Invitation` angelegt.

## Modell 27: `FamilyChildAccount` – entfällt

Das bisherige Kinderkonto-Modell wird nicht weitergeführt. Ein Schüler wird
einheitlich über `Person`, `HouseholdMembership` und gegebenenfalls
`GuardianStudentRelationship` angelegt. Ein eigenes Login wird bei Bedarf
über eine optionale Verbindung zu `UserAccount` und den gemeinsamen
`Invitation`-Prozess erzeugt.

Direkte Passwortfelder und ein separates technisches Kinderkonto gehören
nicht in die fachliche Zielstruktur.

## Modell 28: `AccountDeletionRequest`

`AccountDeletionRequest` bleibt als eigenständiges Datenschutz- und
Sicherheitsmodell bestehen. Es steuert den Löschantrag für ein
`UserAccount`, nicht die Kontodaten selbst.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutiger Löschantrag |
| `user` | betroffenes Benutzerkonto |
| `requested_at` | Zeitpunkt des Antrags |
| `execute_after` | frühester Ausführungszeitpunkt |
| `status` | vorgemerkt, abgeschlossen oder Fehler |
| `processed_at` | tatsächliche Verarbeitung |
| `failure_reason` | Fehlerbeschreibung |

Der Ablauf prüft zunächst Wartefrist, Aufbewahrungspflichten, abhängige
Daten und offene Beziehungen. Erst danach wird gelöscht oder anonymisiert;
der Vorgang wird zusätzlich im Audit dokumentiert.

## Modell 29: `DepartureRetentionCase`

`DepartureRetentionCase` dokumentiert die Datenschutz- und
Aufbewahrungsfolge, wenn ein Schüler eine Klasse verlässt. Die eigentliche
Klassenzugehörigkeit bleibt in `ClassMembership`.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutiger Aufbewahrungsfall |
| `student` | betroffener Schüler |
| `school_class` | verlassene Klasse |
| `left_at` | Austrittsdatum |
| `purge_after` | frühestes Löschdatum |
| `access_revoked_at` | Zeitpunkt des Zugriffsentzugs |
| `processed_at` | Zeitpunkt der Verarbeitung |

Der Fall startet mit dem Ende einer `ClassMembership`, entzieht Zugriffe,
wartet die definierte Aufbewahrungsfrist ab und steuert anschließend die
Prüfung sowie Löschung oder Anonymisierung.

## Modell 30: `ConsentType`

`ConsentType` definiert, welche Art von Einwilligung im System existiert.
Die Definition ist von Textversionen und individuellen Entscheidungen
getrennt.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Einwilligungsart |
| `key` | eindeutige technische Kennung |
| `label` | sichtbare Bezeichnung |
| `category` | allgemein, Foto oder Biometrie |
| `purpose` | Zweck der Einwilligung |
| `recipients` | vorgesehene Empfänger |

Die konkrete Entscheidung wird über `ConsentDecision` und der gültige
rechtliche Text über `ConsentTextVersion` abgebildet.

## Modell 31: `ConsentTextVersion`

`ConsentTextVersion` speichert unveränderliche Versionen eines
Einwilligungstextes. Bereits verwendete Versionen werden nicht überschrieben.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Textversions-ID |
| `consent_type` | Bezug zu `ConsentType` |
| `version` | Versionsnummer |
| `text` | vollständiger Einwilligungstext |
| `effective_from` | Beginn der Gültigkeit |

Die konkrete Entscheidung verweist immer auf die zum Entscheidungszeitpunkt
verwendete Textversion.

## Modell 32: `ConsentDecision`

`ConsentDecision` speichert die konkrete Entscheidung einer Person für eine
Einwilligungsart und deren Textversion.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Entscheidungs-ID |
| `consent_type` | Art der Einwilligung |
| `text_version` | verwendete Textversion |
| `subject_person` | Person, auf die sich die Einwilligung bezieht |
| `deciding_person` | entscheidende Person |
| `decision` | zugestimmt, abgelehnt oder widerrufen |
| `decided_at` | Entscheidungszeitpunkt |
| `valid_from` / `valid_until` | Gültigkeitszeitraum |
| `revoked_at` | Zeitpunkt des Widerrufs |
| `source` | Quelle, zum Beispiel Webportal |

Die konkrete Entscheidung verweist immer auf `ConsentType` und
`ConsentTextVersion`. Der in `ConsentType` gepflegte Empfängerkreis ist nur
eine fachliche Definition; eine individuelle Empfängerzuordnung wäre ein
späterer eigener Baustein.

## Modell 33: `AuditEvent`

`AuditEvent` bleibt als unveränderbarer Sicherheits- und Nachweisdatensatz
bestehen.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Ereignis-ID |
| `occurred_at` | Zeitpunkt des Ereignisses |
| `actor` | auslösendes Benutzerkonto |
| `action` | ausgeführte Aktion |
| `target_type` | Typ des betroffenen Objekts |
| `target_id` | ID des betroffenen Objekts |
| `metadata` | ergänzende technische Informationen |

Auditdaten werden nicht als normale Fachobjekte bearbeitet oder
überschrieben. Ihre Aufbewahrung und Bereinigung werden über die zentrale
Datenpflege mit einer eigenen Retention-Regel gesteuert. Vor einer Löschung
sind Schutzfristen, Nachweisbedarf, Vorschau und Konsistenzprüfung zu
berücksichtigen.

## Modell 34: `MonitoringSnapshot`

`MonitoringSnapshot` bleibt als technisches Betriebsmodell für aggregierte
Messwerte bestehen. Es enthält keine personenbezogenen Fach- oder
Zugangsdaten.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Snapshot-ID |
| `source` | Herkunft des Monitorings |
| `captured_at` | Zeitpunkt der Messung |
| `values` | aggregierte Messwerte |

Für Snapshots wird eine Verwaltungsmaske unter der zentralen Datenpflege
vorgesehen. Dort werden Aufbewahrungsdauer, Bereinigungsintervall,
Vorschau/Testlauf und der eigentliche Bereinigungsjob konfiguriert. Eine
automatische Löschung wird erst nach dokumentierter Konsistenzprüfung und
Freigabe aktiviert.

## Modell 35: `MonitoringComponent`

`MonitoringComponent` ist ein Stammdatensatz mit genau einem Datensatz je
überwachter technischer Komponente. Der Datensatz wird aktualisiert und nicht
für jeden Bericht neu angelegt.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Komponenten-ID |
| `component` | überwachte Komponente |
| `state` | in Ordnung, Warnung oder kritisch |
| `changed_at` | letzte Statusänderung |
| `last_reported_at` | letzter Statusbericht |

Historische Messwerte und Statusverläufe gehören in `MonitoringSnapshot` oder
technische Logs. Für diese Verlaufsdaten gelten die zentralen
Aufbewahrungs- und Bereinigungsjobs; der aktuelle Komponentenstatus selbst
wird nicht automatisch gelöscht.

## Modell 36: `PushSubscription`

`PushSubscription` speichert automatisch die technische Zustellungsmöglichkeit
für ein konkretes Gerät oder einen Browser. Beim Aktivieren erzeugt der
Browser die Subscription; der Nutzer muss kein Gerät auswählen oder manuell
benennen.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Geräte-/Browser-Subscription |
| `user` | zugehöriges Benutzerkonto |
| `endpoint_hash` | eindeutige technische Kennung |
| `endpoint` | Push-Endpunkt |
| `p256dh` | Verschlüsselungsschlüssel |
| `auth` | Authentifizierungswert |
| `enabled` | Push für dieses Gerät aktiv/inaktiv |
| `device_label` | automatisch ermittelte optionale Bezeichnung |
| `created_at` | Registrierungszeitpunkt |

Ein Benutzer kann mehrere automatisch registrierte Geräte oder Browser haben.
Die technische Geräteerkennung erfolgt beim Aktivieren beziehungsweise
Deaktivieren der Push-Funktion.

## Modell 37: `UserNotification`

`UserNotification` ist das persönliche In-App-Postfach eines Benutzers. Eine
Benachrichtigung erhält neben dem Empfänger einen fachlichen Ursprung und
einen klaren Geltungsbereich.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Benachrichtigung |
| `user` | Empfänger |
| `school` | optionaler Schulbezug |
| `school_class` | optionaler Klassenbezug |
| `student` | optionaler Schülerbezug |
| `adapter` | optionaler technischer Adapterbezug |
| `module` | optionaler Portalmodulbezug |
| `category` | Benachrichtigungskategorie |
| `object_type` / `object_id` | konkretes Ursprungsobjekt |
| `revision` | Version zur Duplikatvermeidung |
| `audience_scope` | zum Beispiel Person, Schüler, Klasse oder Schule |
| `title` | Überschrift |
| `summary` | Kurztext |
| `target_url` | Ziel beim Öffnen |
| `created_at` | Erstellung |
| `read_at` | Zeitpunkt des Lesens |

Beispiele sind eine Störung des Chat-Moduls, eine Abwesenheitsmeldung für
einen Schüler oder eine schulweite Nachricht wie „Morgen ist Hitzefrei“.
Die Empfänger werden anhand des Geltungsbereichs und ihrer aktivierten
Benachrichtigungseinstellungen ermittelt.

## Modell 38: `NotificationPreference`

Die bisherige `PushPreference` wird fachlich zu einer allgemeinen
`NotificationPreference` erweitert. Sie steuert, ob ein Benutzer eine
Benachrichtigungskategorie über einen bestimmten Kanal erhält.

### Bestätigte Zielstruktur

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Einstellung |
| `user` | Benutzerkonto |
| `key` | Benachrichtigungskategorie |
| `channel` | Push oder In-App |
| `module` | optionaler Modulbezug |
| `enabled` | aktiviert/deaktiviert |
| `updated_at` | letzte Änderung |

`PushSubscription` bleibt ausschließlich die technische Gerätezuordnung.
Die Notification Preference entscheidet, ob eine Kategorie über einen Kanal
zugestellt werden darf.

## Modell 39: `OnboardingState`

`OnboardingState` gehört fachlich zum späteren Modul
`Einrichtungsassistent`. Es speichert ausschließlich den Fortschritt des
Benutzers, nicht den Aufbau der Kacheln oder Formulare.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutiger Statusdatensatz |
| `user` | Benutzerkonto |
| `current_step` | aktueller Einrichtungsschritt |
| `initial_access_confirmed_at` | bestätigte Erstfreischaltung |
| `completed_at` | abgeschlossener Assistent |
| `completed_policy_version` | verwendete Prozessversion |
| `updated_at` | letzte Änderung |

`initial_access_confirmed_at` dokumentiert die legitimierte Erstfreischaltung
und ist unabhängig von `current_step`. Die eigentliche Ablauf- und
Kachelstruktur wird separat im Einrichtungsassistenten definiert.

## Modell 40: `TutorialState` – entfällt

Ein fortlaufender Tutorial-Fortschritt wird nicht vorgesehen. Der
Einrichtungsassistent ist der einzige geführte Pflichtprozess.

Tutorials werden in einer späteren Phase als optionale kontextbezogene Hilfe
direkt in einzelnen Masken angeboten, zum Beispiel über ein Fragezeichen-
Element. Sie können Beispiele und kurze Erklärungen enthalten, führen aber
keinen verpflichtenden Fortschrittsstatus pro Benutzer.

## Modell 41: `MenuItem` – entfällt

Das bisherige frei hierarchische `MenuItem`-Modell wird nicht als Zielmodell
weitergeführt. Die neue Navigation wird später aus Sichtbarkeit, Rolle,
Berechtigung, Modul und Navigationskontext abgeleitet. Die konkrete
Navigationstruktur und das Design werden in einem eigenen Konzept festgelegt.

## Modell 42: `LogoRequest` – entfällt

Ein eigener Logo-Anfrage- und Bearbeitungsprozess wird nicht vorgesehen.
Anzeigename und optionales Logo werden direkt in den Verwaltungsdaten von
`School` beziehungsweise `SchoolClass` gepflegt.

Für `SchoolClass` wird ein Anzeigename vorgesehen. Als Default wird der
Schulname, ein Trennzeichen und die Klassenbezeichnung verwendet. Ein eigenes
Klassenlogo kann optional hinterlegt werden. Format, Pixelgröße und weitere
Uploadregeln werden erst mit dem verbindlichen CSS-/Designsystem festgelegt.

## Modell 43: `PilotReport`

`PilotReport` bleibt als internes Feedback- und Testmodell bestehen.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Rückmeldung |
| `reporter` | meldende Person |
| `school_class` | optionaler Klassenbezug |
| `kind` | Idee, Hinweis oder Fehler |
| `page_path` | betroffene Seite |
| `description` | Beschreibung |
| `screenshot` | optionaler Screenshot |
| `status` | neu, geprüft, in Arbeit, erledigt oder verworfen |
| `reviewed_by` / `reviewed_at` | Bewertung durch Administration |
| `github_issue_url` / `github_issue_id` | optionaler GitHub-Issue-Bezug |
| `follow_up_conversation` | optionaler persönlicher Chatbezug |
| `follow_up_message` | optionale konkrete Rückfragenachricht |
| `created_at` / `resolved_at` | Zeitstempel |

Die Verwaltungsansicht soll Rückmeldungen bewerten, bei Bedarf direkt ein
GitHub-Issue erzeugen und eine persönliche Rückfrage an den jeweiligen Nutzer
starten können. Die Rückfrage bleibt am Feedbackeintrag verknüpft und zeigt
weiterhin, ob es sich um Idee, Hinweis oder Fehler handelt.

## Modell 44: `ChatRetentionCategory`

`ChatRetentionCategory` bleibt als Aufbewahrungskonfiguration für Chats
bestehen und wird in die zentrale Datenpflege integriert.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Kategorie-ID |
| `name` | Bezeichnung der Aufbewahrungskategorie |
| `retention_days` | Aufbewahrungsdauer |
| `automatic_deletion_enabled` | automatische Löschung aktiviert |
| `intended_for_events` | Kategorie für Veranstaltungs-Chats |
| `is_active` | Kategorie aktiv |

Die zentrale Datenpflege bietet hierfür Verwaltungsmaske, Vorschau-/Testlauf,
konfigurierbare Löschjobs, Ergebnisprüfung und Fehlerbericht. Die Kategorie
wird von `ChatRoom` verwendet; gelöscht werden nur Nachrichten, die die
zugehörige Regel erfüllen.

## Modell 45: `ChatRoom`

`ChatRoom` beschreibt einen Chatraum im Kontext einer Schule und einer
konkreten Klasse. Das Schuljahr wird nicht zusätzlich gespeichert, weil die
Klasse bereits eindeutig Schule und Schuljahr zugeordnet ist.

### Bestätigte Zielstruktur

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` / `public_id` | interne und öffentliche Raum-ID |
| `school` | eindeutige Schule |
| `school_class` | eindeutige Klasse, zum Beispiel 5e |
| `event` | optional verknüpftes Event |
| `retention_category` | Aufbewahrungsregel |
| `title` | Raumname |
| `created_by` | erstellende Person beziehungsweise Administrationskonto |
| `chat_style` | Verweis auf einen administrativen Chat-Style |
| `room_type` | Direktnachricht, Gruppe, Klasse, Schule oder schulübergreifend |
| `is_open` | Raum offen oder geschlossen |
| `youth_protection_enabled` | Jugendschutz aktiv oder inaktiv |
| `youth_protection_profile` | administratives Regel-/Schwellenprofil für den Chat |
| `created_at` | Erstellungszeitpunkt |

Der Zugriff wird nicht über ein einfaches `audience`-Textfeld geregelt,
sondern über `ChatRoomAccess`. Der Style verweist auf definierte visuelle
Bausteine; freie CSS-Regeln werden nicht im Chatraum gespeichert.

Eine persönliche Unterhaltung ist kein eigenes Fachmodell. Sie wird als
`ChatRoom` mit `room_type = direct` und genau zwei aktiven
`ChatRoomAccess`-Einträgen geführt. Das bisherige `DirectConversation`-Modell
entfällt als eigenständige Struktur.

### Erstellungsregeln

Einzel- und Gruppenchats dürfen Nutzer selbst eröffnen. Sie dürfen nur
Personen aus dem zulässigen Klassenkontext einladen; die Einladung wird über
`ChatRoomInvitation` bestätigt und erzeugt anschließend den individuellen
`ChatRoomAccess`-Eintrag. Große Räume für eine gesamte Klasse, Schule oder
später schulübergreifende Bereiche werden ausschließlich durch den
Plattformadministrator oder einen dafür berechtigten `Content Manager`
angelegt und verwaltet. Schüler erhalten dadurch keine Möglichkeit, einen
offenen Klassen- oder Schulraum zu erzeugen.

## Modell 46: `ChatRoomAccess`

`ChatRoomAccess` speichert die tatsächliche Zuordnung eines Chatraums zu einer
konkreten Person. Die Einträge werden aus Klassen-, Rollen- und
Einzelzuweisungen automatisch erzeugt beziehungsweise aktualisiert.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Zugriffs-ID |
| `chat_room` | zugehöriger Chatraum |
| `person` | konkrete berechtigte Person |
| `access_role` | Schüler, Erziehungsberechtigter, Lehrkraft oder Moderator |
| `is_visible` | Raum in der Übersicht sichtbar |
| `access_level` | zunächst `member`, für spätere Erweiterungen vorbereitet |
| `source_type` | Klasse, Rolle oder Einzelzuweisung |
| `source_reference` | kontrollierter Bezug zur auslösenden Regel |
| `valid_from` / `valid_until` | Gültigkeitszeitraum |
| `is_active` | Zugriff aktiv/inaktiv |
| `granted_by` | vergebende Person |
| `created_at` / `updated_at` | Zeitstempel |

Im aktuellen Chat bedeutet aktiver Zugriff zugleich Nutzbarkeit. `is_visible`
steuert zusätzlich, ob der Raum in der persönlichen Raumübersicht erscheint.

## Modell 47: `ChatRoomInvitation`

`ChatRoomInvitation` dokumentiert persönliche Einladungen in einen Chatraum.
Eine Einladung erzeugt noch keinen Zugriff; dieser entsteht erst nach Annahme.

### Zielmodell

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Einladung |
| `chat_room` | eingeladener Raum |
| `invited_person` | eingeladene Person |
| `invited_by` | einladende Person |
| `status` | offen, angenommen, abgelehnt oder abgelaufen |
| `invited_at` | Einladungszeitpunkt |
| `responded_at` | Antwortzeitpunkt |
| `expires_at` | optionaler Ablauf |
| `notification` | Bezug zur In-App-Einladung |

Die Oberfläche verwendet eine Vorschlags- und Auswahlliste statt eines freien
Textfelds. Die Liste wird bereits während der Eingabe live gefiltert; ein
separater Suchbutton ist nicht vorgesehen. Beim Öffnen kann zunächst die
vollständige berechtigte Liste angezeigt werden. Nach Annahme wird ein
passender `ChatRoomAccess`-Datensatz erzeugt.

## Modell 48: `ChatMessage`

`ChatMessage` bleibt als Nachrichtenmodell bestehen. Der Nachrichtentext ist
ein zulässiges echtes Textfeld, weil dort der individuelle Inhalt gespeichert
wird.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` / `public_id` | interne und öffentliche Nachrichten-ID |
| `room` | Chatraum |
| `author` | Absender |
| `reply_to` | optionale Antwort auf eine Nachricht |
| `mentions` | erwähnte Benutzer |
| `body` | individueller Nachrichtentext |
| `attachment` | optionaler Dateianhang |
| `attachment_name` / `attachment_content_type` | Dateimetadaten |
| `attachment_safety_status` | nicht erforderlich, ausstehend, freigegeben oder gesperrt |
| `language_filter_hits` | zusammengefasste Filtertreffer |
| `created_at` / `edited_at` | Erstellung und Bearbeitung |
| `withdrawn_at` / `hidden_at` / `hidden_by` | Rücknahme und Moderationsausblendung |

Jugendschutz- und Sprachfilterereignisse werden mit Nachrichten-ID, Absender,
Zeitpunkt, Regel und Ergebnis in technischen beziehungsweise Audit-Logs
protokolliert. `language_filter_hits` bleibt lediglich eine Kurzangabe an der
Nachricht.

### Fachlich festgelegt: automatische Jugendschutzprüfung

Der Jugendschutz wird für Text und Bildmedien automatisch ausgeführt. Bei
einem Treffer wird der Inhalt im Chat ausgeblendet: Text wird ausgepunktet,
ein Bild wird ausgepixelt. Die technische Originalinformation bleibt für die
berechtigte Prüfung erhalten; eine normale Benutzeroberfläche zeigt sie nicht
unmittelbar an.

Der Textfilter muss über versionierte, administrierbare Regeln erweiterbar
sein. Eine Regel umfasst fachlich mindestens Suchbegriff oder
Ausdrucksgruppe, Kategorie, Schweregrad, Normalisierungs-/Variantenregeln,
Geltungsbereich, Aktion, Aktivstatus und Gültigkeit. Damit können weitere
Wörter und Schreibvarianten über eine geschützte Verwaltungsmaske ergänzt
werden, ohne den Chat-Code zu ändern. Die Regel selbst ist kein freies
Benutzer-Textfeld; sie wird als kontrollierter Sicherheitskatalog gepflegt.

Ein Absender kann den eigenen automatisch verborgenen Text oder das eigene
Bild auswählen und eine Prüfung durch den zuständigen Moderator anfordern.
Zum Start sind das der Plattformadministrator beziehungsweise der
Administrator der betreffenden Klasse. Eine spätere Rolle `Chat-Moderator`
bleibt vorbereitet.

Bei einem automatisch maskierten Bild erhält der Absender eine verständliche
Hinweismeldung. Der Absender kann für dieses Bild einen Prüf-Antrag stellen.
Dieser Antrag wird im Administrationsdashboard mit Bildreferenz, Regel,
Messwerten, Benutzer, Chatraum und Zeitpunkt angezeigt. Die allgemeine
Funktion „diesen Chat melden“ bleibt dagegen zunächst deaktiviert.

Jeder Treffer wird mit Nachricht, Absender, Zeitpunkt, Regel, Medium und
Ergebnis im technischen beziehungsweise Audit-Protokoll erfasst. Wenn ein
Benutzer innerhalb von 24 Stunden mehrfach auslöst, erzeugt die Anwendung
einen Administrationshinweis mit Anzahl, Zeitraum und Referenzen. Das ist
eine Prüfaufforderung und keine automatische Sanktion.

Ein eigenes Modell für einen frei pflegbaren Moderationsstatus wird nicht
vorgesehen. Der technische Zustand ergibt sich aus Nachricht, Filterereignis,
Ausblendung und gegebenenfalls Prüfanforderung. Eine spätere
Chat-Moderatorenrolle erweitert nur die Berechtigungsprüfung.

Die Empfindlichkeit wird über ein versioniertes Jugendschutzprofil gesteuert.
Darin werden aktivierte Regelgruppen, Text- und Bildschwellen,
Medienfreigaben und das Verhalten bei Grenzfällen gepflegt. Das Profil kann
global, einer Schule, einer Klasse oder einem einzelnen Chatraum zugeordnet
werden. Ein eigenes lernendes Bildmodell bleibt konzeptionell vorbereitet,
ist aber kein Bestandteil der ersten Variante und lernt nicht automatisch aus
Test- oder Prüfaufnahmen.

## Modell 49: `ChatReadState`

`ChatReadState` speichert, bis zu welchem Zeitpunkt eine Person einen
Chatraum gelesen hat.

### Bestätigte Felder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Lesestatus-ID |
| `room` | Chatraum |
| `user` | Benutzerkonto |
| `last_read_at` | letzter gelesener Zeitpunkt |

Pro Kombination aus Chatraum und Benutzerkonto gibt es genau einen Datensatz.

## Modell 50: `ChatStyle`

`ChatStyle` definiert die visuelle Darstellung eines Chatraums, ohne freie
CSS-Regeln im Chatraum zu speichern.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Style-ID |
| `key` | automatisch erzeugter technischer Schlüssel |
| `label` | sichtbarer Name, zum Beispiel „Sommerferien“ |
| `theme` | Bezug zu einem zentralen Theme oder Farbschema |
| `font` | Bezug zu einer definierten Schriftart |
| `effect` | optionaler visueller Effekt |
| `background_asset` | optionales Hintergrundbild |
| `message_layout` | Nachrichtenlayout, zum Beispiel Standard-Bubbles |
| `is_active` | Style auswählbar |
| `created_at` / `updated_at` | technische Zeitpunkte |

### Erste Empfehlung

Farben, Schriftarten und Effekte werden nicht als freie CSS-Texte im
`ChatStyle` gespeichert. Sie verweisen auf zentrale Designbausteine. Ein
`ChatRoom` kann dadurch einen Style wie „Sommerferien“ oder „Winter“ nutzen,
ohne dass seine Jugendschutzregeln verändert werden.

## Modell 51: `ChatSafetyProfile`

`ChatSafetyProfile` bündelt die fachliche Empfindlichkeit und die aktiven
Jugendschutzregeln eines Geltungsbereichs. Es ist ein Konfigurationsmodell;
einzelne Treffer werden weiterhin über `AuditEvent` protokolliert.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Profil-ID |
| `key` | technischer Schlüssel |
| `label` | sichtbarer Profilname |
| `version` | versionierte Konfiguration |
| `scope_type` / `scope_id` | global, Schule, Klasse oder Chatraum |
| `enabled_rule_groups` | zugeordnete `ChatSafetyRule`-Gruppen |
| `text_thresholds` | Schwellenwerte für Textregeln |
| `image_thresholds` | Schwellenwerte je Bildkategorie |
| `allowed_media_types` | erlaubte Medienarten |
| `borderline_action` | Verhalten bei Grenzwerten |
| `image_appeal_enabled` | Bild-Prüfantrag aktiv/inaktiv |
| `provider` / `model_version` | verwendeter Prüfprovider und Modellstand |
| `is_active` | Profil aktiv/inaktiv |
| `valid_from` / `valid_until` | Gültigkeitszeitraum |
| `created_by` | administrativ verantwortliche Person |
| `created_at` / `updated_at` | technische Zeitpunkte |

### Erste Empfehlung

Schwellenwerte und Regelgruppen sollten nicht direkt am `ChatRoom` gepflegt
werden. Ein Profil kann dadurch für mehrere Klassen oder Räume verwendet,
versioniert und kontrolliert geändert werden. Ein eigenes lernendes Modell
bleibt lediglich als späterer Prüfprovider vorgesehen.

## Modell 52: `ChatSafetyAppeal`

`ChatSafetyAppeal` speichert den Antrag einer Person, ein automatisch
maskiertes Bild prüfen zu lassen. Es ist ein eigenständiger Prüfprozess und
kein allgemeines Moderationsstatusfeld der Nachricht.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Antrag-ID |
| `message` | betroffene Chat-Nachricht |
| `attachment` | betroffenes Bild |
| `requester` | antragstellende Person |
| `safety_profile` | angewendetes Jugendschutzprofil |
| `audit_event` | ursprüngliches Filterereignis |
| `reason` | optionale Begründung der antragstellenden Person |
| `status` | offen, in Prüfung, freigegeben, abgelehnt oder zurückgezogen |
| `reviewed_by` | prüfende Administratorperson |
| `decision_note` | interne Prüfnotiz |
| `submitted_at` | Antragstellung |
| `reviewed_at` | Prüfzeitpunkt |
| `released_at` | Zeitpunkt einer Freigabe |

### Erste Empfehlung

Ein Antrag darf zunächst nur für automatisch maskierte Bildanhänge entstehen.
Die allgemeine Chat-Meldung bleibt davon getrennt und deaktiviert. Mehrere
Prüfungen können dadurch nachvollziehbar gespeichert werden, ohne den Zustand
der ursprünglichen Nachricht zu überschreiben.

## Modell 53: `ChatReactionPack`

`ChatReactionPack` bündelt administrativ verwaltete Emojis, Sticker und
animierte Reaktionen für die Chat-Oberfläche.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Paket-ID |
| `key` | technischer Schlüssel |
| `label` | sichtbarer Paketname |
| `description` | optionale Beschreibung |
| `pack_type` | Emoji, Sticker, Animation oder gemischt |
| `scope` | global, Schule, Klasse oder Chatraum |
| `school` / `school_class` / `chat_room` | optionaler Geltungsbereich |
| `is_default` | standardmäßig verfügbar |
| `is_active` | aktiviert/deaktiviert |
| `sort_order` | Reihenfolge in der Auswahl |
| `created_by` | administrativ verantwortliche Person |
| `created_at` / `updated_at` | technische Zeitpunkte |

### Erste Empfehlung

Ein Paket enthält mehrere `ChatReactionAsset`-Einträge. Das Standardpaket ist
global verfügbar; weitere Pakete können gezielt Schulen, Klassen oder
Chatraäumen zugewiesen werden.

## Modell 54: `ChatReactionAsset`

`ChatReactionAsset` beschreibt ein einzelnes Emoji, einen Sticker oder eine
Animation innerhalb eines Reaktionspakets.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Asset-ID |
| `pack` | zugehöriges `ChatReactionPack` |
| `asset_type` | Emoji, Sticker oder Animation |
| `label` | sichtbarer Name |
| `unicode_value` | Unicode-Wert bei normalen Emojis |
| `file` | Bild- oder Animationsdatei |
| `thumbnail` | optionale Vorschau |
| `alt_text` | barrierefreie Beschreibung |
| `is_animated` | animiert oder statisch |
| `sort_order` | Reihenfolge im Paket |
| `is_active` | aktiviert/deaktiviert |
| `license_source` | Herkunft und Lizenznachweis |
| `file_size` / `width` / `height` | technische Dateiprüfung |
| `aspect_ratio` | geprüftes Seitenverhältnis |
| `safety_status` | ausstehend, freigegeben oder gesperrt |
| `created_by` | hochladende Administratorperson |
| `created_at` / `updated_at` | technische Zeitpunkte |

### Pflege- und Freigaberegeln

Die Asset-Pflege erfolgt zunächst ausschließlich durch den
Plattformadministrator. Eine spätere Freigabe für ausgewählte
Klassenadministratoren bleibt möglich; eine allgemeine Nutzerfunktion zum
Hochladen eigener Assets ist nicht vorgesehen.

Die Verwaltungsmaske prüft Dateiformat, Dateigröße, Seitenverhältnis,
Abmessungen, Sicherheitsstatus und Lizenzangabe. Kompakte Richtformate wie
48 × 48 Pixel oder 48 × 24 Pixel werden unterstützt; konkrete Grenzwerte
werden mit dem finalen Chat-Design festgelegt. Assets außerhalb der Vorgaben
werden nicht freigegeben.

## Modell 55: `ChatReaction`

`ChatReaction` speichert die Zuordnung einer Person zu einer Nachricht und
einem ausgewählten Emoji, Sticker oder Asset.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Zweck |
|---|---|
| `id` | eindeutige Reaktions-ID |
| `message` | betroffene Chat-Nachricht |
| `user` | reagierende Person |
| `asset` | verwendetes `ChatReactionAsset` |
| `created_at` | Zeitpunkt der Reaktion |
| `updated_at` | Zeitpunkt einer Änderung |
| `removed_at` | Zeitpunkt des Entfernens |

### Bestätigte Bedienlogik

Auf Smartphone und Tablet öffnet ein 500 ms langer Druck die Reaktionspalette.
Auf dem Desktop erscheint nach 500 ms Mouse-over eine kompakte Leiste. Eine
fokussierte Nachricht öffnet sie mit Enter oder Leertaste. Ein einfacher Klick
setzt keine Reaktion; ein Doppelklick wird nicht verwendet.

Direkt werden die vier häufigsten Reaktionen angeboten. Eine Person kann die
Reaktion ändern oder entfernen. Pro Nachricht und Benutzer wird dieselbe
Reaktion nur einmal gespeichert.

### Gesundheitsstatus

Ein separates fachliches Modell `AdapterHealthCheck` wird nicht vorgesehen.
Der Gesundheitsstatus wird an der konkreten Adapter-Modul-Zuordnung geführt.
Nach maximal drei Prüfversuchen kann genau diese Zuordnung auf `störung`
gesetzt werden; andere Module desselben Adapters bleiben unabhängig. Einzelne
historische Prüfungen gehören später in technische Logs und unterliegen den
zentralen Bereinigungsregeln.

## Modell 56: `CalendarEntry`

`CalendarEntry` ist der zentrale fachliche Kalendereintrag. Stundenplan,
Hausaufgaben, Prüfungen, Veranstaltungen, Vertretungen und Raumänderungen
können darüber angezeigt werden; die jeweiligen Fachdaten bleiben in ihren
eigenen Modellen.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Django-Typ | Zweck |
|---|---|---|
| `id` | `BigAutoField` | Primary Key |
| `school_class` | `ForeignKey` | Klasse |
| `school_year` | `ForeignKey` | Schuljahr |
| `student` | `ForeignKey`, optional | Schülerbezug |
| `event` | `ForeignKey`, optional | Veranstaltungsbezug |
| `homework` | `ForeignKey`, optional | Bezug zu einer Hausaufgabe |
| `source_adapter_connection` | `ForeignKey`, optional | Herkunftsadapter |
| `external_id` | `CharField`, optional | eindeutige Kennung beim Adapter |
| `subject` | `ForeignKey`, optional | Fach, zum Beispiel Englisch |
| `teachers` | `ManyToManyField`, optional | zugeordnete Lehrkräfte |
| `room` | `ForeignKey`, optional | kontrollierter Raumbezug |
| `kind` | kontrollierter Auswahlwert | Unterricht, Hausaufgabe, Prüfung, Veranstaltung, Ausfall, Vertretung oder Raumänderung |
| `title` | `CharField` | sichtbare Überschrift |
| `details` | `TextField`, optional | ergänzende Information |
| `starts_at` / `ends_at` | `DateTimeField` | Beginn und Ende |
| `is_all_day` | `BooleanField` | ganztägiger Eintrag |
| `visibility_policy` | `ForeignKey`, optional | Sichtbarkeit und Zielgruppe |
| `status` | kontrollierter Auswahlwert | aktiv, storniert oder ersetzt |
| `revision` | `PositiveIntegerField` | Änderungsnummer |
| `source_updated_at` | `DateTimeField`, optional | Änderungszeitpunkt beim Adapter |
| `imported_at` | `DateTimeField`, optional | Import-/Synchronisationszeitpunkt |
| `updated_at` | `DateTimeField` | letzte lokale Änderung |

### Fachliche Regeln

Ein allgemeiner freier Bezugstyp wird nicht verwendet. Der Eintrag erhält
stattdessen klar definierte optionale Relationen zu Schüler, Veranstaltung
und Hausaufgabe. Schule und Klasse bilden den organisatorischen Kontext.

Hausaufgaben bleiben ein eigenes Modell und werden nur optional als
Kalendereintrag gespiegelt. Die persönliche Darstellung — nur am Abgabetag,
an mehreren Tagen, erledigte Aufgaben ausblenden oder als „Erledigt“ zeigen —
gehört in eine Benutzereinstellung und nicht in `CalendarEntry`.

Mehrere Hausaufgaben am selben Tag sollen in der Kalenderansicht gruppiert
werden können, damit nicht unnötig viele Einzelkarten untereinander stehen.

## Modell 57: `Subject`

`Subject` definiert ein zentrales Unterrichtsfach. Dadurch können
Adapterkürzel wie `EN`, `ENG` oder `English` einheitlich auf „Englisch“
abgebildet werden.

### Aktueller Zustand

Ein eigenständiges `Subject`-Modell ist derzeit noch nicht vollständig
vorhanden. Fächer werden teilweise als Freitext geführt; zusätzlich bestehen
adapterbezogene Übersetzungstabellen.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` | eindeutige Fach-ID |
| `key` | `SlugField` | technischer Schlüssel, zum Beispiel `english` |
| `canonical_name` | `CharField` | offizieller Fachname |
| `short_name` | `CharField`, optional | kurze Anzeigeform |
| `subject_group` | `ForeignKey`, optional | Fachgruppe, zum Beispiel Sprachen |
| `school_level` | kontrollierter Wert, optional | Grundschule, Sek I oder Sek II |
| `is_active` | `BooleanField` | verfügbar oder archiviert |
| `created_at` / `updated_at` | `DateTimeField` | technische Zeitpunkte |

### Relationen

`Subject` wird von `CalendarEntry`, `TimetableEntry` und `Homework` verwendet.
Eine optionale Lehrplanzuordnung kann später ergänzt werden. Die
adapterabhängigen Kürzel werden nicht in `Subject`, sondern in einer eigenen
Mapping-Tabelle gepflegt.

## Modell 58: `AdapterSubjectMapping`

`AdapterSubjectMapping` ordnet eine externe Fachbezeichnung eines Adapters
einem zentralen `Subject` zu.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` | eindeutige Mapping-ID |
| `adapter_connection` | `ForeignKey` | technische Adapterverbindung |
| `source_code` | `CharField` | externer Fachcode |
| `source_label` | `CharField` | externe Fachbezeichnung |
| `subject` | `ForeignKey` | zentrales Fach |
| `context` | kontrollierter Wert | Kalender, Stundenplan oder Hausaufgaben |
| `school` | `ForeignKey`, optional | schulbezogene Ausnahme |
| `school_class` | `ForeignKey`, optional | klassenbezogene Ausnahme |
| `priority` | `PositiveIntegerField` | Vorrang bei mehreren Treffern |
| `is_active` | `BooleanField` | Mapping aktiv/inaktiv |
| `valid_from` / `valid_until` | `DateField`, optional | Gültigkeitszeitraum |
| `created_by` | `ForeignKey` | erstellende Administratorperson |
| `created_at` / `updated_at` | `DateTimeField` | technische Zeitpunkte |

### Erste Empfehlung

Das Mapping gilt möglichst global für den Adapter. Schule und Klasse werden
nur für echte Ausnahmen verwendet. Die Verwaltung zeigt unbekannte Codes in
einer Zuordnungsliste und erlaubt ausschließlich die Auswahl vorhandener
Fachrelationen.

## Modell 59: `AdapterTestRun`

`AdapterTestRun` dokumentiert einen Testlauf bei der Einrichtung eines
Adapters für eine Schule oder Klasse.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` | eindeutige Testlauf-ID |
| `adapter_connection` | `ForeignKey` | getestete Adapterverbindung |
| `school` / `school_class` | `ForeignKey` | Testkontext |
| `modules` | kontrollierte Relationen | getestete Module |
| `status` | kontrollierter Wert | gestartet, erfolgreich, teilweise erfolgreich oder fehlgeschlagen |
| `started_at` / `finished_at` | `DateTimeField` | Laufzeit |
| `record_counts` | `JSONField` | Ergebnisanzahlen je Modul |
| `unmapped_values` | `JSONField` | unbekannte Fach-, Lehrer- oder Raumwerte |
| `warnings` / `errors` | strukturierte Fehlerdaten | Hinweise und Fehler |
| `tested_by` | `ForeignKey` | prüfende Administratorperson |
| `confirmed_at` | `DateTimeField`, optional | Bestätigung der Zuordnungen |

Zugangsdaten werden nicht im Testlauf gespeichert. Sie werden über die
verschlüsselte Adapterverbindung nur für die Abfrage verwendet.

## Modell 60: `MarketingDemoSession`

`MarketingDemoSession` bildet einen zeitlich begrenzten Marketing-Testzugang
ab. Sie ist kein reguläres Benutzerkonto und keine dauerhafte Familie.

### Bestätigte Arbeitsfelder

| Feld/Arbeitsname | Django-Typ | Zweck |
|---|---|---|
| `id` | `UUIDField` | eindeutige Demo-ID |
| `token_hash` | `CharField` | gehashter, einmaliger Zugangslink |
| `email` | `EmailField` | Empfängeradresse |
| `school` | `ForeignKey`, optional | vorausgefüllte Schule |
| `school_class` | `ForeignKey` | ausgewählte Klasse |
| `display_name` | `CharField` | Name oder klar markierter Demo-Platzhalter |
| `adapter` | `ForeignKey` | ausgewählter Adapter |
| `module_results` | `JSONField` | Ergebnis je Modul |
| `status` | kontrollierter Wert | offen, aktiv, abgelaufen oder widerrufen |
| `started_at` | `DateTimeField`, optional | Start des Demo-Laufs |
| `expires_at` | `DateTimeField` | Ablauf nach 30 Minuten |
| `used_at` | `DateTimeField`, optional | einmalige Verwendung des Links |
| `retry_of` | `ForeignKey`, optional | Bezug zu einem erneuten Test |
| `created_at` | `DateTimeField` | Erstellung |

Zugangsdaten werden nur verschlüsselt für die Laufzeit verwendet und nach
Ablauf beziehungsweise erfolgreicher Bereinigung entfernt. Ein erneuter Test
erzeugt eine neue Session mit einem neuen Token.

## Zentrale Auslagerungsliste

Diese eine modellübergreifende Liste enthält alle Felder, die aus ihrem
aktuellen Modell herausgenommen, verschoben, zusammengeführt oder durch eine
Relation ersetzt werden könnten. Bei jedem Eintrag werden das Ursprungsmodell
und die bisherige Wirkung festgehalten. Die Liste wird bei der Besprechung
jedes weiteren Modells ergänzt; es werden keine separaten Auslagerungslisten
pro Modell angelegt.

Die Einträge sind zunächst nur Prüfkandidaten. Nichts wird gelöscht, bevor
Herkunft, Nutzung, Zielmodell und Datenübernahme geklärt sind.

| Feld | Ursprungsmodell | Bisherige Wirkung | Prüfkandidat für neues Modell |
|---|---|---|---|
| `source_id` | `core.School` | speichert die externe Kennung einer importierten Schule | `SchoolImportRecord` / externe Identität |
| `source_name` | `core.School` | speichert die Bezeichnung der Importquelle | `SchoolImportRecord` |
| `source_imported_at` | `core.School` | speichert den Zeitpunkt des letzten Imports | `SchoolImportRecord` |
| `source_raw` | `core.School` | hält die unverarbeiteten Quelldaten als JSON vor | `SchoolImportRecord` oder Importarchiv |
| `search_name` | `core.School` | normalisierte Suchdarstellung für Namenssuche/-vergleich | Suchindex oder weiterhin technisch abgeleitet |
| `latitude` | `core.School` | speichert den Breitengrad des Schulstandorts | `SchoolLocation` |
| `longitude` | `core.School` | speichert den Längengrad des Schulstandorts | `SchoolLocation` |
| `location_valid` | `core.School` | kennzeichnet, ob die Standortdaten geprüft wurden | `SchoolLocation` / Standortprüfung |
| `possible_duplicate_group` | `core.School` | gruppiert mögliche Dubletten aus der Bestandserfassung | `SchoolImportRecord` / Duplikatprüfung |
| `logo` | `core.School` | stellt ein einzelnes Schullogo bereit | `BrandingAsset` |
| `enabled_features` | `core.School` | speichert aktivierte Funktionen als JSON | `SchoolModuleOverride` / Modulkonfiguration |
| `visible_menu_items` | `core.School` | speichert sichtbare Menüpunkte als JSON | Menü-/Modulpolicy |
| `director` | `core.School` | speichert die Schulleitung als freien Text | später `Person`-/Rollenrelation oder schulische Kontaktrolle |
| `chat_display_name` | `core.Person` | frei gesetzter Chat-Anzeigename | entfällt; ersetzt durch `display_name_mode` |
| `contribution_name_mode` | `core.Person` | separate Namensauswahl für Mitbringlisten | entfällt; ersetzt durch `display_name_mode` |
| `home_latitude` / `home_longitude` | `core.Person` | speichert persönliche Standortkoordinaten | später Standort-/Mobilitätsmodell prüfen |
| `profile_photo` | `core.Person` | speichert das Profilbild direkt an der Person | `ProfilePhoto` |
| `profile_image_mode` | `core.Person` | schaltet Avatar oder Foto als Darstellung | `ProfileVisual.active_mode` |
| `avatar_key` / `avatar_seed` | `core.Person` | speichert Avatar-Auswahl und Variante | `AvatarSelection` |
| `field_visibility` | `core.Person` | speichert Sichtbarkeiten als JSON | Datenschutz-/Freigabemodell |
| `email_visibility` / `phone_visibility` / `relationship_visibility` | `core.Person` | einzelne Sichtbarkeitseinstellungen | Datenschutz-/Freigabemodell |
| `profile_photo_reference` | `core.StudentProfile` | technischer Profilfoto-Verweis am Schülerprofil | entfällt; `ProfileVisual` / `ProfilePhoto` |

Vorläufige Abgrenzung: `name`, `short_name`, `school_type`, externe amtliche
Kennung sowie geprüfte Kontakt- und Adressstammdaten verbleiben zunächst in
`School`. Ob einzelne Kontaktfelder wie `phone` oder `email` später in ein
separates `SchoolContact` verschoben werden, wird bei der Detailbesprechung
der Stammdaten entschieden.

Dieses Dokument ordnet die aktuell in Django registrierten Modelle fachlich
ein. Es ersetzt weder `docs/Architecture.md` noch `docs/DecisionLog.md` und
nimmt keine noch offenen Modellentscheidungen vorweg. Ziel ist eine gemeinsame
Arbeitsgrundlage für die schrittweise Bereinigung und spätere Migration.

## 1. Befund des aktuellen Stands

Der Visualisierer zeigt derzeit 151 Modelle. Darin enthalten sind neben den
KlassID-Fachmodellen auch Wagtail-, Authentifizierungs-, Sitzungs- und weitere
Frameworkmodelle. Diese technischen Modelle sind nicht automatisch ein
Hinweis auf fachliche Unordnung.

Die wesentliche fachliche Auffälligkeit liegt im eigenen Code:

- `core` bündelt derzeit 41 Modelle aus sehr unterschiedlichen Bereichen.
- `webuntis` bündelt Zugang, Importdaten, Abwesenheiten und Synchronisation.
- Rollen, Familienbeziehungen, Modulfreigaben und technische Adapter sind noch
  nicht überall als durchgängige fachliche Kette sichtbar.
- Einige Modelle sind bereits gute fachliche Bausteine, andere sind Übergangs-
  oder Betriebsmodelle und sollten nicht direkt als Benutzerfunktion gelesen
  werden.

Die erste Bereinigung muss deshalb zunächst ordnen und benennen. Löschen oder
Zusammenführen erfolgt erst nach Daten- und Abhängigkeitsprüfung.

## 1.1 Verbindliches Format jeder weiteren Modellbesprechung

Jede Besprechung startet künftig mit einer technischen Ist-Liste in diesem
Format:

```text
Modell: app_label.ModelName

Vorhandene Felder
| Name | Django-Feldtyp | Pflicht/optional | Null erlaubt | aktuelle Bedeutung |

Aktuelle Beziehungen
| Relation | Richtung | Zielmodell | Kardinalität | related_name |

Danach:
- fachliche Korrekturen;
- neue oder zu entfernende Felder;
- Primary-Key-Entscheidung;
- geplante Relationen und Abhängigkeiten;
- Rollen, Gültigkeit, Audit und Löschung;
- offene Punkte.
```

Die Ist-Liste wird aus dem tatsächlich registrierten Django-Modell geprüft und
nicht aus einer älteren Dokumentation übernommen. Fachliche Arbeitsnamen und
konkrete spätere Python-/Django-Namen werden getrennt gekennzeichnet.

## 1.2 Beispiel: aktuelles Modell `core.School`

### Modellname

`core.School`

### Vorhandene Felder

| Feld | Django-Typ | Pflicht/optional | Vorläufige Bedeutung |
|---|---|---|---|
| `id` | `BigAutoField` | technisch automatisch | aktueller Primary Key |
| `source_id` | `CharField` | optional | externe Quell-ID |
| `source_name` | `CharField` | optional | Herkunftsbezeichnung |
| `source_imported_at` | `DateTimeField` | optional | Importzeitpunkt |
| `name` | `CharField` | Pflichtfeld | Schulname |
| `search_name` | `CharField` | technisch geführt | normalisierte Suche |
| `short_name` | `CharField` | optional | Kurzname |
| `slug` | `SlugField` | optional | URL-/technischer Schlüssel |
| `address` | `CharField` | optional | Anschrift |
| `address2` | `CharField` | optional | zusätzlicher Anschriftsteil |
| `postal_code` | `CharField` | optional | Postleitzahl |
| `city` | `CharField` | optional | Ort |
| `federal_state` | `CharField` | optional | Bundesland |
| `website` | `URLField` | optional | Website |
| `email` | `EmailField` | optional | offizielle E-Mail |
| `school_type` | `CharField` | optional | Schulart |
| `legal_status` | `CharField` | optional | rechtlicher Status |
| `provider` | `CharField` | optional | Träger/Anbieter |
| `fax` | `CharField` | optional | Faxnummer |
| `phone` | `CharField` | optional | Telefonnummer |
| `director` | `CharField` | optional | Leitung als Textfeld |
| `source_raw` | `JSONField` | optional | unverarbeitete Quelldaten |
| `latitude` | `DecimalField` | optional | Geokoordinate |
| `longitude` | `DecimalField` | optional | Geokoordinate |
| `location_valid` | `BooleanField` | Pflichtfeld | Standortprüfung |
| `possible_duplicate_group` | `CharField` | optional | Duplikatprüfung |
| `logo` | `ImageField` | optional | Schullogo |
| `enabled_features` | `JSONField` | Pflichtfeld technisch | aktuelle Feature-Freigaben |
| `visible_menu_items` | `JSONField` | Pflichtfeld technisch | aktuelle Menüfreigaben |
| `is_active` | `BooleanField` | Pflichtfeld | aktive Nutzung |
| `created_at` | `DateTimeField` | automatisch | Erstellung |
| `updated_at` | `DateTimeField` | automatisch | letzte Änderung |

### Aktuelle Beziehungen

| Relation | Zielmodell | Kardinalität | Aktueller Zweck |
|---|---|---|---|
| `registrationapplication` | `core.RegistrationApplication` | eine Schule zu vielen Anträgen | Registrierungsbezug |
| `classes` | `core.SchoolClass` | eine Schule zu vielen Klassen | Schulklassen |
| `branding_assets` | `core.BrandingAsset` | eine Schule zu vielen Assets | Branding |
| `portalconfigurationvalue` | `core.PortalConfigurationValue` | eine Schule zu vielen Werten | Konfigurationsüberschreibungen |
| `portalmoduleoverride` | `core.PortalModuleOverride` | eine Schule zu vielen Overrides | Modulfreigaben |
| `logorequest` | `core.LogoRequest` | eine Schule zu vielen Anfragen | Logo-Prozess |
| `roleassignment` | `core.RoleAssignment` | eine Schule zu vielen Zuweisungen | schulbezogene Rollen |
| `timegrid` | `schedule.TimeGrid` | eine Schule zu vielen Zeitrastern | Stundenplanzeiten |
| `portal_adapters` | `portal_adapters.PortalAdapter` | eine Schule zu vielen Adaptern | Schulportalquellen |

### Erste fachliche Beobachtung

`core.School` enthält aktuell Stammdaten, Importherkunft, Geodaten, Branding,
Feature-/Menüfreigaben und Aktivierungsstatus in einem Modell. Das ist eine
Beobachtung für die weitere Diskussion, noch keine Entscheidung zur Aufteilung.
Insbesondere `enabled_features` und `visible_menu_items` müssen später gegen
das geplante fachliche Modul- und Rechte­modell geprüft werden.

## 2. Inventarisierungsregeln

Jedes Modell wird nach denselben Fragen bewertet:

1. Welche fachliche Aussage speichert es?
2. Wem gehört der Datensatz: Konto, Person, Familie, Kind, Schule oder Modul?
3. In welchem Gültigkeits- und Sichtbarkeitsbereich gilt er?
4. Ist es Stammdaten, Konfiguration, Importdaten, Verlauf oder Audit?
5. Welche Rolle darf lesen, ändern, bestätigen oder verwalten?
6. Welche anderen Modelle sind zwingend erforderlich?
7. Ist es ein Zielmodell, ein Übergangsmodell oder nur technische Infrastruktur?

Bewertung:

- **behalten**: fachlich klar und in der Zielstruktur plausibel;
- **ordnen**: sinnvoll, aber im falschen oder zu breiten Modul;
- **prüfen**: Überschneidung, unklare Zuständigkeit oder Übergang;
- **ablösen**: nur nach definierter Migration und Abnahme.

## 3. Priorität 1 – Identität, Familie und Zugriff

Diese Gruppe wird zuerst besprochen, weil alle späteren Schul-, Adapter- und
Modulabfragen daran hängen.

| Modell | Fachliche Bedeutung | Erste Bewertung |
|---|---|---|
| `UserAccount` | Anmeldekonto und Authentifizierungszustand | behalten; vom Personenprofil trennen |
| `Person` | reale Person mit Profildaten und Sichtbarkeiten | behalten; zentrale Personenbasis |
| `Household` | Familien-/Haushaltskontext | behalten; allein keine Berechtigung ableiten |
| `StudentProfile` | kindbezogene Fachdaten | behalten; an `Person` anbinden |
| `GuardianChildRelationship` | geprüfte Beziehung zwischen erwachsener Person und Kind | behalten; zentrale Zugriffskante |
| `RoleAssignment` | Rolle in einem konkreten Kontext | behalten; Scope und Modulrechte schärfen |
| `ClassMembership` | zeitlich gültige Zugehörigkeit eines Kindes/einer Person zu einer Klasse | behalten; vor jedem geschützten Zugriff prüfen |
| `FamilyChildAccount` | technische Kinderkonto-/Einladungszuordnung | prüfen; Abgrenzung zu `StudentProfile` und `UserAccount` dokumentieren |
| `FamilyAccessCode` | Familienbezogener Aktivierungs-/Zugangscode | prüfen; nicht mit Berechtigung verwechseln |
| `FamilyRegistrationRequest` | Antrag zur Familien-/Personenaufnahme | behalten; Prozessmodell, kein dauerhaftes Profil |
| `ChildJoinRequest` | Antrag zur Zuordnung eines Kindes | behalten; Prozessmodell |
| `RegistrationApplication` | Registrierungsantrag | prüfen; Überschneidung mit den beiden spezifischeren Anträgen |
| `Invitation` | einmalige Einladung | behalten; Prozess-/Sicherheitsmodell |
| `ActivationGrant` | zeitlich begrenzte Aktivierungsfreigabe | behalten; Ablauf und Zweck präzisieren |
| `AccountDeletionRequest` | beantragte Kontolöschung | behalten; mit Aufbewahrung und Audit verbinden |
| `DepartureRetentionCase` | Aufbewahrung nach Austritt | behalten; Betriebs-/Datenschutzmodell |

### Vorläufige fachliche Leitentscheidung

Eine Person, ein Haushalt oder ein gleicher Nachname erzeugt keinen Zugriff
auf ein Kind. Der Zugriff entsteht nur aus einer aktiven, geprüften Beziehung
oder einer ausdrücklich vergebenen kindbezogenen Berechtigung.

Damit sind insbesondere diese Fälle abbildbar:

- Mutter mit Zugriff auf Kind 1 und Kind 2;
- Vater nur mit Zugriff auf Kind 2;
- neuer Lebensgefährte nur mit ausdrücklich zugewiesenem Zugriff auf Kind 1;
- Großeltern oder Pflegepersonen mit ausgewählten Modulen statt Vollzugriff.

Die Rolle `Erziehungsberechtigte` darf dabei nicht pauschal für den gesamten
Haushalt gelten. Sie muss immer für Person, Kind und Geltungsbereich wirksam
sein. Rollenrechte und Modulrechte bleiben getrennt.

## 4. Priorität 2 – Schule, Klasse und Schuljahr

| Modell | Fachliche Bedeutung | Erste Bewertung |
|---|---|---|
| `School` | Schule als Institution | behalten |
| `SchoolClass` | konkrete Klasse | behalten; Anzeige- und technischer Code trennen |
| `SchoolYear` | Schuljahr und Gültigkeitszeitraum | behalten |
| `ClassDomain` | Domain-/Klassenkontext | prüfen; technische Domain von fachlicher Klasse trennen |
| `BrandingAsset` | Logo, Bild oder Branding-Ressource | behalten; Eigentum und Sichtbarkeit klären |
| `SchoolClass` + `SchoolYear` | Klassenkontext | zusammengesetzter fachlicher Scope für viele Module |

Adapter- und Modulfunktionen dürfen nicht global aus einer Schule kopiert
werden. Maßgeblich ist die konkrete Zuordnung:

```text
Kind → aktive Klassenmitgliedschaft → Schule/Schuljahr
     → fachliche Funktion → ausgewählte Adapterquelle → Modulrechte der Rolle
```

## 5. Priorität 3 – Fachliche Module und Datenquellen

| Bereich | Aktuelle Modelle | Erste Einordnung |
|---|---|---|
| Schuladapter | `PortalAdapter`, `PortalAdapterModule`, `ChildModuleConnection`, `SchoolmanagerConnection` | fachliche Quelle, Funktionsfreigabe und technische Verbindung noch klarer trennen |
| WebUntis | `WebUntisConnection`, `WebUntisFeaturePreference`, `WebUntisLesson`, `WebUntisHomework`, `WebUntisAbsence`, `AbsenceDraft`, `AbsenceSubmission`, `HomeworkProgress`, `SyncSchedule`, `SyncRun`, `WebUntisSubjectMapping`, `WebUntisTeacherMapping`, `WebUntisCalendarSubscription` | sinnvoller Kern, aber Zugangsscope Familie/Kind und fachliche Funktion explizit machen |
| Kalender/Stundenplan | `TimeGrid`, `LessonPeriod`, `SchoolBreak`, `TimetableEntry`, `CalendarEntry`, `CalendarChange`, `CalendarDelivery`, `ICalSubscription` | fachliche Anzeige von Import- und Lieferprotokoll trennen |
| itslearning | `ItslearningConnection`, `ItslearningCourse`, `ItslearningUpdate`, `ItslearningCalendarItem`, `WebDavSpace` | eigenes Adaptermodul; gleiche Funktionsbegriffe wie Stundenplan/Hausaufgaben verwenden |
| Speiseplan | `MealPlan`, `MealDay`, `MealOption` | eigenständiges Fachmodul |
| Inhalte | `ProtectedDocument`, `TeacherProfile`, `Post`, `Comment`, `CommentReport` | eigenständiges Fachmodul; Klassen- und Moderationsrechte prüfen |
| Veranstaltungen | `Event`, `ContributionCategory`, `ContributionItem`, `Reservation`, `EventParticipation`, `ReminderDelivery`, `EventPoll`, `EventPollOption`, `EventPollVote` | fachlich zusammengehörig; Benachrichtigung als Querschnitt behandeln |
| Chat | `ChatRetentionCategory`, `ChatRoom`, `ChatRoomAccess`, `ChatRoomInvitation`, `ChatMessage`, `ChatReadState`, `ChatStyle`, `ChatSafetyProfile`, `ChatSafetyAppeal`, `ChatReactionPack`, `ChatReactionAsset`, `ChatReaction` | fachlich zusammengehörig; direkte Gespräche sind `ChatRoom` vom Typ `direct`; Jugendschutz-/Filterereignisse und Einsprüche bleiben getrennt nachvollziehbar |
| Mobilität | `MobilityListing`, `MeetingPoint`, `MobilityReaction`, `PickupDisclosure`, `MobilityReport`, `MobilityListingView` | aktuelle Fachgruppe; UI-Ausblendung und Datenlöschung getrennt entscheiden |
| Medien | `Gallery`, `Photo`, `PhotoSubjectDeclaration`, `PhotoReport`, `PhotoModerationDecision` | fachlich klar, Einwilligung und geschützte Auslieferung bleiben Querschnitt |
| Biometrie/Vision | `BiometricCollection`, `BiometricProfile`, `VisionPhotoSubmission`, `BiometricMatch`, `BiometricReference` | eigener sensibler Bereich; standardmäßig deaktiviert |

## 6. Priorität 4 – Querschnitt und Betrieb

| Modellgruppe | Aktuelle Modelle | Einordnung |
|---|---|---|
| Theme/Konfiguration | `PortalTheme`, `PortalConfigurationKey`, `PortalConfigurationValue`, `PortalModule`, `PortalModuleOverride`, `MenuItem` | zentrale Konfiguration; fachliche Modulfreigabe von UI-Menü trennen |
| Einwilligung | `ConsentType`, `ConsentTextVersion`, `ConsentDecision` | eigener Datenschutzbereich |
| Audit | `AuditEvent` | unveränderbarer Sicherheitsnachweis |
| Monitoring | `MonitoringSnapshot`, `MonitoringComponent` | Betrieb/Administration, nicht Nutzerfachlichkeit |
| Push/Benachrichtigung | `PushSubscription`, `PushPreference`, `UserNotification` | Querschnitt; Empfänger aus Policy ermitteln |
| Einstieg/Test | `OnboardingState`, `TutorialState`, `PilotReport` | UI-/Testprozess; nicht in die Kernfamilienmodelle verschieben |
| Branding/Logo | `LogoRequest` | prüfen, ob Prozessmodell oder Brandingverwaltung |

## 7. Erste Strukturhypothese

Die fachliche Struktur sollte langfristig ungefähr so lesbar sein:

```text
Identität
├── Konto
├── Person
├── Familie/Haushalt
├── Kindbeziehung
└── Rollen und Rechte

Schulkontext
├── Schule
├── Schuljahr
├── Klasse
└── Mitgliedschaft

Module
├── Kalender und Stundenplan
├── Hausaufgaben und Lernportale
├── Abwesenheiten
├── Veranstaltungen
├── Chat
├── Inhalte und Medien
└── Speiseplan

Querschnitt
├── Adapterquellen und Synchronisation
├── Benachrichtigungen
├── Einwilligungen
├── Audit
└── Monitoring
```

Das ist eine fachliche Ordnungshypothese, kein Auftrag zur sofortigen
Umbenennung oder Migration der Django-Apps.

## 8. Nächste Besprechungsrunde

Als nächstes sollten wir die Gruppe „Identität, Familie und Zugriff“ Modell für
Modell festlegen. Für jedes Modell entscheiden wir gemeinsam:

- endgültiger fachlicher Name;
- Eigentümer des Datensatzes;
- Pflicht- und optionale Felder;
- Beziehung zu Konto, Person, Familie, Kind und Klasse;
- Rollen-/Modulrechte;
- Status und Gültigkeitszeitraum;
- Entwurf versus aktiv nutzbarer Datensatz;
- Audit-, Lösch- und Migrationsregeln.

Erst danach werden Adapter, Abwesenheiten und die übrigen Module auf diese
Zugriffskette aufgesetzt. So bleibt die Visualisierung ein Prüfwerkzeug und
wird nicht zur Grundlage für vorschnelle technische Umbauten.

## 9. Erweiterbares Betreiber- und Organisationsmodell

### 9.0 Vorgehen bei der Modellbesprechung

Jedes Modell wird künftig in einem festen Raster besprochen und dokumentiert:

| Punkt | Inhalt |
|---|---|
| Fachlicher Zweck | Welche reale Sache oder welcher Prozess wird abgebildet? |
| Eigentümer | Wem gehört der Datensatz fachlich? |
| Primary Key | Identität des Datensatzes, zunächst bevorzugt UUID oder Django-Standard nach Entscheidung |
| Pflichtfelder | Angaben ohne die der Datensatz nicht aktiv werden darf |
| Optionale Felder | Zusatzangaben, die später ergänzt werden können |
| Status/Gültigkeit | Entwurf, aktiv, archiviert, von/bis und gegebenenfalls Prüfstatus |
| Relationen | Verknüpfungen zu anderen Modellen, auch wenn der genaue Fremdschlüssel später festgelegt wird |
| Rechte | Wer darf sehen, anlegen, ändern, freigeben oder löschen? |
| Audit/Löschung | Nachweis, Aufbewahrung und kontrollierte Entfernung |
| Offene Punkte | Bewusst noch nicht entschiedene Eigenschaften |

Die Feldnamen in diesem Dokument sind fachliche Arbeitsnamen. Sie werden erst
nach der gemeinsamen Besprechung in konkrete Django-Felder übersetzt.

### 9.0.1 Plattform versus Fachmodell

Die Plattform ist zunächst der Betreiber- und Deploymentkontext: deine
KlassID-Installation mit ihrem Hauptadministrator. Solange nur eine
Installation betrieben wird, muss daraus kein zusätzliches Geschäftsmodell
`Platform` entstehen. Der Hauptadministrator kann über eine global geltende
Rollen-Zuweisung abgebildet werden.

Für eine spätere Vermarktung bleiben optionale Organisations- oder
Lizenzmodelle möglich. Diese werden nicht vorweggenommen. Ein zukünftiger
`Organization`-Datensatz darf dann Betreiber-, Kunden- oder Trägerbereiche
abbilden, ohne dass `School` oder `SchoolClass` davon abhängig werden.

Der erste konkrete Fachbereich ist daher die Schule.

### 9.0.2 Arbeitsentwurf: `School`

| Feld/Arbeitsname | Bedeutung | Vorläufige Einstufung |
|---|---|---|
| `id` | eindeutige Identität der Schule | Primary Key, UUID vorgeschlagen |
| `name` | offizieller Schulname | Pflichtfeld |
| `short_name` | Kurzname für Navigation und Karten | optional |
| `school_type` | zum Beispiel Gymnasium, Gesamtschule oder Grundschule | optional, kontrollierte Auswahl prüfen |
| `official_identifier` | externe Schulnummer oder Institutionskennung | optional, je Quelle eindeutig wenn vorhanden |
| `address` | schulische Anschrift | optional; Sichtbarkeit und Datenschutz klären |
| `contact_email` | offizielle Kontaktadresse | optional; nicht automatisch für Familien sichtbar |
| `website_url` | öffentliche Website | optional |
| `status` | Entwurf, aktiv, pausiert, archiviert | Pflichtfeld mit Standardwert |
| `valid_from` | Beginn der Gültigkeit im Portal | optional |
| `valid_until` | Ende der Gültigkeit im Portal | optional |
| `created_at` / `updated_at` | technische Zeitpunkte | Pflichtfelder, automatisch |

Vorgesehene Relationen:

```text
School
├── SchoolClass (eine Schule kann viele Klassen haben)
├── SchoolYear / Klassenkontexte
├── PortalAdapter-Zuordnungen
├── schulbezogene Rollen und Modulfreigaben
└── optionale Branding- und Konfigurationswerte
```

Eine Schule erhält nicht automatisch Zugriff auf alle Personen- oder
Familiendaten ihrer Klassen. Die Relation zu Klassen und die Relation zu
berechtigten Verwaltungsrollen sind getrennte fachliche Beziehungen.

### 9.0.3 Vorläufige Relation zur Plattform

Für die erste Betriebsart gilt:

```text
Plattformbetrieb (implizit)
└── mehrere School-Datensätze
    └── mehrere SchoolClass-Datensätze
```

Für spätere Betriebsarten bleibt als Erweiterung offen:

```text
Organization / Kundenbereich (optional)
└── Schools (optional zugeordnet)
    └── SchoolClasses
```

Daraus folgt für die aktuelle Modellbesprechung: `School` wird als
eigenständiges Modell definiert; eine Pflichtrelation zu `Platform` oder
`Organization` wird zunächst nicht festgelegt. Die spätere Relation wird
ergänzt, sobald Betreiber-, Lizenz- oder Mandantenregeln entschieden sind.

### 9.1 Anlass und Zielbild

Das bisherige Modell betrachtet die Familie zu stark als Ausgangspunkt. Für
eine größere Nutzung muss der Einstieg auch von einer Plattform, einer Schule
oder einer einzelnen Klasse aus möglich sein. Die technische Struktur muss
daher mehrere Organisationsformen erlauben, ohne eine davon zwingend
vorzuschreiben.

Vorgesehen ist folgende Hierarchie:

```text
Plattform / Betreiber
├── Schule (optional verwalteter Organisationsbereich)
│   ├── Klasse 5.1
│   │   ├── Klassen-Administratoren
│   │   ├── Content-Manager / Lehrer
│   │   └── Familien und Personen
│   └── Klasse 5.2
│       └── eigene oder gemeinsame schulische Rollen
└── direkte Klassen- oder Pilotbereiche ohne Schul-Administration
```

Eine Schule kann die Plattform selbst verwalten. Sie muss es aber nicht. Eine
Klasse kann direkt durch einen Klassen-Administrator betrieben werden. Mehrere
Klassen derselben Schule können einen gemeinsamen Schul-Administrator haben
oder getrennte Klassen-Administratoren. Diese Organisationsentscheidung darf
nicht im Datenmodell fest verdrahtet werden.

### 9.1.1 Gleichberechtigte Betriebsarten

Das Datenmodell darf keine bestimmte Größe oder Vertriebsform erzwingen. Es
unterstützt mindestens diese Betriebsarten:

| Betriebsart | Beschreibung |
|---|---|
| private Einzelverwaltung | Der Plattformbetreiber verwaltet selbst mehrere Klassen, gegebenenfalls an mehreren Schulen. |
| Klassenbetrieb | Eine einzelne Klasse wird durch einen oder mehrere Klassen-Administratoren betrieben, ohne dass ein Schul-Account erforderlich ist. |
| Schulbetrieb | Eine Schule verwaltet ihre Klassen, Rollen, Einladungen und freigegebenen Module selbst. |
| gemischter Betrieb | Einige Klassen werden durch die Schule, andere durch eigene Klassen-Administratoren oder den Plattformbetreiber verwaltet. |
| späterer Kunden-/Lizenzbetrieb | Ein organisatorischer Kunde erhält einen eigenen Verwaltungsbereich, sofern dies später fachlich und wirtschaftlich entschieden wird. |

Diese Betriebsarten sind Konfiguration und Berechtigungs-Scope, keine
unterschiedlichen Datenmodelle. Eine Klasse muss deshalb immer eigenständig
zuordenbar und verwaltbar bleiben. Eine Schule darf optional übergeordnet
werden, darf aber nicht Voraussetzung für die Existenz einer Klasse sein.

Ebenso darf der Plattformbetreiber mehrere Schulen und Klassen direkt
verwalten, ohne sich selbst als Schul-Administrator jeder einzelnen Schule
anlegen zu müssen. Umgekehrt kann eine Schule ihre Administration vollständig
selbst übernehmen, ohne Zugriff auf andere Schulen oder Klassen zu erhalten.

### 9.2 Rollen sind kontextbezogen

Eine Rolle gehört nicht pauschal zu einem Benutzerkonto. Sie gilt immer in
einem bestimmten Geltungsbereich und mit einer konkreten Funktion.

| Ebene | Beispiele für Rollen | Geltungsbereich |
|---|---|---|
| Plattform | Hauptadministrator, Betreiber, Support | gesamte Plattform |
| Schule | Schul-Administrator, Schulleitung, schulischer Content-Manager | eine Schule und ihre Klassen |
| Klasse | Klassen-Administrator, Klassen-Content-Manager, Lehrer | eine konkrete Klasse |
| Familie | Erziehungsberechtigte, Pflegeperson, weitere berechtigte Person | Haushalt und ausdrücklich zugewiesene Kinder |
| Person | Kind, erwachsene Person, Lehrerprofil | persönliche Identität; keine automatische Organisationsberechtigung |

Ein Lehrer kann beispielsweise gleichzeitig Lehrer in einer Klasse,
Klassen-Administrator in einer anderen Klasse und Content-Manager für eine
Schule sein. Diese drei Funktionen werden als getrennte Zuweisungen mit
unterschiedlichen Rechten gespeichert.

Für eine Zuweisung werden mindestens benötigt:

- Person bzw. Benutzerkonto;
- Rolle;
- Geltungsbereich (`Plattform`, `Schule`, `Klasse` oder `Familie`);
- konkrete Objekt-ID des Geltungsbereichs;
- erlaubte Aktionen bzw. Module;
- Status und Gültigkeitszeitraum;
- Einladungs-, Prüf- und Auditinformationen.

Damit kann der Plattformbetreiber die Gesamtverwaltung behalten, ohne dass
ein Klassen-Administrator automatisch auf andere Klassen oder Familien
zugreifen darf.

### 9.3 Initialer Einstieg über den ersten Erwachsenen

Der initiale Familienprozess startet künftig nicht bei einem Schüler, sondern
bei einem ersten erwachsenen, verifizierten Erziehungsberechtigten:

```text
Einladung oder Initialzugang
→ erster Erwachsener bestätigt E-Mail und richtet sein Konto ein
→ persönliche Pflichtangaben vollständig erfassen
→ Familie/Haushalt anlegen oder einer Familie zuordnen
→ Kinder und weitere Erwachsene direkt erfassen oder einladen
→ Beziehungen, Rollen und Kindzuordnungen festlegen
→ erst danach fachliche Module und Adapter einrichten
```

Der erste Erwachsene darf weitere Personen selbst erfassen oder einen
persönlichen Einladungslink senden. Eine Person, die sich über einen gültigen,
persönlich adressierten Link anmeldet und die Einladung bestätigt, benötigt
keine zusätzliche manuelle Freigabe durch den Hauptadministrator.

Das ersetzt aber nicht die technische Identitätsprüfung: Einladungslinks
bleiben einmalig, gehasht, zeitlich begrenzt und einem Zweck sowie möglichst
einem Empfänger zugeordnet. „Keine manuelle Freigabe“ bedeutet daher nicht
„keine Verifizierung“.

### 9.4 Einladungsarten

Das Einladungsmodell muss mehrere Wege unterstützen, ohne unterschiedliche
Identitätsmodelle zu erzeugen:

| Einladungsweg | Ziel | Ergebnis |
|---|---|---|
| persönlicher E-Mail-Link | Erwachsener, Kind, Lehrer oder Administrator | Empfänger vervollständigt eigenes Konto |
| QR-Code | Papier-/Vor-Ort-Einladung, optional mit Zielklasse | Empfänger öffnet denselben sicheren Einladungsprozess |
| manuelle Erfassung durch berechtigten Admin | Person ohne eigene technische Vorbereitung | Datensatz als Entwurf; persönlicher Login kann später übernommen werden |
| Import einer Schulliste | viele Schüler-/Kontaktstammdaten | validierte Entwürfe; Einladungen werden anschließend gezielt versendet |

Ein QR-Code ist nur eine andere Transportform desselben einmaligen
Einladungstokens. Er darf keine pauschale Klassenberechtigung enthalten.

### 9.5 Schule und Klassen als selbstständige Betreiberbereiche

Für die spätere Vermarktung oder Bezahlmodelle muss die Plattform einen
verantwortlichen Bereich abbilden können. Dafür werden organisatorische
Zuweisungen von Fachrollen getrennt:

```text
Organisation / Scope
    → welche Schule oder Klasse wird verwaltet?

Rolle
    → welche Funktion hat die Person dort?

Modulrecht
    → welche fachlichen Module und Aktionen sind erlaubt?

Datenbeziehung
    → welche Familien, Kinder oder Inhalte darf die Person sehen?
```

Ein Schul-Administrator erhält nicht automatisch Einsicht in private
Familienfelder. Ein Klassen-Administrator darf Klasseninhalte und
Konfiguration verwalten, aber nicht automatisch private Familien- oder
Gesundheitsdaten. Umgekehrt erhält ein Erziehungsberechtigter keine
Administrationsrechte, nur weil er einer Klasse angehört.

### 9.6 Vorläufige Datenmodell-Erweiterung

Für dieses Zielbild sind fachlich voraussichtlich eigene Modelle oder klar
getrennte Modellbereiche erforderlich:

| Baustein | Zweck |
|---|---|
| `Organization` | optionale Schule bzw. spätere Träger-/Kundenorganisation |
| `OrganizationMembership` | Person/Benutzerkonto in einer Organisation |
| `Scope` oder eindeutige Scope-Zuweisung | Plattform, Schule, Klasse oder Familie als Berechtigungsbereich |
| `ScopedRoleAssignment` | Rolle plus Scope plus Gültigkeit |
| `ModulePermission` | sichtbare, lesbare, nutzbare, schreibbare oder bestätigende Aktion |
| `Invitation` mit Zieltyp | sicherer Einstieg für Erwachsenen-, Kinder-, Lehrer- und Admin-Konten |
| `ImportBatch` | nachvollziehbarer Import von Schul-/Klassenlisten |
| `InvitationDelivery` | E-Mail-, QR- oder sonstiger Versandnachweis |

Die bestehenden Modelle `RoleAssignment`, `Invitation`, `FamilyRegistrationRequest`
und `FamilyChildAccount` werden gegen diese Zielbausteine geprüft. Es ist noch
nicht entschieden, ob sie erweitert, aufgeteilt oder schrittweise ersetzt
werden. Eine Migration erfolgt erst nach der gemeinsamen Entscheidung über
Rollen, Scopes und Einladungsabläufe.

### 9.1.2 Einordnung von Lehrkräften

Eine Lehrkraft ist keine eigene Bereichsebene und gehört nicht automatisch zu
einer Familie. Sie ist eine `Person` mit eigenem Benutzerkonto und kann
optional ein ergänzendes `TeacherProfile` besitzen.

Für den ersten Livegang werden keine aktiven Lehrer-Logins vorausgesetzt.
Die technische Möglichkeit für eine spätere `Teacher`-Rolle und ein eigenes
Lehrerkonto bleibt vorbereitet, wird aber erst aktiviert, wenn Lehrkräfte
tatsächlich online teilnehmen sollen.

Die Funktion der Lehrkraft wird über eine kontextbezogene Rollen-Zuweisung
abgebildet:

```text
Person / Benutzerkonto
└── Rollen-Zuweisung
    ├── Lehrer in Klasse 5.1
    ├── Klassen-Admin in Klasse 5.1 (optional)
    └── Content-Manager für Schule A (optional)
```

Damit kann eine Klasse auch ohne Schul-Administration betrieben werden. In
diesem Fall wird die Lehrkraft direkt der Klasse zugewiesen. Wenn eine Schule
später selbst verwaltet, kann dieselbe Lehrkraft zusätzlich eine schulweite
Rolle oder Rollen in mehreren Klassen erhalten.

In einer Klasse existieren damit unterschiedliche Personengruppen:

- Kinder als Schüler mit Klassenmitgliedschaft;
- Erwachsene als Familienmitglieder mit kindbezogenen Beziehungen;
- Lehrkräfte mit Lehrerrollen für die Klasse oder Schule;
- Administratoren oder Content-Manager mit zusätzlichen Verwaltungsrechten.

Diese Gruppen sind keine starren exklusiven Typen. Eine Person kann mehrere
Rollen besitzen, zum Beispiel Lehrkraft und Klassen-Administrator. Die Rechte
werden trotzdem getrennt ausgewertet. Eine Lehrerrolle erzeugt insbesondere
keinen Zugriff auf private Familiendaten und keine Elternrechte.

Die konkrete Ausgestaltung des Lehrermodells wird ausdrücklich zurückgestellt.
Für die Grundstruktur genügt zunächst:

- Lehrkräfte sind als Personen und Benutzerkonten andockbar;
- eine Lehrkraft kann einer Schule, mehreren Schulen und mehreren Klassen
  zugewiesen werden;
- Vertretungen oder kurzfristige Einsätze werden später über zeitlich
  begrenzte Klassen-/Schulzuweisungen abgebildet;
- das spätere `TeacherProfile` darf diese Grundstruktur ergänzen, aber nicht
  voraussetzen, dass jede Lehrkraft nur an einer Schule tätig ist.

### 9.7 Offene Entscheidungen vor der Umsetzung

Vor einer technischen Änderung müssen wir noch festlegen:

1. Wird das zurückgestellte Organisations-/Mandantenmodell nach dem ersten
   Livegang als eigene Ausbaustufe aufgenommen?
2. Welche Rollen darf eine Schule später selbst vergeben, welche nur der
   Plattformbetreiber?
3. Darf ein künftiger Klassen-Administrator Familien einladen oder nur der
   erste Erwachsene?
4. Welche Einladungen dürfen per QR-Code verteilt werden und wie werden sie
   vor Missbrauch geschützt?
5. Welche Module und Aktionen sind Standardbestandteil der jeweiligen Rolle?

Diese Fragen gehören vor die Detailinventarisierung der Familienfelder, weil
ihre Antworten festlegen, welche Beziehungen und Rollen dort gespeichert
werden müssen.
