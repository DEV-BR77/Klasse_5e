# Abwesenheiten und WebUntis-Meldung

Stand: 08.09.2026. Ausdrücklich freigegebener Folgeauftrag im Django-Modul
`webuntis`, ohne zusätzliche Dienste.

## Bedienung und Zugriff

Nach aktueller Einwilligung `webuntis_absences` führt der Link auf der Startseite
und bei der Schuldaten-Verbindung zu `/abwesenheiten/`. Sichtbar sind eigene
Kinder mit bestätigter, zeitlich gültiger Sorgeberechtigtenbeziehung,
Ansichtsrecht und aktiver Klasse im aktuellen Schuljahr. Administratorrollen
geben keinen Zugriff. Jedes Konto sieht ausschließlich Importe seiner eigenen
Verbindung und seine eigenen Entwürfe. Der WebUntis-Modulschalter gilt weiterhin.

Die persönliche Benachrichtigungstabelle enthält „Abwesenheiten“. In-App ist
standardmäßig aus. Bei aktivierter Präferenz entsteht für einen neuen Import
genau ein neutraler Glocken-/Postfachhinweis. Wiederholungen, Statuskorrekturen
und nachträgliche Aktivierung erzeugen keine weiteren Hinweise. Push bleibt
für diese Kategorie deaktiviert. Hinweise enthalten weder Kind noch Zeitraum,
Grund oder Freitext. Der Link prüft den aktuellen Zugriff erneut.

„Abwesenheit bei WebUntis melden“ ist ein ausdrücklicher Schreibvorgang. Er ist
nur sichtbar, wenn die Schule den WebUntis-Adapter samt Abwesenheitsmodul für
das Kind freigegeben hat, der aktuelle Benutzer rechtlich sorgeberechtigt ist,
die Beziehung, Klasse und Einwilligung aktuell sind und genau dieser Benutzer
einen eigenen, verschlüsselten Zugang beim Kind hinterlegt hat. Das im Dashboard
gewählte Kind wird vorgewählt; bei mehreren berechtigten Kindern erscheint eine
eindeutige Auswahl.

Der begrenzte Playwright-Transport öffnet ausschließlich den freigegebenen
WebUntis-Host, meldet sich mit diesem persönlichen Zugang an und bedient das
geprüfte Formular in der eingebetteten Abwesenheitsansicht. Er nutzt keine
WebUntis-Schreib-API. Eine zufällige Token-Zeile reserviert den Vorgang vor dem
Browserstart und verhindert Doppelmeldungen bei wiederholtem Absenden. Nach
dem einmaligen Klick auf „Speichern“ wird die Liste höchstens dreimal frisch
gelesen. Eine Erfolgsmeldung erscheint ausschließlich für einen neuen Eintrag
mit passendem Kind, Zeitraum und Anmerkung; vorhandene oder mehrdeutige Einträge
bestätigen nichts. Ein Timeout löst keinen zweiten Schreibversuch aus. Bei einem
unklaren Ergebnis bleibt die Meldung unbestätigt und die Oberfläche verweist
ohne Zugangsdaten oder Meldeinhalt direkt auf WebUntis.

Die Browserstrecke wurde mit dem echten Formular ohne Absenden geprüft. Die
automatisierten Tests verwenden ausschließlich synthetische Browserantworten;
ein echter Ende-zu-Ende-Test erfordert weiterhin einen Testzugang oder eine
ausdrücklich freigegebene reale Meldung.

Daneben kann „Lokalen Entwurf speichern“ weiterhin einen **nicht übertragenen Entwurf** anlegen:
Kind, Von/Bis (Standard heute), unabhängige optionale Uhrzeiten, Krank,
Arztbesuch oder Sonstiges und maximal 2.000 Zeichen Freitext. Ungültige
Intervalle werden abgewiesen. Entwürfe lassen sich löschen. HTML wird escaped,
POST benötigt CSRF. Die Ansicht erhält `private, no-store`.

## Importvertrag und Grenzen

