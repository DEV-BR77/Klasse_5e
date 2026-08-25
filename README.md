# Klasse 5e

Geschlossene, selbst gehostete Klassenplattform als installierbare Progressive
Web App. Die Phasen 0, 1A, 1B und 2 sind abgeschlossen. Das portable
Django/Wagtail-Grundsystem läuft mit PostgreSQL und der internen Vision-API in
einem Compose-Projekt. Phase 3 ergänzt den geschützten CMS-Kern.

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
Unter `app` liegen Einladungslogin, MFA-Policy, Personen-/Familien-/Klassen-
und Einwilligungsmodell, Audit, PWA und Push-An-/Abmeldung. Phase 3 und 4 werden
im aktuellen Auftrag nacheinander ergänzt. Die Referenzprojekte bleiben
unverändert.

## Lokaler Diagnosebetrieb

Der normale Start veröffentlicht keinen Port. Für einen ausschließlich lokal
gebundenen Diagnosezugang wird zusätzlich `compose.dev.yaml` verwendet. Die
benötigten Geheimnisse werden nur im aufrufenden Prozess bereitgestellt; siehe
`app/docs/OPERATIONS.md`.
