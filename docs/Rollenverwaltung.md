# Persönliche Rollenverwaltung

Portalverwaltung → Rollenverwaltung (`/verwaltung/rollen/`) zeigt alle Benutzerkonten,
aktive Rollenzuweisungen und den ausgewählten Elternvertreter-Chat je Klasse.
Globale Haupt-/stellvertretende Administratoren und aktive Superuser dürfen hier
Portal-Admins und Elternvertretungen vergeben oder entziehen. Schul-/Klassenadmins
erhalten keinen Zugriff auf die globale Benutzerliste oder Rollenvergabe.

„Portal-Admin“ verwendet die bestehende globale Rolle `primary_admin`; Staff- und
Superuserrechte werden nicht vergeben. Die bestehende MFA-Middleware verlangt nach
Vergabe eine starke Anmeldung. Die eigene globale Adminrolle kann über diese Seite
nicht entzogen werden. Andere persönliche Rollen bleiben unverändert.

Elternvertretungen (`parent_representative`) gelten für genau eine Klasse und
benötigen beim Vergeben einen aktuell gültigen Klassenzugang. Mehrere Personen,
einschließlich Stellvertretungen, können dieselbe Rolle erhalten.

Ein bestehender, nicht eventgebundener Chat wird explizit als Elternvertreter-Chat
ausgewählt. Eine neue Auswahl ersetzt die bisherige Zuordnung der Klasse. Keine
automatische Erkennung anhand des Raumtitels; die bisherigen Chat-Zugriffsrechte bleiben.
Neue Beiträge erzeugen in derselben Transaktion je berechtigter Elternvertretung
eine Glockenbenachrichtigung. Eigene Beiträge, fremde Klassen, gesperrte Konten und
entzogene Rollen/Mitgliedschaften werden ausgeschlossen. Die Meldung enthält keinen
Nachrichtentext. Wiederholung ist dedupliziert. Diese rollenbezogenen In-App-Meldungen
sind unabhängig vom optionalen Browser-Push und dessen persönlichen Präferenzen.

Migrationen: `core.0023` ergänzt die Rollenauswahl, `chat.0006` ergänzt die standardmäßig
deaktivierte Chatzuordnung. Bestehende Rollen und Räume bleiben erhalten. Vor einem
Deployment reguläres Backup und Migrationen durchführen; die Zuordnung erfolgt bewusst
nach der Veröffentlichung über die Oberfläche.

Prüfung: `test_role_management.py` sowie bestehende Chat-/Portalverwaltungstests.
