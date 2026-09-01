# Entscheidungsprotokoll

Kurze ADRs; Status **angenommen**, sofern nicht anders markiert.

## ADR-001: Modularer Monolith

**Entscheidung:** Django und Wagtail bilden einen Prozess und ein Deployment
mit klaren internen Fachmodulen und einer PostgreSQL-Datenbank.

**Grund:** Die Plattform bedient eine Klasse. Gemeinsame Transaktionen,
Berechtigungen und ein kleiner Betriebsumfang sind wichtiger als unabhängige
Skalierung. Fachmodule werden nicht zu Netzwerkdiensten.

**Folge:** Redis, API-Gateway, Event Bus, Kubernetes und Datenbanken pro Modul
sind ausgeschlossen, solange ein messbarer Bedarf fehlt.

## ADR-002: Server Rendering statt SPA

**Entscheidung:** Django-Templates/Wagtail rendern die Oberfläche; JavaScript
wird gezielt für PWA, Push und spätere Echtzeitinteraktion eingesetzt.

**Grund:** Ein separater SPA-Build erhöht Abhängigkeiten, Auth-Komplexität und
Betriebsaufwand ohne Nutzen für das MVP.

## ADR-003: Push-Kit zunächst internes Paket

**Entscheidung:** Phase 1A legt den generischen Push-Kern als eigenständiges,
internes Python-Paket mit frameworkneutralen DTOs und Browser-Assets im
`Klasse_5e`-Repository an.

**Grund:** Eine zweite produktive Integration ist noch nicht migriert. Ein
neues Repository würde Versionierung und Veröffentlichung vor tatsächlicher
Wiederverwendung erzwingen. Paketgrenzen und Tests ermöglichen späteres
Extrahieren ohne EventMonitor-Fachlogik.

**Folge:** EventMonitor bleibt unverändert und erhält nur eine kurze spätere
Migrationsanleitung. Ein gemeinsames Repository wird erst entschieden, wenn
beide Anwendungen dasselbe veröffentlichte Paket wirklich konsumieren sollen.

Der konkrete Distributionsname lautet `klasse5e-web-push-kit`, der Importname
`web_push_kit`. Browser-Tests verwenden ausschließlich den eingebauten
Node-Testläufer; eine npm-/Bundler-Infrastruktur entsteht nicht.

## ADR-004: Vision als separater lokaler Dienst

**Entscheidung:** OpenCV, Modelle und biometrische Daten liegen in einer
projektneutralen Vision-API mit eigenem Container und robustem Store. Sie ist
nur im internen Docker-Netz erreichbar.

**Grund:** Schwere/abweichende native Abhängigkeiten, Modellversionierung und
vollständige biometrische Löschung brauchen eine eigene Betriebs- und
Sicherheitsgrenze. Diese Ausnahme begründet keinen Dienst pro Fachmodul.

**Folge:** Die API kennt keine Namen oder Konten, erzwingt `collection_id` und
gibt nur Vorschläge aus. Das Portal hält `subject_id`-Zuordnungen. Nutzung in
Klasse 5e bleibt bis Phase 6 deaktiviert.

## ADR-005: Vision-Workflow erhalten, Implementierung ersetzen

**Entscheidung:** Erkennen, Kandidaten vorschlagen, menschlich bestätigen oder
verwerfen und optional bestätigte Referenzen aufnehmen bleibt erhalten. Der
Ein-Datei-Server, JSON-Dauerhaltung und globale Threads werden nicht übernommen.

**Grund:** Der Workflow verhindert automatische endgültige Identifikation;
die vorhandene technische Form bietet dagegen keine belastbare
Collection-Isolation, Authentisierung, Migration oder vollständige Löschung.

## ADR-006: Modellwahl erst nach Vergleich

**Status:** angenommen mit offener Modellwahl.

**Entscheidung:** Haar/LBPH bildet die reproduzierbare Baseline. Eine Ablösung
erfolgt nur nach lokalem CPU-Vergleichstest, dokumentierter Modelllizenz und
kontrollierbarer Modellversion.

**Grund:** Haar/LBPH ist klein, lokal und bewährt, aber bei Kinderfotos,
Gruppenbildern, Pose und Alter wahrscheinlich begrenzt. Eine ungetestete
Modernisierung wäre ebenso riskant.

## ADR-007: Lokale Medien zuerst

