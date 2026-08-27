# WebUntis Datenschutzgrenzen

- Verschlüsselung: Fernet (authentifizierte symmetrische Verschlüsselung).
- Schlüssel: ausschließlich HomeOps-Referenz `secret://klasse-5e/webuntis/credential-encryption-key`.
- Persönliche Kategorien sind standardmäßig deaktiviert und einzeln widerrufbar.
- Klassenweite Daten werden von persönlichen Daten getrennt gespeichert.
- Push-Nachrichten enthalten keine Hausaufgabentexte, Nachrichten, Namen oder Tokens.
- JSESSIONID/JWT existieren nur während eines kontrollierten Abrufs im Prozessspeicher.
- Logs/Audit enthalten nur Aktion, Status und Zählwerte.
- Beim Entfernen werden Credentials, Sitzungsdaten, Freigaben und Importdaten entfernt.
- Rohantworten und Screenshots mit Schuldaten sind nicht Bestandteil des Repositories.
