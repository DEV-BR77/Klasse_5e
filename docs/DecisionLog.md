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
