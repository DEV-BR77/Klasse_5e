# Anfrage zur WebUntis-JSON-Schnittstelle

Stand: 26.08.2026

Empfohlener erster Empfänger: `sekretariat@thgwob.de` mit der Bitte um
Weiterleitung an die zuständige WebUntis-Administration beziehungsweise den
Datenschutzverantwortlichen der Schule.

## Versandfertige Fassung

**Betreff:** Anfrage zu einem lesenden WebUntis-API-Zugang für das interne KlassenCMS der Klasse 5e

```text
Guten Tag,

ich bin Elternvertreter der Klasse 5e und entwickle ehrenamtlich ein kleines,
nichtkommerzielles und selbst gehostetes KlassenCMS für die Eltern,
Schülerinnen und Schüler sowie die Klassenlehrkräfte unserer Klasse.

Das Portal ist nicht öffentlich zugänglich. Es verwendet persönliche
Einladungen und soll wichtige Klasseninformationen übersichtlich und
datensparsam darstellen. Dazu möchten wir gerne den Stundenplan der Klasse 5e
einschließlich freigegebener Änderungen aus WebUntis in ausschließlich
lesender Form übernehmen.

Nach der offiziellen Untis-Dokumentation kann für Schulprojekte und kleinere
Eigenentwicklungen auf Anfrage eine WebUntis-JSON-Schnittstelle
(`jsonrpc.do`) beziehungsweise eine aktuell empfohlene Plattform-API genutzt
werden.

Könnten Sie uns bitte mitteilen, ob eine solche Anbindung für dieses Projekt
grundsätzlich genehmigt und eingerichtet werden kann?

Benötigt würden ausschließlich folgende Daten der Klasse 5e:

- reguläre Unterrichtsstunden mit Datum, Uhrzeit, Fach und Raum,
- freigegebene Vertretungen, Raum- und Zeitänderungen,
- Unterrichtsentfälle,
- freigegebene Prüfungen beziehungsweise Klassenarbeiten,
- freigegebene Informationen zur Stunde,
- Ferien beziehungsweise unterrichtsfreie Zeiträume,
- nach Möglichkeit die in WebUntis für die betroffenen Schülerinnen und
  Schüler sichtbaren Hausaufgaben.

Nicht übernommen werden sollen insbesondere Noten, Abwesenheiten,
Entschuldigungen, Mitteilungen, Klassenbucheinträge, Kontaktdaten oder andere
Schülerstammdaten.

Für den Betrieb wünschen wir uns nach Möglichkeit einen eigenen, auf diese
Daten und die Klasse 5e begrenzten Lesezugang. Ein persönliches Elternkonto
soll nicht als dauerhafter technischer Zugang verwendet werden. Zugangsdaten
würden ausschließlich verschlüsselt beziehungsweise über eine lokale
Geheimnisverwaltung bereitgestellt und weder in den Quellcode noch in
Protokolle aufgenommen.

Die Daten würden nur im geschützten Klassenbereich angezeigt. Es erfolgt keine
Weitergabe an Werbe-, Analyse- oder Cloud-KI-Anbieter. Änderungen könnten auf
Wunsch der angemeldeten Nutzer durch eine datensparsame Push-Nachricht ohne
Stundenplan-, Prüfungs- oder Hausaufgabentext angekündigt werden.

Bitte teilen Sie uns nach Möglichkeit auch mit:

1. welche Schnittstelle für diesen Anwendungsfall aktuell empfohlen wird,
2. ob ein eigener read-only Integrationszugang eingerichtet werden kann,
3. welche der oben genannten Daten darüber verfügbar sind,
4. welche Authentisierung, Berechtigungen und Rate-Limits gelten,
5. ob eine zusätzliche Zustimmung der Stadt Wolfsburg, von Untis oder einer
   anderen zuständigen Stelle erforderlich ist,
6. welche technischen Unterlagen oder Vereinbarungen wir dafür benötigen.

Bis zu einer ausdrücklichen Freigabe findet kein automatisierter Abruf statt.
Gerne stelle ich die technische Beschreibung, das Datenschutzkonzept oder den
aktuellen Entwicklungsstand des Projekts zur Verfügung.

Das öffentliche Entwicklungsrepository finden Sie hier:
https://github.com/DEV-BR77/Klasse_5e

Vielen Dank für Ihre Unterstützung und gerne auch für die Weiterleitung an die
zuständige Stelle.

Mit freundlichen Grüßen

Bjoern Radke
Elternvertreter der Klasse 5e
```

## Hinweis für den Versand

Keine WebUntis-Zugangsdaten, Screenshots mit Schülerdaten, iCal-Links oder
`.env`-Dateien mitsenden. Falls die Schule technische Nachweise benötigt,
zunächst nur auf das öffentliche Repository verweisen und konkrete Unterlagen
erst nach Rückmeldung gezielt bereitstellen.
