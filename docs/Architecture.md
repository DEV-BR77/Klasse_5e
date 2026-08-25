# Architektur und Bestandsaufnahme

Stand: 25.08.2026. Die Prüfung war statisch und lesend; produktive Daten,
Geheimnisse und Dienste wurden nicht geöffnet oder verändert.

## Bestand

| Projekt | Technik und Daten | Auth/Betrieb | Tests | Verwertbarkeit und Schulden |
|---|---|---|---|---|
| `Klasse_5e` | Zu Beginn leer, kein Git-Repository | keine | keine | Zielrepository; Phase 0 erzeugt nur Dokumentation. Vor Phase 1 Git initialisieren und Schutzdateien festlegen. |
| `The-Life-of-Mila` | Privates Sammelprojekt; Python 3.12, statisches Web-Frontend, Nginx, OpenCV/Numpy/Pillow; Timeline-Dateidaten und Vision-JSON | Bilder-Check publiziert aktuell Port 80; die produktive Python-API besitzt keine erkennbare Request-Authentisierung | ein Timeline-Testmodul; keine Vision-Tests | Human-in-the-loop-Ablauf und HEIC/EXIF-orientierte Bilddekodierung sind Referenzen. Monolithischer Server, JSON-Persistenz, projektbezogene Namen/IDs, globale Threads und direkte Dateipfade werden nicht übernommen. Repository enthält zahlreiche nicht eingecheckte Änderungen und bleibt unberührt. |
| `Bilder-Check-Mehrfachzuordnung` | Ein-Datei-HTTP-Server plus HTML/JS; Haar-Kaskade zur Erkennung, LBPH aus `opencv-contrib` zum Vergleich; Gesichtscrops, Referenzen, Status und Jobs als JSON/Dateien | `ThreadingHTTPServer` auf `0.0.0.0:8000`; Größenlimit und Pfadnormalisierung vorhanden, aber keine Collection-Grenze, Dienstauthentisierung oder umfassende Lösch-API | keine automatisierten Tests gefunden | Wiederzuverwenden ist der fachliche Ablauf: erkennen → vorschlagen → Mensch bestätigt/verwirft → bestätigter Treffer kann Referenz werden. Nicht wiederzuverwenden sind Server- und Persistenzarchitektur. |
| `EventMonitorAI` | FastAPI, SQLAlchemy, Pydantic, PostgreSQL produktiv/SQLite lokal, schlichtes JS, Service Worker, `pywebpush`; Compose mit App, Website, PostgreSQL, Speaker-Worker und Backup | signierte Bearer-Tokens, PBKDF2, Tenant-Mitgliedschaft; VAPID aus Umgebung; Caddy extern | 41 Testmodule, darunter Push-Aktions-/Tokenfluss, aber keine isolierten Versand-/404-/410-Tests | Technischer VAPID-Versand, Subscription-Daten und Stale-Endpoint-Erkennung sind gute Referenzen. Versand ist an Event/User/Tenant-Modelle und Lärm-Payload gekoppelt; Browser bietet Aktivierung, aber keine explizite Abmeldung. Keine Migration in Phase 1A. |
| `PDF-SmartForms-Studio` | Vorliegend ist eine gebaute Windows-Distribution, keine vollständige Quellarbeitskopie; Python 3.12, PyQt6, PyMuPDF und Pillow sind im Bundle sichtbar; lokale JSON-Profile/Templates | lokale Desktop-App, keine Web-Authentisierung oder Docker-Struktur | in dieser Distribution keine Testquellen gefunden; README nennt pytest/ruff/black/mypy im Quellprojekt | Datenschutz-, Human-in-the-loop-, PDF-Analyse- und Template-Konzepte sind fachliche Referenzen. Binärcode und Desktop-UI sind nicht übernehmbar; für Phase 3 wird eine dokumentierte PDF-Schnittstelle neu gebaut. |
| `HomeInfrastructure` | Caddy 2.10.2, gemeinsame externe Docker-Netze und persistente Caddy-Volumes | globale Ports 80/443, verwaltete Caddy-Fragmente; Docker Desktop, spätere NAS-/Home-Server-Migration | keine automatisierten Tests gefunden | Gemeinsamer HTTPS-Einstieg wird genutzt. Klasse 5e erhält später nur ein verwaltetes Route-Fragment und hängt am externen `home-proxy`-Netz; Caddy wird nicht im App-Compose dupliziert. Aktuell breite Tailscale-Regel ist ein dokumentiertes Betriebsrisiko. |

