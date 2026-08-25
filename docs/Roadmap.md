# Roadmap

Es wird immer nur die freigegebene Phase umgesetzt. Spätere Anforderungen
werden hier präzisiert, nicht vorgezogen. Komplexität ist relativ zum Projekt:
**S** klein, **M** mittel, **L** groß, **XL** sehr groß.

| Phase | Ergebnis | Komplexität | Wesentliche Abnahme |
|---|---|---:|---|
| 0 | Bestandsaufnahme und Bauplan | M | diese fünf Dokumente; klare Wiederverwendung, Risiken und Grenzen |
| 1A | **abgeschlossen:** internes, generisches Web-Push-Kit | M | neutrale DTOs/Payloads, Versand, 404/410-Ergebnis, An-/Abmeldung, Service-Worker-Helfer, Tests, EventMonitor-Migrationsnotiz |
| 1B | **abgeschlossen:** lokale projektneutrale Vision-API | XL | Collection-Isolation, SQLite/WAL, persistierte Jobs, bestätigter Workflow, Lösch-APIs/-tests, YuNet/SFace, getrennte Baseline, deaktiviertes InsightFace und interner Container |
| 2 | **abgeschlossen:** schlankes Django/Wagtail-Grundsystem | XL | Einladungen, persönliche Konten, Schülerprofile ohne Kontozwang, verifizierte Guardian-Child-Rechte, Rollen, Mitgliedschaft, einzelne versionierte Einwilligungen, Audit, PWA, PostgreSQL, starke Admin-Anmeldung |
| 3 | **abgeschlossen:** CMS-Kern | L | wirklich geschützte PDFs, freigegebene Lehrerfelder, Beiträge/Kommentare und fachliche CMS-Rechte |
| 4 | **abgeschlossen:** Events und Mitbringlisten | M–L | transaktionssichere Reservierung, Eigenverwaltung, Audit und Erinnerungs-Push |
| 5 | **abgeschlossen:** geschützte Galerien ohne Vision | XL | Uploadprüfung, Metadatenentfernung, Moderation, Einwilligungsprüfung, geschützte Medien und Löschfristen |
| 6 | optionale biometrische Suche | XL | standardmäßig aus, ausdrückliche Einwilligung, nur bestätigte Treffer, Zugriff nur auf eigene Kinder, vollständiger Widerrufstest |
| 7 | begrenzter Klassenchat | L | Klassen-/Eventräume, Zugriffsentzug, Moderation, Aufbewahrung und datensparsamer Push; Echtzeittechnik erst nach Messung |
| 8 | manueller Kalender und Stundenplan | L | Wochenansicht, Änderungsvergleich, deduplizierter Push und widerrufbares iCal |
| 9 | Schulportaladapter | L–XL | erst nach Portal-/API-/Rechtsprüfung; idempotenter austauschbarer Adapter und manueller Fallback |
| 10 | Produktion und Schuljahreswechsel | XL | Compose/Caddy, Header, Health, Export/Löschung, Backup und praktisch geübter Restore, Übergabe und Sitzungsentzug |

## Freigabepunkte

1. **Erledigt:** Phase 0, Phase 1A und Phase 1B sind abgeschlossen.
2. **Erledigt:** Phasen 2, 3 und 4 einschließlich phasenübergreifender Abnahme.
3. **Erledigt:** Phase 5, geschützte Galerien ohne Vision. Phase 6 bleibt
   ausdrücklich nicht freigegeben.
4. **Erledigt in Phase 2:** Django 5.2 LTS, Wagtail 7.2 LTS und django-allauth
   MFA sind gepinnt; Datenschutztexte bleiben ausdrücklich fachliche Entwürfe.
5. **Vor Produktion:** Betriebsadresse, Caddy-Route, Backupziel,
   Wiederherstellungsziele und Netz-Zugriffspolicy freigeben.
6. **Vor Phase 6:** gesonderte Datenschutzentscheidung zur Biometrie.
7. **Vor Phase 9:** gesonderte rechtliche und technische Machbarkeitsprüfung.

## Gemeinsamer Folgeauftrag für Phase 2 bis 4

Die Phasen 2, 3 und 4 werden nach Abschluss und Abnahme von Phase 1B als ein
gemeinsamer Auftrag strikt in der Reihenfolge 2 → 3 → 4 bearbeitet. Eine
Folgephase beginnt erst, wenn die vorherige Phase vollständig implementiert,
migriert, getestet, im Docker-Betrieb verifiziert, sicherheits- und
berechtigungsgeprüft, dokumentiert und in einem eigenen Git-Commit gesichert
ist. Nach Phase 4 folgen zusätzliche phasenübergreifende Integrationstests.
Dieser Auftrag ist abgeschlossen. Phase 5 wird in einem getrennten Auftrag
umgesetzt; Phase 6 und spätere Phasen bleiben ausgeschlossen.

**Phasenübergreifende Abnahme abgeschlossen (25.08.2026):** Der synthetische
End-to-End-Test verbindet bestätigte Familienbeziehung, Einwilligung und
Widerruf, geschützten Dokumentdownload, Beitrag/Kommentar, Event und
Reservierung. Die vollständigen App-, Push-Kit- und Vision-Suiten sowie
Compose-Neustart und PostgreSQL-Restore wurden zusätzlich ausgeführt. Phase 5
ist nicht begonnen.

**Phase-5-Abnahme abgeschlossen (25.08.2026):** Sichere JPEG-/PNG-Neucodierung,
Metadatenentfernung, manuelle Personenangaben, konservative Consent-Policy,
Moderation, geschützte Auslieferung, Meldung, Rückzug und idempotente Löschung
sind getestet. PostgreSQL und drei synthetische Bildableitungen wurden in
frische Volumes restauriert; SHA-256-Prüfsummen waren identisch. Phase 6 ist
nicht begonnen.

## Umsetzung Phase 1B

Der Modellvergleich verwendet einen gemeinsamen
Pipelinevertrag für Erkennung, Ausrichtung, Embedding, Vergleich,
Modellinformation und Health Check. Haar/LBPH dient nur als Baseline,
YuNet/SFace ist der bevorzugte lokale CPU-Kandidat. SCRFD/ArcFace bleibt bis zu
einer schriftlichen Erlaubnis für konkrete Gewichte deaktivierter
Vergleichskandidat; Gewichte werden weder eingecheckt noch ungeprüft zur
Laufzeit installiert. Bewertet werden Erkennungs-/Trefferqualität in den
vorgegebenen Bildsituationen sowie Laufzeit, Speicher und Modellgröße. Kein
Modell darf Treffer automatisch endgültig bestätigen.

## Bewusst zurückgestellt

Mehrere Schulen/SaaS, native Apps, Direktnachrichten, Video, Zahlungen,
Noten/Krankmeldungen, öffentliche Galerien, Cloud-Gesichtserkennung,
automatische endgültige Identifikation, allgemeines IAM, Kubernetes, Event Bus,
API-Gateway und Microservices für CRUD-Funktionen bleiben Nicht-Ziele, bis eine
neue ausdrückliche Entscheidung sie ändert.
