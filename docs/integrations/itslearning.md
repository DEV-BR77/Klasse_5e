# itslearning-Integration

## Umfang

Der Bereich `/itslearning/` ist ein persoenlicher, kindbezogener Leseadapter.
Kurs-RSS-Feeds und der persoenliche iCal-Feed werden ausschliesslich von
`wob.itslearning.com` abgerufen, normalisiert und lokal angezeigt. Die in den
Feed-Adressen enthaltenen GUIDs sowie Benutzername und Passwort liegen
verschluesselt in PostgreSQL. Lokale Zugangsdaten-Dateien werden weder
eingelesen noch eingecheckt; die Zugangsdaten werden durch einen berechtigten
Elternteil in **Familie -> itslearning** hinterlegt.

Nachrichten sind bewusst noch nicht automatisiert. itslearning stellt dafuer im
geprueften Portal keinen stabilen RSS-/iCal-Leseweg bereit. Ein
passwortgestuetztes Screen-Scraping waere fragil und wird nicht als Hintergrundjob
betrieben.

## WebDAV

Fuer jedes bestaetigte, verwaltbare Kind kann ein eigener WebDAV-Bereich mit
100 MiB Standardquota eingerichtet werden. Der Bereich nutzt ein separates
WebDAV-Kennwort, HTTP Basic Auth nur ueber die oeffentliche HTTPS-Verbindung und
eine nicht erratbare UUID im Pfad. Unterstuetzt werden `OPTIONS`, `PROPFIND`,
`GET`, `HEAD`, `PUT`, `MKCOL` und das Loeschen leerer Ordner
beziehungsweise einzelner Dateien. Die Belegung ist fuer Eltern im
Speicherbereich und fuer Administratoren im Django-Admin sichtbar.

WebDAV-Daten liegen unter `WEBDAV_ROOT` (Standard: `MEDIA_ROOT/webdav`) und
damit im bestehenden persistenten Medienvolume. Sie muessen in Backup und
Restore des Medienvolumes einbezogen werden.

## Betrieb

- Migration `itslearning.0001_initial` ausfuehren.
- `ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY` als eigenen Fernet-Schluessel setzen.
  Der Schluessel darf nicht mit dem WebUntis-Schluessel geteilt werden.
- Nach dem Deployment `collectstatic` ausfuehren.
- Fuer automatische Aktualisierung ist spaeter ein periodischer Aufruf von
  `sync_itslearning` einzuplanen; die erste Version aktualisiert manuell.

## Sicherheit

- Feed- und Kalenderlinks werden ausschliesslich per HTTPS von
  `wob.itslearning.com` uebernommen.
- Feed-Antworten sind auf 2 MiB und RSS auf 100 Eintraege begrenzt.
- WebDAV-Pfade werden kanonisiert; `..` und Ausbruch aus dem Kindverzeichnis
  werden abgewiesen.
- Die Quota-Pruefung verwendet die tatsaechlich empfangene Nutzlast.
- Synchronisationsfehler werden nur als neutrale Fehlercodes gespeichert.
- Verwaltungsbefehle verwenden interne IDs; Passwoerter werden nur ueber stdin gelesen.
- Secrets und Feed-Tokens erscheinen nicht in Listenansichten oder Logs.
