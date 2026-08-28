# Technische und organisatorische Maßnahmen

## Vertraulichkeit

- rollen-, klassen- und objektbezogene Serverprüfung; bestätigte Familienbeziehungen;
- sichere Passwort-Hashes, Sitzungen, CSRF-Schutz und MFA für privilegierte Konten;
- private Medienauslieferung, Secret-Verwaltung außerhalb Git, Fernet für externe Zugänge;
- minimaler administrativer Zugriff und regelmäßige Rechteprüfung.

## Integrität und Belastbarkeit

- versionierte Migrationen, Tests, kleine Commits und reproduzierbare Container-Builds;
- Transaktionen, Sperren und Idempotency für Synchronisation und Löschung;
- Eingabe-, Datei- und Zielhostprüfung; Abhängigkeits- und Sicherheitsupdates;
- getrennte Dienste und Ressourcenlimits für Bildverarbeitung.

## Verfügbarkeit und Wiederherstellung

- verschlüsselte rotierende Backups, dokumentierte Restore-Tests und Lösch-Tombstones;
- Zustandsüberwachung ohne Inhaltslogs, Fehlerklassifikation und Runbooks;
- Ausfall optionaler Dienste beeinträchtigt Kernfunktionen nicht.

## Datenschutz durch Technikgestaltung

- optionale Funktionen und Kategorien standardmäßig aus;
- granulare, aktuelle Einwilligung mit leichtem Widerruf;
- Datenminimierung, definierte Zweck- und Löschgrenzen;
- DSFA- und globales Freigabegate für Biometrie.

Die Maßnahmen werden mindestens jährlich und nach Sicherheitsvorfall, Architekturänderung oder neuem Anbieter auf Wirksamkeit geprüft.
