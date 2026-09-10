# Technische Startfreigabe für die Abnahme

Stand: 11.09.2026. Dieser Nachweis erlaubt die Vorbereitung einer getrennten
Staging-Abnahme. Er ist **keine** Produktivfreigabe und ersetzt weder die
Geräteabnahme noch die Rechte- oder Datenschutzprüfung mit echten Beteiligten.

## Nachgewiesene technische Vorbedingungen

| Prüfung | Ergebnis |
| --- | --- |
| Django-Gesamtsuite | 332 bestanden, 0 Fehler, 0 übersprungen in 337,07 Sekunden |
| JUnit-Nachweis | `output/test-results/pytest-20260911-012530.xml` (lokal, absichtlich nicht versioniert) |
| Ruff | `ruff check src tests` bestanden |
| Django-Systemprüfung | `manage.py check` bestanden |
| Modell-/Migrationsprüfung | `manage.py makemigrations --check --dry-run` ohne Änderungen |
| Frontend-Assets | `manage.py tailwind build` bestanden |
| Git-Hygiene | `git diff --check` bestanden |
| Staging-Compose | getrennte Compose-Auflösung mit `.env.staging.example` geprüft; keine Container gestartet |

Die Tests verwenden eine isolierte lokale Testdatenbank. Sie greifen weder auf
Produktivdaten noch auf einen externen Dienst zu. Referenzdaten werden vor jedem
Testfall reproduzierbar wiederhergestellt, damit ein grünes Ergebnis nicht von
einem zufällig gefüllten lokalen Datenbestand abhängt.

## Für die Staging-Abnahme vorbereitet

- `compose.staging.yaml` erzwingt das eigene Compose-Projekt
  `klasse-5e-staging`, eigene PostgreSQL-, Medien- und Vision-Volumes,
  deaktivierte biometrische Suche sowie zwingend aktives MFA für Adminrollen.
- `.env.staging.example` dokumentiert ausschließlich separate Staging-Werte;
  die tatsächlich verwendete `.env.staging` ist von Git ausgeschlossen.
- `tools/Test-StagingConfiguration.ps1` prüft vor jedem Start die
  Compose-Auflösung, den Ausschluss des Produktivhosts und die getrennten
  Volumes. Der Befehl hat keine Start-, DNS- oder Caddy-Nebenwirkung.

## Bewusst noch nicht erledigt

Diese Schritte brauchen eine getrennte Infrastruktur- und Fachabnahme und
dürfen nicht aus diesem Quellstand heraus behauptet werden:

1. Einen Staging-Host festlegen, DNS und die Caddy-Route dafür separat
   einrichten sowie neue, ausschließlich dafür gültige Secrets hinterlegen.
2. Die leere Staging-Umgebung starten, migrieren und über HTTPS mit dem
   Staging-Host smoke-testen.
3. Die dokumentierten Abläufe auf Desktop, iPhone und Android durchführen:
   Anmeldung/Abmeldung, Profil speichern, Kindwechsel, Kontaktfreigaben und
   Widerruf, Kalender, Chat inklusive Kinderschutz, Familienansicht,
   Rechtewechsel und WebUntis-Einrichtung.
4. Erst nach protokolliertem Bestehen dieser Abnahme einen separaten,
   gesicherten Produktiv-Rollout entscheiden.