**Entscheidung:** Dateien liegen zunächst lokal in gesicherten Volumes und
werden ausschließlich nach Anwendungsprüfung ausgeliefert. S3-kompatibler
Storage ist keine MVP-Abhängigkeit.

**Grund:** Ein einzelner Betreiber profitiert von einfachem Backup und Restore.
Öffentliche oder dauerhafte Medien-URLs sind unabhängig vom Speicher verboten.

## ADR-008: Gemeinsamer Caddy

**Entscheidung:** Das Projekt verwendet den globalen Caddy aus
`HomeInfrastructure` und später ein verwaltetes Route-Fragment. Es startet
keinen zweiten öffentlichen Reverse Proxy.

**Grund:** Zertifikate, Ports und gemeinsame Infrastruktur sollen
projektunabhängig bleiben.

## ADR-009: Keine Aktionstoken im Push-Kit

**Entscheidung:** Phase 1A enthält keine signierten Aktionstoken. Neutrale
Notification-Aktionen dürfen nur auf zugelassene URLs verweisen.

**Grund:** Claims, Benutzerbezug, Autorisierung und Wirkung einer Aktion sind
Fachlogik der einbettenden Anwendung. Ein generischer Tokenmechanismus würde
ohne zweiten konkreten Anwendungsfall unnötige Sicherheits-API erzeugen.

**Folge:** Detailseiten verlangen reguläre Anmeldung. Benötigt eine Anwendung
später eine direkte Aktion, implementiert und testet sie kurzlebige Claims in
ihrem eigenen Sicherheitskontext.

## ADR-010: Ein portables Docker-Compose-Projekt

**Entscheidung:** Alle Laufzeitbestandteile gehören zu genau einem stabil
benannten Compose-Projekt `klasse-5e`. Vorgesehene Dienste sind
`klasse-5e-app`, `klasse-5e-db` und `klasse-5e-vision`; ein Worker ist nur nach
einer späteren Bedarfsentscheidung zulässig. Das Push-Kit bleibt Bibliothek im
App-Container. Produktion veröffentlicht keine internen Host-Ports und bindet
nur die App an das externe Netz des globalen Caddy an.

**Grund:** Repository/Release, persistenter Export und Secrets sollen für einen
Umzug auf jeden geeigneten Docker-Host genügen. Lokale Python-/Node-/Datenbank-
Installationen, Hostnamen, absolute Windows-Pfade und manuell veränderte
Container würden Reproduzierbarkeit und Restore-Fähigkeit verhindern.

**Folge:** Phase 2 liefert versionierte Dockerfiles, Produktions-Compose,
benannte Volumes, internes Netz, App-/DB-Healthchecks und einen ausschließlich
lokalen Diagnosezugang. Phase 1B liefert zuvor nur Vision-Image, internen
Healthcheck und kleine Compose-Testkonfiguration. Modelle und sämtliche
Fachdaten werden außerhalb ersetzbarer Image-/Container-Layer gehalten.
Backup/Restore umfasst Datenbank, Medien und Vision-Daten sowie Manifeste,
Prüfsummen, nicht geheime Konfiguration, Secret-Referenzliste und Versionen;
entschlüsselte Secrets sind ausgeschlossen. Vor Produktivbetrieb wird der
vollständige Ablauf auf einem frischen zweiten Docker-Host praktisch geprüft.

## ADR-011: Rechte auf Schülerprofile nur über verifizierte Beziehungen

**Entscheidung:** Ab Phase 2 sind Schüler eigene Personen mit
`StudentProfile` und Klassenmitgliedschaft, ohne notwendiges MVP-Benutzerkonto.
Jeder Sorgeberechtigte verwendet ein persönliches Benutzerkonto. Rechte werden
ausschließlich aus einer bestätigten, zeitlich gültigen
`GuardianChildRelationship` mit getrennten Verwaltungs- und
Einwilligungsrechten abgeleitet, nicht aus Haushalt oder Freitext.

**Grund:** Gemeinsame Logins und Identitätsübernahme verhindern persönliche
Auditierbarkeit. Haushalte bilden Sorge-, Trennungs- und Bezugspersonenmodelle
nicht zuverlässig ab. Besonders biometrische Einwilligungen müssen pro
entscheidungsberechtigter Person nachvollziehbar und konfliktfähig bleiben.

