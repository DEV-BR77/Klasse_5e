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