## Push-Prüfung

Der EventMonitor-Versand liest Subscriptions, erstellt eine JSON-Nachricht und
ruft `pywebpush.webpush` mit VAPID-Private-Key und Subject auf. Antworten 404
oder 410 markieren Endpunkte als ungültig und löschen sie nach dem Versand.
Inaktive oder fehlende Benutzer werden ebenfalls bereinigt.

Das Modell speichert `endpoint`, `p256dh`, `auth`, Benutzerbezug und
Erstellungszeit; der Endpoint ist global eindeutig. Die API legt an oder
aktualisiert eine Subscription für den angemeldeten Benutzer. Der Browser
registriert `/sw.js`, übernimmt bestehende Subscriptions und kann nach
Notification-Freigabe abonnieren. Der Service Worker zeigt EventMonitor-
spezifische Aktionen und sendet signierte Antworten zurück.

Lücken vor Wiederverwendung:

- technische DTOs und Versand müssen ohne ORM-, User-, Tenant- und Eventmodell
  funktionieren;
- explizite Abmeldung auf Browser und Server fehlt;
- `pushsubscriptionchange` und Geräte-/Kategorie-Metadaten sind nicht behandelt;
- Fehlerklassen neben 404/410 sowie Retry/Timeout-Verhalten brauchen einen
  klaren Vertrag;
- Payload, Klickziel, Datenschutzstufe und Aktionen brauchen ein neutrales,
  größenbegrenztes Schema;
- isolierte Tests für Payload, Versand und Stale-Endpoint-Ergebnis fehlen.

## Vision-Prüfung

Die produktive Mila-API und der Bilder-Check enthalten im Wesentlichen
denselben Ansatz: ein OpenCV-Haarmodell erkennt frontale Gesichter, Ausschnitte
werden lokal gespeichert und ein bei jedem Lauf aus Startreferenzen und
bestätigten Ausschnitten trainiertes LBPH-Modell liefert Distanzen. Niedrigere
LBPH-Distanz bedeutet größere Ähnlichkeit. Vorschläge bleiben offen, bis ein
Mensch sie bestätigt; Einzel- und Mehrfachprüfung sind vorgesehen. Daemon-
Threads führen Scan und Klassifikation im Webprozess aus; Status, Referenzen,
Gesichter und Jobs werden atomar in JSON-Dateien geschrieben.

Haar/LBPH ist CPU-sparsam und als Baseline wertvoll, aber für wechselnde
Pose, Licht, Alter, Teilverdeckung und Gruppenbilder voraussichtlich nicht
zuverlässig genug, um ohne Vergleichsmessung als Zielmodell festgelegt zu
werden. Phase 1B muss daher zuerst einen reproduzierbaren, manuell annotierten
Vergleichsdatensatz und Kennzahlen für Erkennung sowie Kandidaten-Ranking
definieren. Ein moderneres lokales CPU-Modell darf erst nach Lizenz-, Größen-,
Latenz- und Qualitätsvergleich gewählt werden. Es bleibt stets ein
Vorschlagssystem.

## Zielarchitektur

```text
Browser/PWA
    |
    | HTTPS
    v
globaler Caddy (HomeInfrastructure)
    |
    v
Django + Wagtail (modularer Monolith) ---- PostgreSQL
    |          |                          (alle Fachdaten)
    |          +---- geschützte lokale Medien
    |
    +---- internes Python-Push-Kit ---- Browser-Pushdienste
    |
    +---- internes Docker-Netz ---- lokale Vision-API ---- eigener robuster Store
                                       (ab Phase 1B; Nutzung erst Phase 6)
```

Die Browser-Pushdienste sind technisch unvermeidbare externe Zusteller; die
Fachanwendung übermittelt standardmäßig keine sensiblen Inhalte. Die
Vision-API hat keinen veröffentlichten Host-Port und keinen Internetbedarf.

## Modulgrenzen des Monolithen

