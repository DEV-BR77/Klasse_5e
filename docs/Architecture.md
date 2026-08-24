# Architektur und Bestandsaufnahme

Stand: 24.08.2026. Die Prüfung war statisch und lesend; produktive Daten,
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

