# Klasse 5e

Geschlossene, selbst gehostete Klassenplattform als installierbare Progressive
Web App. Phase 0 und 1A sind abgeschlossen; Phase 1B stellt die lokale,
projektneutrale Vision-API bereit. Eine Klassenanwendung existiert noch nicht.

## Dokumentation

- [Projektauftrag und MVP](PROJECT.md)
- [Architektur und Bestandsaufnahme](docs/Architecture.md)
- [Entscheidungsprotokoll](docs/DecisionLog.md)
- [Phasenplan](docs/Roadmap.md)
- [Vorbereitete InsightFace-Lizenzanfrage](docs/licenses/InsightFace-Lizenzanfrage.md)
- [Web-Push-Kit](packages/web-push-kit/README.md)
- [EventMonitor-Migrationsnotiz](docs/migrations/EventMonitorAI-web-push-kit.md)
- [Vision-API](services/vision/README.md)

## Beschlossene technische Richtung

- modularer Monolith mit Django und Wagtail
- PostgreSQL als einzige fachliche Datenbank
- serverseitig gerenderte, mobile Oberfläche mit schlankem JavaScript
- PWA und Web Push ohne separaten SPA-Stack
- lokale Medienablage hinter autorisierten Django-Downloads
- separate lokale Vision-API nur wegen OpenCV-/Modellabhängigkeiten
- Caddy aus `HomeInfrastructure` als gemeinsamer HTTPS-Einstieg
- Redis, Objektstorage und WebSockets erst bei nachgewiesenem Bedarf

## Aktueller Umfang

Das interne Paket unter `packages/web-push-kit` enthält validierte Python-DTOs,
VAPID-Konfiguration, einen `pywebpush`-Sender mit strukturierten Ergebnissen,
Browser-Helfer für An-/Abmeldung und eine neutrale Service-Worker-Vorlage.
Die Vision-API unter `services/vision` ergänzt Collection-isolierte Persistenz,
persistierte Jobs, Human-in-the-loop, vollständige Löschpfade und portablen
Docker-Betrieb. Sie enthält keine Benutzer-, Klassen- oder Einwilligungslogik.
Spätere Phasen sind nicht begonnen. Die Referenzprojekte bleiben unverändert.
