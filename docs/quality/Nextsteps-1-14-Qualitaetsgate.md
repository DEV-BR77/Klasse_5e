# Qualitätsgate Aufgaben 1–14

Stand: 28. August 2026

## Ergebnis

Das technische Qualitätsgate ist bestanden. Die organisatorische/rechtliche Produktivfreigabe bleibt ausdrücklich offen, bis Verantwortlichkeit, echte Kontaktangaben, Rechtsgrundlagen, Auftragsverarbeiter und die Biometrie-DSFA freigegeben wurden.

## Prüfungen

| Prüfung | Ergebnis |
|---|---|
| Python-Kompilierung `app/src` | bestanden |
| Django `check` lokal und im App-Container | 0 Fehler |
| `makemigrations --check --dry-run` | keine Abweichung |
| Pytest vollständig | 76 bestanden |
| Ruff Lint | bestanden |
| Ruff Format (betroffene Bereiche) | bestanden |
| `git diff --check` | bestanden |
| Docker Compose Build | App- und Vision-Image gebaut |
| Rollout/Migration | `core.0003_onboarding_consent_catalog` angewendet |
| Containerzustand | App, PostgreSQL und Vision gesund |
| Template-Kompilierung | 19 UI-/Onboarding-/Datenschutztemplates geladen |
| Laufzeit-Default | 19 Zwecke; 0 Seed-Entscheidungen; 0 Push-Präferenzen; 0 aktive WebUntis-Funktionen; Biometrie aus |
| Secret-Diffprüfung | keine Klartext-Secrets; ausschließlich Feld-/Variablennamen |

## Abgedeckte Abnahmeszenarien

Neues Elternkonto, unbestätigte Beziehung, mehrere Sorgeberechtigte, Teilzustimmung, Ablehnung, Widerruf, neue Textversion, geschlossenes Biometrie-Gate, Tutorialfortschritt, öffentliche Datenschutzinformation sowie responsive/Forced-Colors-Regeln. Direkte Schritt-Sprünge werden serverseitig zurückgewiesen. WebUntis prüft die aktuelle Einwilligung beim Aktivieren und nochmals unmittelbar vor dem Abruf.

## Nicht als Fehler verdeckte Grenzen

- Die Verantwortlichkeitsentscheidung und echten Informationspflicht-Kontakte sind offene Beschlusspunkte und verhindern eine behauptete Produktivfreigabe.
- Biometrie bleibt global deaktiviert; ein Realbetrieb benötigt die genehmigte DSFA.
- Compose meldet bestehende Ownership-Hinweise für die beiden Vision-Volumes. Die Volumes wurden nicht gelöscht oder zurückgesetzt; der Dienst ist gesund.
- Pytest meldet nur Umgebungswarnungen zu fehlendem Host-`staticfiles`-Verzeichnis und nicht beschreibbarem Cache. Build/Container enthalten die gesammelten statischen Dateien; die Tests selbst bestehen vollständig.

## Zusätzliches Infrastruktur-Gate

- Vision-Dienst: 33 Tests bestanden, einschließlich Backup-/Restore-Nachweis.
- App und Vision laufen als UID/GID `10001:10001` mit schreibgeschütztem Root-Dateisystem; PostgreSQL-Prozesse laufen als UID `999` und schreiben in ihr Datenvolume.
- Kein Container veröffentlicht einen Host-Port; damit existiert auch keine öffentliche Development-Portbindung.
- Die offiziellen Rechtsquellen wurden am 28. August 2026 erfolgreich abgerufen. Interne Ergebnisdateien und UI-Templates sind vorhanden beziehungsweise kompilieren im App-Image.

## Laufzeit-Pilotnachweis

Nach dem Rollout wurden die zwei in `Nextsteps.md` ausdrücklich vorgegebenen realen Biometrie-Pilotentscheidungen ausschließlich in der laufenden Datenbank mit aktueller Textversion, Zeitpunkt, Entscheider, Umfang und minimiertem Audit erfasst. Es wurden keine Biometrieprofile, Bilder oder Embeddings erzeugt; das globale Biometrie-Gate blieb deaktiviert. Namen und Objektkennungen sind nicht Bestandteil dieses Git-Nachweises.
