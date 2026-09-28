# Reproduzierbarer Buildkandidat – 28.09.2026

Dieser Nachweis schließt den vor der unabhängigen Schlussabnahme vereinbarten
Build-Schritt ab. Er dokumentiert zunächst einen lokal erzeugten Linux-/Docker-
Buildkandidaten. Staging wurde dabei nicht als visuelle Referenz verwendet.
Auf anschließenden ausdrücklichen Wunsch wurde derselbe Arbeitsstand zusätzlich
nach Staging ausgerollt; die eigenständige Abnahme gegen Mockups und
Anforderungen bleibt dennoch der nachfolgende Punkt 3.

## Build und Zuordnung

- Image: `klassid-redesign-candidate:20260928`
- Image-ID: `sha256:5304a4d56e8d8c65c4540b9c3a8f9e2bc4c31e7e4a9b969ba460d8196aafe0f1`
- Der unveränderte Projekt-Dockerfile führte `tailwind build` und danach
  `collectstatic` erfolgreich aus.
- Tailwind meldete Version 4.3.0 und einen erfolgreichen Abschluss.
- Django meldete im erzeugten Image: `System check identified no issues`.

## CSS-Artefakt

Quell-Bundle und von Django eingesammeltes Bundle im Image sind bytegleich:

- SHA-256: `de8042ba3bc57e28f6e15fd675d09577e141e718ce3d41ae50d58313efcc0725`
- Größe: 329.061 Bytes
- Enthalten: die aktuelle Token- und Designsystemschicht, unter anderem
  `--theme-panel-padding` und `.auth-benefit-icon`
- Nicht mehr enthalten: der veraltete Pseudohaken
  `.auth-benefits li:before`

Das erzeugte Bundle wurde unverändert als lokaler Abnahmestand nach
`app/theme/static/css/dist/styles.css` übernommen. Die Datei ist ein
generiertes, ignoriertes Buildartefakt und keine zweite CSS-Quelle.

## Browserprüfung des gebauten Bundles

Der vorhandene vollständige Browser-Smoke wurde danach genau einmal gegen
dieses Bundle wiederholt:

- 36 benannte Seiten bei 360, 768 und 1440 px
- 156 neu erzeugte Screenshots unter `qa-artifacts/redesign-current/`
- Chat-Aktionen sowie Emoji-/Sticker-Auswahl, Einstellungen, Themes,
  Designsystem und Avatar-Abläufe bestanden
- kein horizontaler Dokumentüberlauf
- keine JavaScript-Fehler; `browser-errors.json` enthält `[]`
- Abschlussmeldung: `PASS`

Die absichtlich ausgelösten HTTP-400-Antworten der ungültigen Theme- und
Chat-Asset-Formulare gehören zur Negativprüfung und sind kein Laufzeitfehler.
Visuell nachgesehen wurden Login, Designsystem auf Desktop und Mobil sowie der
Chatraum. Der Login zeigt mit dem neuen Bundle genau ein Vorteilssymbol je
Zeile.

## Ergebnis und Grenze

Der lokale Quellstand besitzt damit ein reproduzierbares Linux-Image und ein
eindeutig zugeordnetes CSS-/Static-Artefakt. Der technische Build-Block ist
abgeschlossen. Nicht enthalten sind echte Geräte-/Push-Integrationen oder die
unabhängige Schlussbewertung gegen alle Mockups; diese werden durch diesen
Nachweis ausdrücklich nicht vorweggenommen.

## Nachträgliches Staging-Deployment

Nach Abschluss der lokalen Prüfung wurde der Arbeitsstand auf ausdrücklichen
Wunsch nach Staging ausgerollt:

- Staging-Image: `klasse-5e-app:staging`
- Image-ID: `sha256:32977da3b92b5fc29ee3469f5b9c72697c697c5b1b6ad931a90979b72a97f670`
- Startzeit des App-Containers: 28.09.2026, 21:30 Uhr (Europe/Berlin)
- App-, PostgreSQL- und Vision-Container: gesund
- angewandte Migrationen: `chat.0012_chat_sticker_images` und
  `core.0041_portaltheme_semantic_tokens`
- Django-Systemcheck und ausstehende-Migrationen-Prüfung: ohne Befund
- öffentliche Endpunkte `/health/` und `/accounts/login/`: HTTP 200
- geschützter WebUntis-Einstieg `/mehr/webuntis/`: korrekte Weiterleitung zum
  Login
- öffentlich ausgeliefertes CSS:
  `/static/css/dist/styles.d05866ce058d.css?v=settings-v3`, HTTP 200,
  329.061 Bytes und derselbe SHA-256 wie der Buildkandidat

Die Staging-Konfiguration wurde vor dem Start geprüft; Datenbank und Volumes
sind vom Produktivsystem getrennt, der MFA-Bypass ist deaktiviert und die
biometrische Suche bleibt ausgeschaltet. Das Deployment dient der parallelen
Sichtprüfung, nicht als Referenz oder vorweggenommene Endabnahme.