| Modul | Verantwortet | Darf abhängen von |
|---|---|---|
| `accounts` | Einladung, Konto, starke Anmeldung, Sitzungen | `audit` |
| `classes` | Schuljahr, Klasse, Rollen, aktive Mitgliedschaften | `accounts`, `audit` |
| `families` | Person, Haushalt, Sorgeberechtigte, Kinderbeziehungen | `accounts`, `classes`, `audit` |
| `consents` | Typ, Textversion, Zweck, Empfänger, Status, Widerruf | `families`, `accounts`, `audit` |
| `core` | Dashboard, Navigation, gemeinsame Zugriffspolicies | öffentliche Schnittstellen der obigen Module |
| `content` | geschützte Dokumente, Lehrerprofile, Beiträge, Kommentare | `classes`, `consents`, `audit` |
| `events` | Events und transaktionssichere Mitbringlisten | `classes`, `content`, `notifications`, `audit` |
| `media` | Upload, Metadatenentfernung, Moderation, geschützte Auslieferung | `classes`, `consents`, `events`, `audit` |
| `vision` | Fachadapter und opaque ID-Zuordnung; keine Erkennung im Monolithen | `media`, `families`, `consents`, `audit` |
| `chat` | Räume, Nachrichten, Moderation, Aufbewahrung | `classes`, `events`, `notifications`, `audit` |
| `calendar` | manueller Plan, Änderungen, iCal-Tokens | `classes`, `events`, `notifications`, `audit` |
| `portal_adapters` | spätere externe Schulportaladapter | nur neutrales `calendar`-Importinterface |
| `notifications` | Präferenzen und Empfängerauswahl; Aufruf des Push-Kits | `accounts`, `classes`, `consents` |
| `audit` | append-orientierte sicherheitsrelevante Ereignisse | keine Fachmodule |

Fachmodule greifen nicht auf interne Tabellen anderer Module zu, sondern auf
kleine Service-/Policy-Schnittstellen. Das ist eine Codegrenze innerhalb eines
Django-Prozesses, kein Netzwerkdienst.

### Verbindliches Familien- und Schülermodell ab Phase 2

Ein Schüler ist eine eigene `Person` mit `StudentProfile` und aktiver
Klassenmitgliedschaft; im MVP ist dafür kein eigenes Benutzerkonto nötig.
Sorgeberechtigte besitzen stets getrennte persönliche Benutzerkonten. Geteilte
Familienlogins, gemeinsame Passwörter und Identitätsübernahme eines
Kinderkontos sind ausgeschlossen.

Zugriff auf ein Schülerprofil folgt ausschließlich aus einer bestätigten,
zeitlich gültigen `GuardianChildRelationship`, niemals allein aus einem
gemeinsamen Haushalt. Sie enthält mindestens `guardian_person_id`,
`student_person_id`, `relationship_type`, `is_legal_guardian`, getrennte Rechte
für Ansicht, Profilverwaltung sowie allgemeine, Foto- und biometrische
Einwilligungen, `valid_from`, `valid_until`, `status`, `verified_by` und
`verified_at`. Damit bleiben getrennte Haushalte, mehrere Sorgeberechtigte,
mehrere Kinder und sonstige autorisierte Bezugspersonen modellierbar.

Jede Handlung speichert das tatsächlich authentisierte Benutzerkonto. Eine
sichtbare Familienbezeichnung wird nur aus verifizierten Beziehungen abgeleitet
und nie als frei behauptbarer Text gespeichert. Profilfreigaben steuern, ob
Elternname, Beziehung und Schülerbezug sichtbar sind; Moderation und Audit
behalten unabhängig davon den wirklichen Actor. Einwilligungsentscheidungen
mehrerer Sorgeberechtigter bleiben einzeln. Fehlt bei besonders sensibler
Verarbeitung die erforderliche eindeutige Zustimmung, ist sie widersprüchlich
oder widerrufen, darf sie nicht starten beziehungsweise muss gestoppt werden.

## Kerndaten und externe Verträge

Phase 2 verwendet mindestens `User`, `Invitation`, `Person`, `Household`,
`GuardianChildRelationship`, `SchoolYear`, `Class`, `ClassMembership`,
`RoleAssignment`, `ConsentType`, `ConsentTextVersion`, `ConsentDecision` und
`AuditEvent`. Zugriffsentscheidungen verlangen aktives Konto, aktive
Mitgliedschaft und passende Rolle oder Objektberechtigung. Widerruf wird direkt
aus dem aktuellen Entscheidungsdatensatz geprüft, nicht aus einem Cache.

Das Push-Kit erhält ein neutrales Subscription-DTO und ein Payload mit
`title`, `body`, `url`, `category`, optionalen neutralen Aktionen und stabiler
Nachrichten-ID. Es gibt ein Ergebnis je Endpoint (`delivered`, `stale`,
`temporary_failure`, `permanent_failure`); nur die Anwendung löscht ihren
Datensatz anhand dieses Ergebnisses.