Der bestehende lesende Adapter-Endpunkt `absences` wird über `sync_feature`
angebunden. Er benötigt aktive Feature-Präferenz, Einwilligung, Beziehung,
Konto und Klasse. Bestandsverbindungen erhalten migrationsseitig eine
**deaktivierte** Abwesenheitspräferenz. Freigabe erfolgt über die bestehenden
Einwilligungs-/Feature-Einstellungen.

Akzeptiert werden eine Liste, `{"absences": [...]}` oder
`{"data": {"absences": [...]}}`. Datensätze benötigen `id`, `studentId`,
`startDate`, `endDate`; optional sind `startTime`, `endTime`, `status`.
Datumsformate entsprechen dem bestehenden Importparser; Uhrzeiten sind HHMM
oder ISO-Uhrzeiten. Jede Schüler-ID muss zur Verbindung passen. Fehlende oder
fremde IDs, fehlerhafte Strukturen und Intervalle brechen die gesamte
Transaktion ab. Stabiler Schlüssel ist Verbindung plus externe ID.
Importiert werden die vergangenen 90 Tage einschließlich heute. Fehlende
Datensätze gelten nicht als Löschanweisung. Die Ansicht zeigt den Abrufstand.

Der Vertrag ist mit synthetischen Daten getestet. Konkrete Antwortform und
Leseberechtigung des Schulservers sind noch nicht live verifiziert. Fehlende
Leseberechtigung bleibt ein sichtbarer Adapterfehler; es gibt keinen
Browser-Fallback für Abwesenheiten. Die Ansicht bezeichnet Einträge als aus
WebUntis importierte Schuldaten: eine bestimmte Lehrkraft als Urheber wird
nicht ohne Quellmetadaten behauptet. Gründe, Diagnosen und Lehrkraftnamen
werden nicht aus der Quelle gespeichert.

Die Browsermeldung startet nie verdeckt: Sie folgt ausschließlich auf das
verbindliche Absenden im Formular. Freitext, Zugangsdaten und Browserrohdaten
werden nicht protokolliert. Die Protokollzeile enthält nur einen zufälligen Token,
den handelnden Benutzer, das Kind, eine Einweg-Prüfsumme und den neutralen
Ergebnisstatus.

## Migration und Aufbewahrung

Migration `webuntis.0010` ergänzt das minimierte, tokenbasierte
Sendeprotokoll additiv. Vor produktivem Upgrade gilt der vorhandene
Backup-/Restore-Prozess. Rollback auf `0009` entfernt die neue Tabelle und
deren Daten; bei Bedarf vorher einen geschützten Export erstellen.

`python manage.py purge_absences` täglich über den bestehenden Betriebslauf
aufrufen. Es löscht Importe älter als 90 Tage, Entwürfe und Sendeprotokolle nach 30 Tagen sowie
Datensätze ohne aktuelle Berechtigung/Einwilligung. Zugriff endet bereits vor
dem Löschlauf unmittelbar. Kontolöschung entfernt auch lokale Entwürfe;
Verbindungslöschung entfernt zugehörige Importe. Audit speichert beim Anlegen
eines Entwurfs nur Actor, Aktion und lokale Objekt-ID.

## Prüfung

`pytest tests/test_absences.py` prüft Opt-in, Idempotenz, atomaren Abbruch bei
fremden Kindern, Widerruf, Klassenablauf, Kontoaktivität, Datumsstandard,
Formularintervalle, XSS-Escaping, CSRF, Präferenzspeicherung und Löschung.
Zusätzlich prüfen die synthetischen Browserfälle die einmalige Übermittlung,
verzögerte Rücklesung, Timeout nach dem Schreibversuch, falsches Kind oder
Intervall, vorhandene ähnliche Einträge, deaktivierte Adapter und
Doppelabsenden. Tests verwenden keine echten Schuldaten oder Zugangsdaten.

Abschlussprüfung am 09.09.2026: Die vollständige Testsuite bestand mit 287
Tests. Django `check`, Migrationsabgleich und Ruff für die geänderten Module
sind ohne Befund. Der Docker-Build inklusive Playwright Chromium lief durch;
`webuntis.0010_absencesubmission` wurde produktiv migriert und der neue
App-Container ist gesund. Ein realer End-to-End-Test bleibt ausgeschlossen,
solange keine reale Abwesenheit ausdrücklich freigegeben wird.
