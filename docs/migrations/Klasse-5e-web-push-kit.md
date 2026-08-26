# Einbindung des Web-Push-Kits in Klasse 5e

Diese Dokumentation beschreibt ausschließlich, wie das interne
`klasse5e-web-push-kit` im Klassenportal verwendet wird. Das Kit ist ein
frameworkneutrales Python-Paket unter `packages/web-push-kit`; Benutzerkonten,
Klassenrechte, Empfängerauswahl und Persistenz bleiben Aufgaben der
Django-Anwendung.

## Verantwortungsgrenze

Das Web-Push-Kit stellt die technischen Transportbausteine bereit:

- `Subscription` für Browser-Endpoint, `p256dh` und `auth`;
- `NotificationPayload` für die begrenzte Nachricht;
- `VapidConfig` für öffentliche und private VAPID-Daten;
- `WebPushSender` für den eigentlichen Versand;
- `DeliveryResult` und `DeliveryStatus` für die neutrale Auswertung;
- Browser-Helfer für Registrierung, Anmeldung und Abmeldung;
- eine neutrale Service-Worker-Vorlage für Anzeige und Klickziel.

Das Kit kennt keine Benutzer, Kinder, Familien, Klassen, Rollen, Termine,
Chatnachrichten oder Stundenpläne. Es speichert und löscht auch keine
Subscriptions. Dadurch kann die Klasse-5e-Anwendung alle fachlichen und
datenschutzbezogenen Entscheidungen selbst erzwingen.

## Serverseitiger Versand mit `WebPushSender`

Die Django-Anwendung erzeugt den Sender aus der serverseitigen
VAPID-Konfiguration. Der private VAPID-Schlüssel stammt ausschließlich aus der
lokalen Geheimnisverwaltung und wird weder an den Browser übertragen noch in
Git oder Logs geschrieben.

```python
from web_push_kit import VapidConfig, WebPushSender

sender = WebPushSender(
    VapidConfig(
        public_key=vapid_public_key,
        private_key=vapid_private_key,
        subject=vapid_subject,
    )
)
```

Der aufrufende Fachdienst ermittelt zuerst die berechtigten Empfänger und ihre
aktivierten `PushSubscription`-Datensätze. Jeder Datenbankdatensatz wird erst
unmittelbar vor dem Versand in das neutrale Kit-DTO übertragen:

```python
from web_push_kit import NotificationPayload, Subscription

result = sender.send(
    Subscription(
        endpoint=stored.endpoint,
        p256dh=stored.p256dh,
        auth=stored.auth,
    ),
    NotificationPayload(
        title="Klasse 5e",
        body="Es gibt einen neuen Hinweis.",
        url=f"/events/{event.id}/",
        category="event",
        message_id=f"event-{event.id}-{reason}",
    ),
)
```

Der Sender ruft intern den standards-basierten Web-Push-Transport auf und gibt
nur ein strukturiertes, nicht sensitives Ergebnis zurück. Transportfehlertexte,
Endpoint, Schlüssel und Payload werden nicht in `DeliveryResult` übernommen.

## Auswertung der Zustellung

`WebPushSender` unterscheidet vier Ergebnisse:

| Status | Bedeutung | Reaktion der Klasse-5e-Anwendung |
|---|---|---|
| `delivered` | Pushdienst hat die Nachricht angenommen | fachliche Zustellung als ausgelöst erfassen |
| `stale` | Subscription ist bei HTTP 404/410 nicht mehr gültig | betroffenen Datenbankdatensatz löschen |
| `temporary_failure` | Timeout, Rate-Limit oder vorübergehender Dienstfehler | keine Zustellung verbuchen; später begrenzt erneut versuchen |
| `permanent_failure` | dauerhafte Ablehnung oder ungültiger Versand | nicht automatisch endlos wiederholen; nicht sensitiv protokollieren |

Das Kit trifft diese Entscheidungen nicht selbst. Die Django-Anwendung wertet
den Status aus und bleibt Eigentümerin der gespeicherten Subscription:

```python
from web_push_kit import DeliveryStatus

if result.status is DeliveryStatus.STALE:
    stored.delete()
elif result.status is DeliveryStatus.TEMPORARY_FAILURE:
    return "temporary_failure"
```

## Derzeitige fachliche Verwendung

Die erste konkrete Integration befindet sich im Eventmodul unter
`app/src/klasse5e/events/services.py`. `send_event_reminder`:

1. prüft anhand von `ReminderDelivery`, ob derselbe Anlass für denselben
   Termin und Benutzer bereits verarbeitet wurde;