**Folge:** Inhalte und administrative Handlungen referenzieren immer das
tatsächlich handelnde Konto. Sichtbare Familienbezeichnungen entstehen nur aus
verifizierten Beziehungen und unterliegen Profilfreigaben. Fehlende,
widersprüchliche oder widerrufene erforderliche Zustimmungen blockieren oder
stoppen sensible Verarbeitung. Phase 1B implementiert davon keinerlei Modelle.

## ADR-012: SQLite für den einzelnen Vision-Container

**Entscheidung:** Phase 1B verwendet SQLite mit WAL, aktivierten Fremdschlüsseln
und kontrollierten Transaktionen. Es läuft genau eine Service-Instanz ohne
separaten Worker.

**Grund:** Gelegentliche lokale Batches benötigen Persistenz und
Neustartfähigkeit, aber keine horizontale Parallelität. PostgreSQL, Redis und
ein Broker würden den portablen Betrieb ohne nachgewiesenen Nutzen vergrößern.

**Folge:** Horizontale Skalierung ist ausgeschlossen. Wenn Messungen später
mehrere Instanzen erfordern, wird Store und Jobmodell neu entschieden.

## ADR-013: YuNet/SFace produktiver Kandidat, InsightFace gesperrt

**Entscheidung:** YuNet 2023mar plus SFace 2021dec ist die bevorzugte lokale
CPU-Pipeline. Haar/LBPH bleibt getrennte Legacy-Baseline. Der SCRFD/ArcFace-
Adapter meldet ohne schriftliche Erlaubnis und installierte, manifestierte
Gewichte ausschließlich `model_not_licensed_or_installed`.

**Grund:** OpenCV stellt konkrete Gewichte mit dokumentierter Herkunft,
Lizenzen und Prüfsummen bereit. Die Lizenz der InsightFace-Gewichte ist für den
operativen Anwendungsfall nicht geklärt.

**Folge:** Kein Image und kein normaler Start lädt Modelle. Modellwechsel sind
kontrollierte Migrationen; Embeddings verschiedener Versionen werden niemals
direkt verglichen.

## ADR-014: Django-LTS, Wagtail-LTS und Allauth-MFA

**Entscheidung:** Der Monolith pinnt Django 5.2.17 LTS, Wagtail 7.2.3 LTS und
django-allauth 65.19.1 mit TOTP-, WebAuthn- und Recovery-Code-Unterstützung.

**Grund:** Die LTS-Linien reduzieren Upgrade-Risiko. Allauth ist aktiv
gepflegt, Wagtail-kompatibel und vermeidet eigene Kryptografie. Privilegierte
Rollen werden zusätzlich durch eine zentrale MFA-Policy geschützt.

**Folge:** Es gibt keine öffentliche Registrierung. Bootstrap erzeugt nur
eine zeitlich begrenzte Einladung und schreibt ihr Klartexttoken ausschließlich
in eine explizit gewählte lokale Datei mit restriktiven Rechten.

## ADR-015: Ein PostgreSQL-Store für den Monolithen

**Entscheidung:** Alle Fachmodule des Monolithen nutzen dieselbe PostgreSQL-
Datenbank und gemeinsame Transaktionen. SQLite ist ausschließlich eine schnelle
Testoption; regulärer Docker-Betrieb verwendet PostgreSQL.

**Grund:** Klassenrechte, Audit und spätere Reservierungskonkurrenz benötigen
referenzielle Integrität und transaktionale Sperren, jedoch keine Datenbank je
Modul.

## ADR-016: Geschützte Medien über Fach-Views

**Entscheidung:** Klassenbezogene Dokumente werden in einem privaten Volume
gespeichert und nur durch eine autorisierte Django-Download-View ausgeliefert.
Wagtails allgemeine Dokumentauslieferung wird dafür nicht verwendet.

**Grund:** Ein direkter Medienpfad oder dauerhafter Link könnte Login- und
Klassenprüfung umgehen. Der kleine konkrete Downloadpfad ist leichter zu
prüfen als eine allgemeine Storage-Abstraktion.

## ADR-017: Datenbankgestützte Event-Erinnerungen ohne Worker

**Entscheidung:** Erinnerungsanlässe werden durch eine eindeutige Datenbankzeile
dedupliziert und von einem expliziten Management-/Deployment-Aufruf versendet.
Phase 4 führt keinen dauerhaften Worker ein.

**Grund:** Das geringe Klassenvolumen rechtfertigt weder Redis noch Celery.
Transaktionen und eindeutige Constraints liefern bereits Wiederholbarkeit;
ein späterer Scheduler kann denselben Service aufrufen.

