# Anfrage zur WebUntis-JSON-Schnittstelle

Stand: 26.08.2026

## Versand

Die Anfrage soll zunächst gestellt werden an:

- `sekretariat@thgwob.de`

Mit der Bitte um Weiterleitung an die zuständige WebUntis-Administration und,
falls erforderlich, an den Datenschutzverantwortlichen beziehungsweise den
zuständigen Schulträger.

**Betreff:** Anfrage zu einem lesenden WebUntis-API-Zugang für das interne KlassenCMS der Klasse 5e

```
Guten Tag,

ich bin Elternvertreter der Klasse 5e und entwickle ehrenamtlich ein kleines,
nichtkommerzielles und selbst gehostetes KlassenCMS für die Eltern,
Schülerinnen und Schüler sowie die Klassenlehrkräfte unserer Klasse.

Das Portal ist nicht öffentlich zugänglich. Es verwendet persönliche
Einladungen und soll wichtige Klasseninformationen übersichtlich und
datensparsam an einem Ort darstellen. Dazu möchten wir gerne den Stundenplan
der Klasse 5e einschließlich freigegebener Änderungen aus WebUntis in
ausschließlich lesender Form übernehmen.

Nach der offiziellen Untis-Dokumentation kann für Schulprojekte und kleinere
Eigenentwicklungen auf Anfrage die WebUntis-JSON-Schnittstelle
(`jsonrpc.do`) beziehungsweise eine aktuell empfohlene Plattform-API genutzt
werden.

Könnten Sie uns bitte mitteilen, ob eine solche Anbindung für dieses Projekt
grundsätzlich genehmigt und eingerichtet werden kann?

Benötigt würden ausschließlich folgende Daten der Klasse 5e:

- reguläre Unterrichtsstunden mit Datum, Uhrzeit, Fach und Raum
- freigegebene Vertretungen, Raum- und Zeitänderungen
- Unterrichtsentfälle
- freigegebene Prüfungen beziehungsweise Klassenarbeiten
- freigegebene Informationen zur Stunde
- Ferien beziehungsweise unterrichtsfreie Zeiträume
- nach Möglichkeit die in WebUntis für die betroffenen Schülerinnen und
  Schüler sichtbaren Hausaufgaben

Nicht übernommen werden sollen insbesondere Noten, Abwesenheiten,
Entschuldigungen, Mitteilungen, Klassenbucheinträge, Kontaktdaten oder andere
Schülerstammdaten.

Für den nachhaltigen und sicheren Betrieb würden wir gerne einen eigenen,
ausschließlich lesenden WebUntis-Integrationszugang verwenden, der auf die
benötigten Daten der Klasse 5e beschränkt ist. Dieser Zugang soll unabhängig
von einem persönlichen Elternkonto bestehen. Sämtliche Zugangsdaten würden
ausschließlich in einer lokalen, geschützten Geheimnisverwaltung gespeichert
und weder in den Quellcode noch in Protokolle aufgenommen.

Die abgerufenen Daten würden nur im geschützten Klassenbereich angezeigt. Es
erfolgt keine Weitergabe an Werbe-, Analyse- oder Cloud-KI-Anbieter. Änderungen
könnten auf Wunsch der angemeldeten Nutzer durch eine datensparsame
Push-Nachricht angekündigt werden. Die Push-Nachricht selbst würde keine
Stundenplan-, Prüfungs- oder Hausaufgabentexte enthalten.

Der geplante Einsatz ist wie folgt begrenzt:

- Nutzung ausschließlich für die Klasse 5e
- Zugriff nur für eingeladene und berechtigte Klassenmitglieder
- keine kommerzielle Nutzung, Werbung oder sonstige Monetarisierung
- Betrieb ausschließlich auf einem privat verwalteten, selbst gehosteten Server
- ausschließlich lesender Zugriff
- keine Veränderung von Daten in WebUntis
- keine Weitergabe der Zugangsdaten oder abgerufenen Daten an Dritte
- keine öffentliche API und keine öffentliche Stundenplanansicht
- Protokollierung ohne Zugangsdaten und ohne sensible Inhaltsdaten
- Beendigung des Zugriffs und Löschung der importierten Daten nach Wegfall der Berechtigung

Bitte teilen Sie uns nach Möglichkeit auch mit:

1. Welche Schnittstelle wird für diesen Anwendungsfall aktuell empfohlen?
2. Kann ein eigener, auf die Klasse 5e und die genannten Daten beschränkter
   read-only Integrationszugang eingerichtet werden?
3. Welche der genannten Stundenplan-, Änderungs-, Prüfungs- und
   Hausaufgabendaten sind über diese Schnittstelle verfügbar?
4. Welche Authentisierung, Berechtigungen, Abrufintervalle und Rate-Limits
   gelten?
5. Ist alternativ oder ergänzend ein dafür freigegebenes persönliches
   iCal-Abonnement vorgesehen, und welche Daten enthält dieses am THG?
6. Ist eine zusätzliche Zustimmung der Stadt Wolfsburg, von Untis oder einer
   anderen zuständigen Stelle erforderlich?
7. Welche technischen Unterlagen, Datenschutzvereinbarungen oder sonstigen
   Nachweise werden benötigt?
8. Kann die Erlaubnis ohne jährliche Neubeantragung für die Dauer des
   bestehenden Klassenverbands gelten, beginnend in Klassenstufe 5 und
   längstens bis zum Abschluss beziehungsweise Ende der Klassenstufe 13?

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

Solange keine ausdrückliche Freigabe und kein geeigneter technischer Zugang
erteilt wurden, findet kein automatisierter WebUntis-Abruf statt. Persönliche
Eltern-Zugangsdaten, Screenshots mit Schülerdaten, iCal-Links und lokale
`.env`-Dateien dürfen nicht versendet oder in Git aufgenommen werden.

## Nachverfolgung

Anfrage am 26.08.2026 an das THG versendet. Der zuständige Administrator wurde
in Kopie gesetzt. Antwort und technische Freigabe stehen noch aus.
