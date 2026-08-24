# Roadmap

Es wird immer nur die freigegebene Phase umgesetzt. Spätere Anforderungen
werden hier präzisiert, nicht vorgezogen. Komplexität ist relativ zum Projekt:
**S** klein, **M** mittel, **L** groß, **XL** sehr groß.

| Phase | Ergebnis | Komplexität | Wesentliche Abnahme |
|---|---|---:|---|
| 0 | Bestandsaufnahme und Bauplan | M | diese fünf Dokumente; klare Wiederverwendung, Risiken und Grenzen |
| 1A | internes, generisches Web-Push-Kit | M | neutrale DTOs/Payloads, Versand, 404/410-Ergebnis, An-/Abmeldung, Service-Worker-Helfer, Tests, EventMonitor-Migrationsnotiz |
| 1B | lokale projektneutrale Vision-API | XL | Collection-Isolation, robuster Store, Jobs, bestätigter Workflow, Lösch-APIs/-tests, Modellvergleich, interner Container |
| 2 | schlankes Django/Wagtail-Grundsystem | XL | Einladungen, Rollen, Familien, Mitgliedschaft, versionierte Einwilligungen, Audit, PWA, PostgreSQL, starke Admin-Anmeldung |
| 3 | CMS-Kern | L | wirklich geschützte PDFs, freigegebene Lehrerfelder, Beiträge/Kommentare und fachliche CMS-Rechte |
| 4 | Events und Mitbringlisten | M–L | transaktionssichere Reservierung, Eigenverwaltung, Audit und Erinnerungs-Push |
| 5 | geschützte Galerien ohne Vision | XL | Uploadprüfung, Metadatenentfernung, Moderation, Einwilligungsprüfung, geschützte Medien und Löschfristen |
| 6 | optionale biometrische Suche | XL | standardmäßig aus, ausdrückliche Einwilligung, nur bestätigte Treffer, Zugriff nur auf eigene Kinder, vollständiger Widerrufstest |
| 7 | begrenzter Klassenchat | L | Klassen-/Eventräume, Zugriffsentzug, Moderation, Aufbewahrung und datensparsamer Push; Echtzeittechnik erst nach Messung |
| 8 | manueller Kalender und Stundenplan | L | Wochenansicht, Änderungsvergleich, deduplizierter Push und widerrufbares iCal |
| 9 | Schulportaladapter | L–XL | erst nach Portal-/API-/Rechtsprüfung; idempotenter austauschbarer Adapter und manueller Fallback |
| 10 | Produktion und Schuljahreswechsel | XL | Compose/Caddy, Header, Health, Export/Löschung, Backup und praktisch geübter Restore, Übergabe und Sitzungsentzug |

## Freigabepunkte

1. **Jetzt:** Phase 0 prüfen und Bauplan freigeben oder korrigieren.
2. **Danach separat:** Phase 1A und 1B dürfen geplant/implementiert werden;
   fremde Repositories bleiben zunächst unverändert.
3. **Vor Phase 2:** Repository initialisieren, Django/Wagtail-Versionen sowie
   starke Admin-Authentisierung auswählen und Datenschutztexte fachlich klären.
4. **Vor Produktion:** Betriebsadresse, Caddy-Route, Backupziel,
   Wiederherstellungsziele und Netz-Zugriffspolicy freigeben.
5. **Vor Phase 6:** gesonderte Datenschutzentscheidung zur Biometrie.
6. **Vor Phase 9:** gesonderte rechtliche und technische Machbarkeitsprüfung.

## Bewusst zurückgestellt

Mehrere Schulen/SaaS, native Apps, Direktnachrichten, Video, Zahlungen,
Noten/Krankmeldungen, öffentliche Galerien, Cloud-Gesichtserkennung,
automatische endgültige Identifikation, allgemeines IAM, Kubernetes, Event Bus,
API-Gateway und Microservices für CRUD-Funktionen bleiben Nicht-Ziele, bis eine
neue ausdrückliche Entscheidung sie ändert.