### Konkrete Phase-1A-Paketstruktur

```text
packages/web-push-kit/
├── pyproject.toml
├── src/web_push_kit/       # DTOs, VAPID-Konfiguration, Sender und Ergebnisse
├── tests/                  # frameworkneutrale Python-Tests
├── browser/                # ES-Modul-Helfer und kopierbarer Classic Worker
└── browser/tests/          # Tests mit dem eingebauten Node-Testläufer
```

Der Distributionsname ist `klasse5e-web-push-kit`, der Python-Import folgt mit
`web_push_kit` der üblichen Unterstrichkonvention. Ein injizierbarer Transport
hält Sendertests ohne Netz und echte Schlüssel deterministisch. Das Paket
persistiert und löscht nichts: 404/410 wird als `stale`, temporäre HTTP-/
Transportfehler als `temporary_failure`, andere Ablehnungen als
`permanent_failure` und Erfolg als `delivered` zurückgegeben. Browser-Code
erhält Anwendungs-Callbacks statt fester API-Routen.

Die Vision-API verwendet ausschließlich opaque IDs: `collection_id`,
`image_id`, `face_id`, `subject_id`, `reference_id`, `match_id`, `job_id`.
Jede Tabelle und jeder Zugriff trägt `collection_id`; collection-übergreifende
Queries und Trainingsläufe sind verboten und werden getestet. Originalbilder
bleiben in der Fachanwendung. Löschoperationen existieren für Bild, Subject und
Collection und umfassen Crops, Vergleichsdaten, Referenzen, Matches und Jobs.

## Betrieb und Sicherheit

- Django-Sessions nutzen sichere, HttpOnly- und SameSite-Cookies; CSRF bleibt
  aktiv. Administratoren benötigen Passkey oder TOTP-2FA.
- Einladungen sind gehasht, einmalig, ablaufend und rate-limitiert. Es gibt
  keine öffentliche Registrierung.
- Medien werden nicht direkt durch Caddy ausgeliefert. Eine autorisierte
  Django-View prüft Mitgliedschaft und Einwilligung und kann intern/kurzlebig
  ausliefern.
- App, PostgreSQL und Vision veröffentlichen produktiv keine Host-Ports; nur
  Caddy ist Eingang. Getrennte Datenbankrollen und interne Diensttokens folgen
  Least Privilege.
- Logs enthalten keine Nachrichtentexte mit sensiblen Daten, Bilder,
  Gesichtsausschnitte, Namen oder biometrische Vektoren.
- Lokale Medien sind zunächst ein versioniertes Volume/Verzeichnis. S3 wird
  erst eingeführt, wenn Migration, Größe oder Betrieb es verlangen.
- Redis/Worker werden erst bei nachgewiesenem Bedarf an dauerhaften Jobs oder
  Echtzeitverteilung eingeführt. Bis dahin sind DB-gestützte Jobs oder direkte
  kurze Tasks vorzuziehen.

## Reproduzierbarer Docker-Betrieb und Portabilität

Alle Bestandteile bilden langfristig genau ein transportierbares
Docker-Compose-Projekt mit dem stabilen Projektnamen `klasse-5e`. Das
Web-Push-Kit bleibt Bibliothekscode im App-Image und erhält weder Container
noch Deployment. Die Zielstruktur lautet:

| Compose-Dienst | Aufgabe | Netzwerkzugang | Persistenz |
|---|---|---|---|
| `klasse-5e-app` | ab Phase 2 Django/Wagtail, SSR/PWA und internes Push-Kit | internes Netz und gemeinsames externes Proxy-Netz; nur über globalen Caddy erreichbar | geschützte Medien/Dokumente in dokumentiertem Volume |
| `klasse-5e-db` | PostgreSQL | nur internes Compose-Netz, kein produktiver Host-Port | eigenes benanntes Datenbank-Volume |
| `klasse-5e-vision` | ab Phase 1B lokale Vision-API, OpenCV/ONNX Runtime und freigegebene Modelle | ausschließlich internes Compose-Netz, kein Host-Port | eigene Vision-Daten und getrennt bereitgestellte Modelle |
| `klasse-5e-worker` | nur später bei nachgewiesenem dauerhaftem Jobbedarf | internes Netz | keine Einführung ohne neue Entscheidung |

