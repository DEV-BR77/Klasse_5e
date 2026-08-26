# Technischer Projektüberblick

Dieses Dokument enthält die technischen Informationen, die früher direkt auf
der Repository-Startseite standen. Die allgemein verständliche Vorstellung des
Klassenportals befindet sich in der [README](../README.md).

## Systemstand

Klasse 5e ist eine geschlossene, selbst gehostete Klassenplattform als
installierbare Progressive Web App. Die Phasen 0 bis 8 sind umgesetzt. Das
portable Django/Wagtail-Grundsystem läuft mit PostgreSQL und der internen
Vision-API in einem gemeinsamen Compose-Projekt.

Enthalten sind der geschützte CMS-Kern, Veranstaltungen und
transaktionssichere Mitbringlisten, moderierte Event-Fotogalerien, der
Klassenchat sowie ein manueller Kalender und Stundenplan. Die lokale,
einwilligungsbasierte Personensuche ist standardmäßig deaktiviert, zeigt nur
menschlich zu bestätigende Vorschläge und ist nicht produktiv freigegeben.

## Beschlossene technische Richtung

- modularer Monolith mit Django und Wagtail;
- PostgreSQL als einzige fachliche Datenbank;
- serverseitig gerenderte, mobile Oberfläche mit schlankem JavaScript;
- PWA und Web Push ohne separaten SPA-Stack;
- lokale Medienablage hinter autorisierten Django-Downloads;
- separate lokale Vision-API nur wegen OpenCV- und Modellabhängigkeiten;
- Caddy aus `HomeInfrastructure` als gemeinsamer HTTPS-Einstieg;
- Redis, Objektstorage und WebSockets erst bei nachgewiesenem Bedarf.

## Komponenten

Das interne Paket unter `packages/web-push-kit` enthält validierte Python-DTOs,
VAPID-Konfiguration, einen `pywebpush`-Sender mit strukturierten Ergebnissen,
Browser-Helfer für An- und Abmeldung sowie eine neutrale
Service-Worker-Vorlage.

Die Vision-API unter `services/vision` ergänzt Collection-isolierte Persistenz,
persistierte Jobs, Human-in-the-loop, vollständige Löschpfade und portablen
Docker-Betrieb. Sie enthält keine Benutzer-, Klassen- oder Einwilligungslogik.

Unter `app` liegen Einladungslogin, MFA-Policy, Personen-, Familien-, Klassen-
und Einwilligungsmodell, Audit, PWA, Push-An- und Abmeldung sowie die
geschützten CMS-, Event-, Galerie-, Chat- und Kalendermodule.
`app/src/klasse5e/biometrics` koppelt die Galerie über opaque IDs an Vision und
erzwingt Einwilligung, Rollen, menschliche Bestätigung und Widerrufslöschung.

## Lokaler Diagnosebetrieb

Der normale Start veröffentlicht keinen Port. Für einen ausschließlich lokal
gebundenen Diagnosezugang wird zusätzlich `compose.dev.yaml` verwendet. Die
benötigten Geheimnisse werden nur im aufrufenden Prozess bereitgestellt; siehe
[`app/docs/OPERATIONS.md`](../app/docs/OPERATIONS.md).

## Weiterführende Dokumentation

- [Projektauftrag und MVP](../PROJECT.md)
- [Architektur und Bestandsaufnahme](Architecture.md)
- [Entscheidungsprotokoll](DecisionLog.md)
- [Phasenplan](Roadmap.md)
- [Vorbereitete InsightFace-Lizenzanfrage](licenses/InsightFace-Lizenzanfrage.md)
- [Web-Push-Kit](../packages/web-push-kit/README.md)
- [EventMonitor-Migrationsnotiz](migrations/EventMonitorAI-web-push-kit.md)
- [Vision-API](../services/vision/README.md)

