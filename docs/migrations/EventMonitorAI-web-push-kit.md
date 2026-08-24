# Spätere EventMonitorAI-Migration auf das Web-Push-Kit

Diese Notiz beschreibt nur eine mögliche spätere Migration. Phase 1A verändert
`EventMonitorAI` nicht.

## Ersetzbare technische Komponenten

- Der `pywebpush.webpush`-Aufruf und die HTTP-Statusklassifikation in
  `backend/app/services/push.py` können durch `WebPushSender` ersetzt werden.
- Das technische Schema aus Endpoint, `p256dh` und `auth` wird beim Versand in
  `Subscription` abgebildet.
- Registrierung, vorhandene Subscription und Abmeldung in `frontend/app.js`
  können die Funktionen aus `browser/push-client.mjs` verwenden.
- `frontend/sw.js` kann auf der neutralen Service-Worker-Vorlage aufbauen.

## Verbleibende EventMonitor-Fachlogik

EventMonitor entscheidet weiterhin über Benutzer, Tenant-Isolation,
Empfängerauswahl, Ereignistext, Datenschutz, Kategorie, Zielseite,
Versandzeitpunkt und Persistenz. Sein `PushSubscription`-SQLAlchemy-Modell und
die API-Authentisierung bleiben anwendungsintern. Ereignis-/Zeugenaktionen und
deren signierte Tokens sind ausdrücklich keine Aufgabe des Kits.

```python
dto = Subscription(
    endpoint=model.endpoint,
    p256dh=model.p256dh,
    auth=model.auth,
)
result = sender.send(dto, application_payload)
if result.status is DeliveryStatus.STALE:
    session.delete(model)
```

Temporäre Fehler dürfen nur nach EventMonitors eigener begrenzter Retry-Policy
erneut versucht werden. Permanente Fehler sollten sichtbar gezählt, aber nicht
mit Endpoint, Schlüsseln oder Payload protokolliert werden.

## Explizite Abmeldung

Eine authentisierte, idempotente DELETE- oder POST-Route sollte einen Endpoint
nur aus dem Konto/Tenant des aktuellen Benutzers löschen. Der Browser ruft
`unsubscribe` mit einem `deleteSubscription`-Callback auf; dieser sendet die
vor dem Browser-Unsubscribe gesicherten Subscription-Daten an diese Route.
Mehrfache Abmeldung und bereits fehlende Datensätze liefern Erfolg bzw. einen
neutralen idempotenten Status.

## Tests

Die bestehenden Token-/Zeugen- und Noise-Log-Tests bleiben erhalten. Ergänzt
werden sollten:

- DTO-Abbildung aus dem SQLAlchemy-Modell,
- Payload-Abbildung ohne unerlaubte sensible Inhalte,
- Auswertung aller vier Delivery-Status,
- Löschen nur bei `stale` und nur im richtigen Tenant,
- authentisierte, idempotente Abmeldung,
- Browser-Anmeldung, Abmeldung und Service-Worker-Klickziele,
- bestehende EventMonitor-Aktionstokens als weiterhin fachliche Tests.
