# Internes Web-Push-Kit

Kleines, frameworkneutrales Paket für Standards-basierten Web Push. Es kennt
weder Benutzer noch Mandanten, Datenbanken, Events oder Empfängerregeln. Die
Python-Distribution heißt `klasse5e-web-push-kit`; importiert wird sie nach
Python-Konvention als `web_push_kit`.

## Python-Schnittstelle

```python
from web_push_kit import (
    DeliveryStatus,
    NotificationPayload,
    Subscription,
    VapidConfig,
    WebPushSender,
)

subscription = Subscription(endpoint, p256dh, auth)
payload = NotificationPayload(
    title="Neue Mitteilung",
    body="Details sind nach der Anmeldung verfügbar.",
    url="/messages/42",
    category="general",
    message_id="msg-42",
)
sender = WebPushSender(VapidConfig(public_key, private_key, "mailto:admin@example.invalid"))
result = sender.send(subscription, payload)

if result.status is DeliveryStatus.STALE:
    application_repository.delete_by_endpoint(subscription.endpoint)
elif result.status is DeliveryStatus.TEMPORARY_FAILURE:
    application_retry_policy.consider_retry(subscription)
```

Das Kit löscht und persistiert nichts. `DeliveryResult` enthält nur Status,
optionalen HTTP-Status und einen stabilen, nicht sensitiven Grund. Endpoint,
Schlüssel, Payload und Transportfehlermeldung werden nicht übernommen.

Statuszuordnung:

- Erfolg: `delivered`
- HTTP 404/410: `stale`
- fehlende Antwort, Timeout, 408/425/429 oder 5xx: `temporary_failure`
- andere 4xx und unerwartete Programm-/Transportfehler: `permanent_failure`

Die aufrufende Anwendung entscheidet über Löschen und Wiederholen. Der Sender
ist synchron; Warteschlangen und Worker gehören nicht in dieses Paket.

## Payload-Vertrag

Erforderlich sind `title` (120), `body` (500), `url` (2048), `category` (64)
und `message_id` (128 Zeichen). Optional sind `tag` (128), `icon` (2048) und
höchstens zwei neutrale Aktionen mit ID (64), Titel (80) und optionaler URL.
URLs sind interne absolute Pfade (`/…`) oder HTTPS-URLs ohne Zugangsdaten.
Das kompakte UTF-8-JSON darf 3072 Bytes nicht überschreiten. Ungültige Werte
erzeugen vor dem Versand `TypeError` oder `ValueError`.

## Browser

`browser/push-client.mjs` exportiert:

- `supportStatus(environment?)`
- `registerServiceWorker(scriptUrl, options?)`
- `getExistingSubscription(registration)`
- `subscribe({registration, publicKey, saveSubscription, environment?})`
- `unsubscribe({registration, deleteSubscription})`

`saveSubscription` und `deleteSubscription` werden von der Anwendung
bereitgestellt; es gibt keine fest eingebaute API-Route. `subscribe` darf nur
aus einer ausdrücklichen Benutzeraktion aufgerufen werden. Die Abmeldung liest
die Daten vor `PushSubscription.unsubscribe()`, lässt den authentisierten
Server-Callback den Datensatz idempotent entfernen und kündigt anschließend
die Browser-Subscription. Fehlt sie bereits, liefert die Funktion idempotent
`not_subscribed`.

`browser/service-worker.js` ist eine kopierbare Classic-Worker-Vorlage. Sie
akzeptiert standardmäßig nur Ziele derselben Origin. Zusätzliche HTTPS-Origins
müssen explizit in `WEB_PUSH_ALLOWED_ORIGINS` eingetragen werden. Bei Klick
wird ein vorhandenes gleich-originiges Fenster navigiert und fokussiert oder
ein neues geöffnet. Ungültige Payloads werden still verworfen.

`pushsubscriptionchange` ist browserübergreifend und bei beendetem Browser
nicht zuverlässig genug für eine Zusage. Die Anwendung soll beim nächsten
regulären Aufruf die bestehende Subscription lesen und gegebenenfalls nach
einer Benutzeraktion neu abonnieren bzw. erneut an den Server übertragen.

## Datenschutz und Sicherheit

- Browser-Pushdienste sind externe technische Zusteller.
- Push-Nachrichten enthalten standardmäßig keine sensiblen Details. Diese
  werden erst nach Anmeldung an der Ziel-URL angezeigt.
- Endpoint, `p256dh` und `auth` sind vertrauliche technische Daten und dürfen
  nicht protokolliert werden.
- Der VAPID Private Key bleibt ausschließlich serverseitig und kommt aus der
  Geheimnisverwaltung; `.env.example` enthält bewusst keine Schlüsselwerte.
- Die Anwendung muss erlaubte Ziel-URLs vor offenen Weiterleitungen schützen.
- Payloads bleiben klein; Browser- und Pushdienstgrenzen können enger sein.
- Zustellung ist nicht garantiert. Push ist kein revisionssicherer oder für
  Notfälle geeigneter Kommunikationskanal.

Signierte Aktionstoken sind absichtlich nicht enthalten. Autorisierung und
fachliche Claims gehören in die einbettende Anwendung; Links sollten im
Regelfall eine Anmeldung verlangen.

## Entwicklung

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
node --test browser/tests/*.test.mjs
```

Für eine echte Browserintegration sind zusätzlich manuell zu prüfen: iOS-PWA
nach Installation auf dem Home-Bildschirm, Android/Chromium, Permission-UX,
Schlüsselrotation, erneute Registrierung und serverseitig authentisierte,
idempotente An-/Abmelde-Endpunkte.