2. liest nur aktivierte Subscriptions dieses Benutzers;
3. versendet über den injizierten `WebPushSender` eine datensparsame
   Ereigniserinnerung;
4. entfernt ausschließlich nach `stale` die nicht mehr gültige Subscription;
5. verbucht bei einem temporären Fehler noch keine erfolgreiche Erinnerung;
6. erzeugt erst nach der Verarbeitung den deduplizierenden
   `ReminderDelivery`-Datensatz.

Der Sender wird als Abhängigkeit übergeben. Dadurch bleiben Tests vollständig
lokal und benötigen weder echte Pushdienste noch VAPID-Schlüssel.

Weitere Klassenmodule wie Chat, Kalender oder spätere externe
Stundenplanänderungen dürfen denselben Sender verwenden. Sie benötigen jedoch
jeweils eigene Empfängerregeln, Opt-in-Präferenzen, Deduplizierung und
Nachrichtentypen. Das Kit darf diese Fachlogik nicht übernehmen.

## Subscription-Verwaltung in Django

`PushSubscription` gehört zum authentisierten Benutzerkonto und speichert:

- den Endpoint sowie seinen SHA-256-Hash;
- `p256dh` und `auth`;
- den Aktivierungsstatus;
- den Erstellungszeitpunkt.

Der Endpoint-Hash verhindert doppelte Datensätze und ermöglicht eine gezielte
idempotente Abmeldung. Die authentisierte Django-Route akzeptiert:

- `POST` zum Anlegen beziehungsweise Aktualisieren der eigenen Subscription;
- `DELETE` zum Entfernen ausschließlich der eigenen Subscription.

Die Browser-Helfer aus `packages/web-push-kit/browser/push-client.mjs` erhalten
diese Routen als Anwendungs-Callbacks. Eine Permission-Anfrage wird nur durch
eine ausdrückliche Benutzeraktion ausgelöst. Bei der Abmeldung werden die
Subscription-Daten zuerst serverseitig entfernt und anschließend im Browser
gekündigt.

## Datenschutz und Nachrichtengestaltung

Push ist nur ein freiwilliger Hinweis, kein revisionssicherer
Kommunikationskanal. Nachrichten der Klasse 5e enthalten standardmäßig keine:

- Namen von Kindern oder Familien;
- Chatnachrichten;
- Foto- oder Biometrieinformationen;
- Hausaufgaben- oder Prüfungstexte;
- vollständigen Stundenplanänderungen;
- Kontakt- oder Profildaten.

Die Nachricht weist lediglich auf eine neue Information hin. Einzelheiten
werden erst nach erfolgreicher Anmeldung über einen internen Pfad derselben
Origin angezeigt. Externe oder offene Weiterleitungsziele sind nicht zulässig.

Browser-Pushdienste sind externe technische Zusteller. Deshalb werden Payloads
klein und inhaltsarm gehalten. Zustellung ist nicht garantiert, und
sicherheitskritische oder dringende Mitteilungen dürfen nicht ausschließlich
über Push erfolgen.

## Betrieb ohne zusätzlichen Dienst

Das Web-Push-Kit ist Bibliothekscode im Django-App-Image und erhält keinen
eigenen Container. Für das geringe Klassenvolumen werden Erinnerungsanlässe
durch eindeutige Datenbankeinträge dedupliziert und über einen expliziten
Management- beziehungsweise Deployment-Aufruf verarbeitet. Redis, Celery und
ein dauerhafter zusätzlicher Worker sind dafür derzeit nicht erforderlich.

## Tests

Die Paket- und Anwendungstests decken mindestens ab:

- Validierung von Subscription, VAPID-Konfiguration und Payload;
- Begrenzung von Texten, Aktionen, Zielen und JSON-Größe;
- Zuordnung von Erfolg, 404/410, temporären und permanenten Fehlern;
- Schutz sensitiver Werte in Objekt-Repräsentationen und Ergebnissen;
- Löschen einer Subscription ausschließlich bei `stale`;
- Erhalt der Subscription bei einem temporären Fehler;
- Deduplizierung derselben Eventerinnerung;
- authentisierte, benutzergebundene An- und Abmeldung;
- Browser-Anmeldung, Abmeldung und sichere Service-Worker-Klickziele.

Echte Browserintegration, iOS-PWA, Android/Chromium, Permission-UX,
Schlüsselrotation und erneute Registrierung bleiben praktische
Integrationsprüfungen vor dem Produktivbetrieb.

