# Abwesenheiten und lokaler Meldeprototyp

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

„Abwesenheit melden“ speichert einen **lokalen, nicht übertragenen Entwurf**:
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

**Schreiben nach WebUntis ist nicht implementiert.** Es gibt keinen Sendejob,
Submit-Endpunkt, Browserstart oder versteckten Versand. Ein späterer gemeinsamer
Browserdurchlauf muss Kind, Zeitraum und Inhalt überprüfen und die Schulmeldung
ausdrücklich ausführen. Ein lokaler Entwurf bestätigt keine Meldung bei der Schule.

## Migration und Aufbewahrung

Migration `webuntis.0009` ergänzt `WebUntisAbsence`, `AbsenceDraft` und die
Feature-Auswahl additiv. Vor produktivem Upgrade gilt der vorhandene
Backup-/Restore-Prozess. Rollback auf `0008` entfernt die neuen Tabellen und
deren Daten; bei Bedarf vorher einen geschützten Export erstellen.

`python manage.py purge_absences` täglich über den bestehenden Betriebslauf
aufrufen. Es löscht Importe älter als 90 Tage, Entwürfe nach 30 Tagen sowie
Datensätze ohne aktuelle Berechtigung/Einwilligung. Zugriff endet bereits vor
dem Löschlauf unmittelbar. Kontolöschung entfernt auch lokale Entwürfe;
Verbindungslöschung entfernt zugehörige Importe. Audit speichert beim Anlegen
eines Entwurfs nur Actor, Aktion und lokale Objekt-ID.

## Prüfung

`pytest tests/test_absences.py` prüft Opt-in, Idempotenz, atomaren Abbruch bei
fremden Kindern, Widerruf, Klassenablauf, Kontoaktivität, Datumsstandard,
Formularintervalle, XSS-Escaping, CSRF, Präferenzspeicherung und Löschung.
WebUntis-, Profil-/Benachrichtigungs- und Familienkontexttests dienen der
Regression. Tests verwenden keine echten Schuldaten oder Zugangsdaten.
Ein Live-Import, Git-Push und Deployment sind nicht ausgeführt.

Abschlussprüfung am 08.09.2026: 62 Tests in den neun genannten Fach-/
Regressionsmodulen bestanden. Django `check`, Migrationsabgleich und Ruff für
neue Module/Migration/Tests sind ohne Befund. Die Testdatenbank wurde mit allen
Migrationen auf SQLite aufgebaut. Warnungen betreffen ausschließlich das im
Test-Worktree noch nicht durch `collectstatic` erzeugte Staticfiles-Verzeichnis.
PostgreSQL-/Docker- und Live-Browser-Abnahme bleiben vor Deployment erforderlich.