## ADR-018: Neu codierte private Galerieableitungen

**Entscheidung:** Phase 5 speichert nach Pillow-Decodierung nur neu codierte
JPEG-/PNG-Ableitungen in opaque Verzeichnissen. Originaluploads und Metadaten
werden nicht behalten. Django liefert nach aktueller Klassen- und Consent-
Prüfung mit privaten No-Store-Headern aus.

**Grund:** Neu-Codierung entfernt EXIF/GPS und unbekannte Zusatzdaten.
Dynamische Policy-Prüfung macht Widerruf sofort wirksam; öffentliche oder
dauerhafte Links würden diese Grenze schwächen.

**Folge:** HEIC, automatische Verpixelung und Vision bleiben ausgeschlossen.
Download ist zweistufig standardmäßig deaktiviert.

## ADR-019: Biometrische Suche als deaktivierbare Integration

**Entscheidung:** Phase 6 integriert die projektneutrale Vision-API über opaque
UUIDs in ein eigenes Monolith-Modul. `BIOMETRIC_SEARCH_ENABLED` ist standardmäßig
aus. Ein Profil entsteht nur, wenn jeder aktuell verifizierte, rechtlich
sorgeberechtigte und biometrieberechtigte Guardian aktuell zugestimmt hat.
Modellvorschläge bleiben `proposed`, bis ein berechtigter Mensch bestätigt oder
verwirft; ein bestätigter Treffer wird nur mit einem zweiten expliziten Parameter
und eigener Consent-Art zur Referenz.

**Grund:** Die getrennte App-/Vision-Zuordnung hält Namen aus dem Vision-Dienst,
verhindert automatische Identifikation und macht Widerruf technisch prüfbar.
Collection- und Subject-IDs enthalten keine Fachbegriffe. Modelle und Scores
bleiben versionsgebundene Vergleichswerte, keine Prozentwahrscheinlichkeiten.

**Folge:** Verantwortliche Stelle für den freigegebenen technischen Test ist
Björn Radke. Vision-Quelldateien werden binnen 24 Stunden, bei dokumentierter
manueller Prüfung spätestens binnen sieben Tagen entfernt. Subject-Embeddings
werden binnen 24 Stunden nach Widerruf, Profillöschung, Testende oder Abschaltung
gelöscht. Zuordnungs-/Protokolldaten enden nach 30 Tagen, minimierte
sicherheitsrelevante Auditdaten spätestens nach 90 Tagen. Ein
`purge-source`-Endpunkt entfernt die importierte Bildquelle, ohne geprüfte
Ableitungen vorzeitig zu vernichten. Eine Produktivnutzung erfordert eine neue
gesonderte Freigabe.
# ADR-020: Klassenchat mit kurzem Polling

**Entscheidung:** Phase 7 verwendet serverseitige Django-Endpunkte und kurzes
Polling statt WebSockets. Räume sind klassenisoliert, Nachrichten werden nur
inhaltsleer zurückgezogen oder moderativ ausgeblendet und nach der definierten
Frist gelöscht. Push ist opt-in und enthält keinen Nachrichtentext.

**Grund:** Für einen kleinen Klassenraum ist die robustere Betriebsform ohne
Redis und zusätzliche Worker ausreichend. Ein Wechsel zu SSE oder WebSockets
benötigt erst einen nachgewiesenen Last- oder Bedienungsbedarf.

# ADR-021: Manueller Kalender vor Portaladapter

**Entscheidung:** Der neutrale Wochenplan und Kalender sind eigenständige
Django-Modelle. Änderungen werden über Revisionen verglichen; iCal erhält
rotierbare, gehashte Zugriffstokens. Eine Portalquelle ist keine Voraussetzung.

**Grund:** Die Plattform bleibt bei Portalausfall nutzbar und sendet nur für
wirkliche neue Revisionen einen Hinweis.

# ADR-022: Versioniertes, fortsetzbares Datenschutz-Onboarding

**Entscheidung:** Der Erstlogin verwendet ein serverseitiges Zehn-Schritte-
Onboarding und die bestehenden Modelle `ConsentType`, `ConsentTextVersion` und
`ConsentDecision`. Ein kleiner `OnboardingState` speichert nur Schritt,
Identitätsbestätigung, Abschluss und Richtlinienversion. Optionale Zwecke sind
getrennt und standardmäßig aus; eine neue materielle Textversion erzwingt eine
erneute Entscheidung. Ein Tutorial besitzt einen unabhängigen Zustand.

