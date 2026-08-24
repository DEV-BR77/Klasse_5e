# Klasse 5e

Geschlossene, selbst gehostete Klassenplattform als installierbare Progressive
Web App. Phase 0 ist freigegeben; Phase 1A stellt jetzt ein internes,
frameworkneutrales Web-Push-Kit bereit. Eine Klassenanwendung existiert noch
nicht.

## Dokumentation

- [Projektauftrag und MVP](PROJECT.md)
- [Architektur und Bestandsaufnahme](docs/Architecture.md)
- [Entscheidungsprotokoll](docs/DecisionLog.md)
- [Phasenplan](docs/Roadmap.md)
- [Vorbereitete InsightFace-Lizenzanfrage](docs/licenses/InsightFace-Lizenzanfrage.md)
- [Web-Push-Kit](packages/web-push-kit/README.md)
- [EventMonitor-Migrationsnotiz](docs/migrations/EventMonitorAI-web-push-kit.md)

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
Phase 1B und spätere Phasen sind nicht begonnen. `EventMonitorAI` und
`The-Life-of-Mila` wurden nicht verändert.