Compose-Projekt, Dienste, internes Netz und Volumes erhalten eindeutige,
projektbezogene Namen. Der globale Caddy aus `HomeInfrastructure` wird nicht
kopiert. Die App wird später zusätzlich an dessen externes Docker-Netz
angeschlossen. Für Diagnose und Abnahme darf ein gesondertes, nicht
produktives Compose-Profil oder Override ausschließlich die App an
`127.0.0.1` veröffentlichen; DB und Vision bleiben intern.

Regulärer Betrieb setzt nur Docker Engine/Desktop, das Repository oder ein
Release-Paket und lokal bereitgestellte Secrets voraus. Er hängt nicht von
Windows-Python/-Node, einer lokalen Datenbank, absoluten Windows-Pfaden,
Host-IP, Rechnernamen oder manuellen Änderungen in laufenden Containern ab.
Entwicklung darf Quellcode per Bind Mount einbinden. Produktion verwendet
reproduzierbar aus versionierten Dockerfiles gebaute und versionierte Images.
Kontrollierte Datenbankmigrationen sind Teil des Deployments; Healthchecks
decken App, Datenbank und Vision ab.

Fach- und Laufzeitdaten liegen ausschließlich in dokumentierten benannten
Volumes oder bewusst gewählten relativen Projektverzeichnissen. Modelle,
Uploads, Fotos, Embeddings und Secrets werden nie in Images eingebaut. Modelle
werden über einen dokumentierten, prüfsummenverifizierten Importprozess aus
einer freigegebenen Quelle bereitgestellt. Container-Layer sind vollständig
ersetzbar und enthalten keine einzige maßgebliche Kopie persistenter Daten.

### Portabler Export und Umzug

Eine portable Sicherung umfasst:

- PostgreSQL-Dump;
- geschützte Medien und Dokumente;
- Vision-Datenbank, bestätigte Referenzdaten und Embeddings;
- Modellmanifest und Modellprüfsummen, nicht ungeprüfte Modellgewichte im
  Anwendungsimage;
- relevante nicht geheime Konfiguration;
- Liste der benötigten `secret://`-Referenzen;
- verwendete Image- und Anwendungsversionen.

Passwörter, VAPID Private Key, Diensttokens, private Schlüssel und andere
entschlüsselte Secrets sind nie Bestandteil eines unverschlüsselten Exports.
Sie werden am Zielhost erneut über die lokale Geheimnisverwaltung
bereitgestellt.

Der verbindliche Migrationsweg lautet:

```text
backup → Integritätsprüfung → Übertragung → restore → Datenbankmigration
       → Start → Healthchecks → Funktionstest → Reverse-Proxy-Umschaltung
```

Ein Hostwechsel benötigt damit nur Repository/Release, geprüften Datenexport,
Secret-Bereitstellung, `docker compose` und eine dokumentierte Proxy-Route am
Zielsystem. Portabilität gilt erst als nachgewiesen, wenn Backup und Restore
spätestens vor Produktivbetrieb auf einem frischen zweiten Docker-Host samt
Health- und Funktionstests erfolgreich waren. Die konkrete Compose-Grundlage
entsteht in Phase 2; Phase 1B erhält vorab nur die freigegebene kleine interne
Vision-Testkonfiguration.

## Risiken und offene Entscheidungen

| Thema | Risiko / Entscheidung | Zeitpunkt |
|---|---|---|
| Repository | `Klasse_5e` ist noch kein Git-Repository. | vor Phase 1 |
| Django/Wagtail | konkrete kompatible Versionen und 2FA/Passkey-Paket nach Wartungs-, Lizenz- und Sicherheitsprüfung pinnen | Phase 2 |
| Push-Browser | iOS-PWA-Einschränkungen, Payloadgrößen, Zustellgarantie und Browser-Abmeldung praktisch testen | Phase 1A/2 |
| Push-Datenschutz | erlaubte Inhalte pro Kategorie und Login-only-Links festlegen | vor erster Fachintegration |
| Vision-Modell | Haar/LBPH gegen ein lokales CPU-Modell mit echten, rechtmäßig verwendbaren Testbildern vergleichen | Phase 1B |
| Biometrie | Verantwortliche Stelle, Datenschutzprüfung, Löschfristen und Einwilligungstexte fehlen noch | vor Phase 6 |
| Vision-Store | PostgreSQL im Vision-Container oder SQLite mit klarer Single-Writer-Grenze entscheiden; keine JSON-Dauerhaltung | Phase 1B |
| PDF | vorliegender PDF-SmartForms-Bestand ist nur eine Distribution; keine Codeextraktion möglich. AcroForm-Bedarf und Lizenzierung separat klären | Phase 3 |
| Lizenzen | Mila-Code ist proprietär; nur Ideen, keine Codekopie. PDF-Lizenz ist Entwurf. Alle Python-/JS-/Modellabhängigkeiten benötigen SBOM und Lizenzprüfung | je Phase |
| Medien | Kapazität, Backupdauer, Löschfristen und Restore-Zielwerte festlegen | Phase 2/5/10 |
| Infrastruktur | breite temporäre Tailscale-Regel und Übergangsnetz dürfen nicht als Klassenisolation gelten | vor Produktion |
| Schulportal | Portal, API, Nutzungsrecht, MFA und Zugang fehlen absichtlich | Phase 9 |