**Grund:** Damit bleiben Nachweis, Widerruf, Rechteprüfung und Wiederaufnahme
auch ohne JavaScript konsistent. Für Kinder zählen nur bestätigte, aktuelle
Beziehungen mit Zweckrecht. Bei mehreren Berechtigten hält eine fehlende oder
ablehnende Entscheidung die Funktion aus. Produktive Pilotdaten bleiben reine

# ADR-023: Schulen als Mandantenebene und delegierte Klassenverwaltung

**Entscheidung:** Das bisherige Ein-Klassen-Modell wird migrationssicher um
Schulen erweitert. Jede Klasse gehört genau einer Schule; bestehende Klassen
werden bei der Migration einer Standardschule zugeordnet. Branding, aktivierte
Funktionen und sichtbare Menüpunkte können auf Schulebene und überschreibend
auf Klassenebene konfiguriert werden. Diese Darstellungskonfiguration ersetzt
niemals objektbezogene Berechtigungsprüfungen. Ein Hauptadministrator verwaltet
schulübergreifend, während die neue Rolle `class_admin` ausschließlich im
Kontext ihrer konkret zugewiesenen Klasse gilt.

**Grund:** Der ausdrücklich freigegebene Folgeauftrag hebt das frühere
Mehrschulen-Nichtziel auf. Eine explizite Mandantenachse verhindert implizite
globale Abfragen und ermöglicht später delegierte Verwaltung, ohne globale
Staff- oder Superuserrechte an Klassenadministratoren zu vergeben.

**Folge:** Alle fachlichen Abfragen und Adminaktionen werden schrittweise auf
Schul- und Klassenisolation geprüft. Logo- und Menüfelder sind private Medien
beziehungsweise Darstellungsdaten; serverseitige Policies bleiben maßgeblich.

# ADR-024: Kontrollierte Registrierung ohne unmittelbaren Fachzugriff

**Entscheidung:** Das frühere Verbot öffentlicher Registrierung wird durch
einen rate-limitierten Bewerbungsprozess mit E-Mail-Verifikation ersetzt. Ein
neues Konto bleibt bis zur administrativen Prüfung, expliziten Schul- und
Klassenzuweisung sowie abgeschlossenem Pflicht-Onboarding ohne Zugriff auf
Fachbereiche. Selbst erklärte Kinderbeziehungen beginnen stets unbestätigt.
Freigabelinks sind zufällig, gehasht gespeichert, kurz befristet, widerrufbar
und genau einmal verwendbar.

**Grund:** Interessierte Mitglieder sollen einen Antrag stellen können, ohne
dass eine behauptete Rolle oder Zuordnung eine Berechtigung erzeugt. Die
Trennung von Identitätsprüfung, Mandantenzuweisung, Beziehungsbestätigung und
Einwilligung erhält Least Privilege und persönliche Auditierbarkeit.

**Folge:** Registrierung, erneuter Mailversand und Login erhalten
Missbrauchsschutz ohne Tracker oder Benutzeraufzählung. Aktivierungs- und
Onboarding-Statusübergänge werden transaktionssicher und auditierbar.

# ADR-025: classid.de als kanonische Portal- und Versanddomain

**Entscheidung:** `https://classid.de` wird nach kontrollierter DNS-, TLS- und
Proxy-Migration die kanonische Portaladresse. Der bisherige Host bleibt
vorübergehend als HTTPS-Weiterleitung bestehen. Ausgehende Systemmail nutzt
ausschließlich freigegebene Absender der verifizierten Domain über Resend;
Reply-To ist fest konfiguriert und nicht frei durch Benutzer wählbar.

**Grund:** Portal- und Kommunikationsidentität sollen stabil und unabhängig
von der bisherigen Sammeldomain sein. Ein stufenweiser Wechsel erhält alte
Links und erlaubt einen klaren Rollback.

**Folge:** Vor produktiven Änderungen werden IONOS-Zone, Split-DNS, Caddy und
Zertifikate gesichert. Bestehende MX-, Mail- und sonstige Dienste bleiben
unangetastet; SPF wird pro Domain konsolidiert, DKIM ergänzt und DMARC zunächst
beobachtend betrieben. Resend ist kein Posteingang.
