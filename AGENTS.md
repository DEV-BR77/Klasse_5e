# Projektregeln für Codex

## Maßgebliche Quellen

Vor jeder Aufgabe sind die zentralen Vorgaben in
`C:\Users\Bjoern\.homeops\codex-instructions.md` zu lesen. Bei Docker,
Netzwerk, DNS, Backups oder Self-Hosting gilt zusätzlich
`C:\Users\Bjoern\.homeops\context.yaml`.

Für dieses Projekt sind in dieser Reihenfolge maßgeblich:

1. `PROJECT.md` für Ziel, MVP und verbindliche Leitplanken,
2. `docs/Architecture.md` für Architektur und Modulgrenzen,
3. `docs/DecisionLog.md` für angenommene Entscheidungen,
4. `docs/Roadmap.md` für Phasen, Reihenfolge und Abnahmekriterien.

## Arbeitsregeln

- Es wird ausschließlich die ausdrücklich freigegebene Phase umgesetzt.
- Spätere Anforderungen werden dokumentiert, aber nicht vorgezogen.
- Der Anwendungskern bleibt ein modularer Django/Wagtail-Monolith.
- Vision ist der einzige vorab erlaubte separate Fachdienst.
- Redis, Worker, WebSockets, S3, Microservices und zusätzliche Frontend-
  Frameworks benötigen einen nachgewiesenen Bedarf und eine neue Entscheidung.
- Bestehende Implementierungen werden vor Neuentwicklung geprüft, aber nicht
  blind kopiert.
- Andere Repositories dürfen nur verändert werden, wenn der aktuelle Auftrag
  sie ausdrücklich einschließt.
- Nicht eingecheckte Benutzerarbeit muss erhalten bleiben.
- Geheimnisse, personenbezogene Laufzeitdaten, Fotos, Gesichtsausschnitte,
  Embeddings, Modelle und Uploads gehören nicht in Git.
- Biometrische Funktionen bleiben trotz abgeschlossener Phase 6 standardmäßig
  deaktiviert und benötigen für jeden Betrieb die dokumentierte Einwilligung.
- Jede abgeschlossene Phase benötigt angemessene Tests, kurze Dokumentation,
  Sicherheitsprüfung und überprüfbare Abnahmekriterien.
- Änderungen werden in kleinen, nachvollziehbaren Commits festgehalten.

## Aktueller Stand

Phase 0 bis Phase 6 sind abgeschlossen. Die Phasen 7 bis 11 sind als
aufeinanderfolgender Auftrag freigegeben; jede Phase benötigt vor Beginn der
nächsten ein vollständiges Qualitätsgate.