## Nicht übernommen / neu zu bauen

Direkt als Referenz übernommen werden nur: EventMonitors VAPID-Aufrufsmuster
und Stale-Erkennung, der Service-Worker-Lebenszyklus, Milas bestätigter
Prüfablauf, sichere Pfadauflösung/Größenlimits als Testideen sowie Caddys
gemeinsames Netz- und Route-Konzept. Es wird kein Code blind kopiert.

Neu gebaut werden das Django/Wagtail-Fachmodell, sämtliche Rollen- und
Einwilligungspolicies, geschützte Medienauslieferung, PWA-Shell, neutrales
Push-Paket, Vision-Vertrag/Persistenz/Collection-Isolation/Löschung,
CMS-Funktionen und alle späteren Fachmodule.

## Konkrete Phase-1B-Struktur

`services/vision` ist ein einzelner FastAPI-Dienst mit SQLAlchemy/Alembic und
SQLite im WAL-Modus. Genau eine aktive Instanz verarbeitet gelegentliche,
persistierte Jobs und nimmt sie nach Neustart kontrolliert wieder auf. Diese
Last und der Verzicht auf horizontale Skalierung rechtfertigen SQLite;
PostgreSQL wäre derzeit zusätzliche Betriebskomplexität ohne konkreten Nutzen.

Zusammengesetzte Schlüssel und Fremdschlüssel führen `collection_id` durch alle
fachlichen Tabellen. Die interne `/v1`-API verlangt außer beim Healthcheck ein
Diensttoken. Ein Mensch bestätigt oder verwirft jeden Vorschlag; nur ein
expliziter Parameter macht einen bestätigten Treffer zur Referenz.

Das Image enthält weder Modelle noch Laufzeitdaten. Das normale Compose
veröffentlicht keinen Host-Port und nutzt getrennte Daten- und Modellvolumes;
der Development-Override bindet den Diagnoseport ausschließlich an
`127.0.0.1`. Die API bleibt später Teil des einen Compose-Projekts `klasse-5e`.

## Konkrete Phase-2-Struktur

Der Monolith verwendet Django 5.2 LTS, Wagtail 7.2 LTS und ein von Beginn an
eigenes E-Mail-basiertes `UserAccount`-Modell. `django-allauth` übernimmt
TOTP, WebAuthn/Passkeys und Recovery Codes; eine zusätzliche Policy sperrt
privilegierte Rollen ohne eingerichteten zweiten Faktor. Einladungen speichern
nur SHA-256-Tokenwerte und sind einmalig sowie zeitlich begrenzt.

Die erste Migration enthält Personen, Schülerprofile, Haushalte, bestätigte
Guardian-Child-Beziehungen, Schuljahre, Klassenmitgliedschaften, Rollen,
versionierte Einzelentscheidungen zu Einwilligungen, Audit und technische
Push-Subscriptions. Zugriffe werden unmittelbar gegen aktives Konto,
Mitgliedschaft, Rolle, Beziehung und Sichtbarkeit geprüft. Die PWA cached nur
statische Shell-Ressourcen und niemals authentisierte Antworten.

Das gemeinsame Compose-Projekt heißt `klasse-5e` und umfasst App, PostgreSQL
und den unveränderten Vision-Dienst. Das normale Compose veröffentlicht keine
Host-Ports; `compose.dev.yaml` bindet Diagnoseports ausschließlich an
`127.0.0.1`. App und Vision laufen ohne root und mit read-only Root-Dateisystem;
alle Fachdaten liegen in benannten Volumes.
