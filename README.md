# Klasse 5e

Geschlossene, selbst gehostete Klassenplattform als installierbare Progressive
Web App. Das Projekt befindet sich nach der Bestandsaufnahme in **Phase 0**:
Es enthält einen verbindlichen Bauplan, aber noch keine Anwendung.

## Dokumentation

- [Projektauftrag und MVP](PROJECT.md)
- [Architektur und Bestandsaufnahme](docs/Architecture.md)
- [Entscheidungsprotokoll](docs/DecisionLog.md)
- [Phasenplan](docs/Roadmap.md)
- [Vorbereitete InsightFace-Lizenzanfrage](docs/licenses/InsightFace-Lizenzanfrage.md)

## Beschlossene technische Richtung

- modularer Monolith mit Django und Wagtail
- PostgreSQL als einzige fachliche Datenbank
- serverseitig gerenderte, mobile Oberfläche mit schlankem JavaScript
- PWA und Web Push ohne separaten SPA-Stack
- lokale Medienablage hinter autorisierten Django-Downloads
- separate lokale Vision-API nur wegen OpenCV-/Modellabhängigkeiten
- Caddy aus `HomeInfrastructure` als gemeinsamer HTTPS-Einstieg
- Redis, Objektstorage und WebSockets erst bei nachgewiesenem Bedarf

## Nächster Schritt

Nach Freigabe werden Phase 1A (internes Web-Push-Kit) und Phase 1B
(projektneutrale Vision-API) getrennt geplant und umgesetzt. Bis dahin werden
`EventMonitorAI` und `The-Life-of-Mila` nicht verändert.
