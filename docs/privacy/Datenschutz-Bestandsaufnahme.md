# Datenschutz-Bestandsaufnahme

Stand: 28. August 2026. Diese Bestandsaufnahme beschreibt den vorgesehenen Betrieb; sie ersetzt weder die noch offene Festlegung der datenschutzrechtlichen Rollen noch eine Rechtsberatung.

## Datenarten und Zwecke

| Bereich | Daten | Zweck | Quelle | Empfänger/System | Aufbewahrung/Löschung |
|---|---|---|---|---|---|
| Konto und Anmeldung | Name, E-Mail, Passwort-Hash, MFA-Status, Sitzungsdaten | Authentisierung und Kontoschutz | betroffene Person/Einladung | Django, PostgreSQL | Kontoende; technische Protokolle nach Betriebskonzept |
| Person und Klasse | Name, Rolle, Klasse, Schuljahr | Klassenportal und Berechtigungen | Verwaltung/Eltern | Django, PostgreSQL | Schuljahreswechsel bzw. Zweckende |
| Familienbeziehungen | Eltern-Kind-Zuordnung, Prüfstatus, Verwaltungsrechte | rechtssichere Vertretung und Einwilligung | Einladung und Bestätigung | Django, PostgreSQL | Beziehung endet oder Konto wird gelöscht |
| Profil/Kontakt | E-Mail, Telefon, Sichtbarkeit, optionale Angaben | freiwilliger Kontakt innerhalb der Klasse | betroffene Person/Sorgeberechtigte | berechtigte Klassenmitglieder | Widerruf, Änderung oder Kontoende |
| Einwilligungen | Zweck, Textversion, Entscheidung, Zeitpunkt, Entscheider | Nachweis und technische Freigabe | betroffene Person/Sorgeberechtigte | Django, PostgreSQL | Nachweisfrist nach Löschkonzept; Inhalte werden nicht überschrieben |
| Beiträge, Termine, Kalender, Chat, Dokumente | Inhalts- und Metadaten, Autor, Zeitstempel | Klassenorganisation und Kommunikation | Nutzende/Redaktion | berechtigte Klassenmitglieder | fachliche Löschung bzw. Schuljahreswechsel |
| Push | Gerätekennung/Push-Endpunkt, Kategorien | freiwillige Benachrichtigung | Endgerät/Nutzende | Anwendung und ggf. Push-Anbieter | Abmeldung, Widerruf, ungültiger Endpunkt |
| Fotos und Galerie | Bild, Metadaten, Zuordnung, Freigabe | freiwillige Klassenchronik | Upload durch Berechtigte | berechtigte Klassenmitglieder | Widerruf, Löschwunsch, Zweckende |
| Biometrische Gesichtssuche | Referenzfoto, Gesichtsausschnitt, Embedding, Treffer | ausschließlich freiwillige private Fotosuche | ausdrückliche Einwilligung | lokaler Vision-Dienst | sofort bei Widerruf/Profilentfernung; standardmäßig deaktiviert |
| WebUntis | verschlüsselter Zugang, Funktionspräferenzen, technische Abrufdaten | optionaler, kontrollierter Import | Sorgeberechtigte/WebUntis | Django, thgwob.webuntis.com | Zugangsentfernung/Widerruf; keine dauerhafte Sitzung |
| Audit und Sicherheit | Ereignistyp, pseudonymisierte IDs, Zeitpunkt, Ergebnis | Missbrauchserkennung und Nachweis | Anwendung | Betriebsverantwortliche | begrenzte Frist nach Löschkonzept |
| Backups und Logs | verschlüsselte Datenbank-/Mediendateien; minimierte technische Logs | Wiederherstellung und Betriebssicherheit | Anwendung | lokales Backupziel | rotierende Fristen; Löschung läuft zeitversetzt aus Backups aus |

## Schutz- und Minimierungsgrundsätze

- Alle optionalen Funktionen beginnen deaktiviert. Ablehnung darf Kernfunktionen nicht sperren.
- Zugriff folgt Klasse, Rolle, bestätigter Familienbeziehung und – wo erforderlich – aktueller Einwilligung.
- Passwörter, WebUntis-Sitzungen, Klartext-Secrets, Fotos, Embeddings und produktive Datensätze gehören nie in Git oder Dokumentation.
- Sichtbarkeit und Exporte werden serverseitig geprüft. Direkte URLs umgehen die Regeln nicht.
- Widerruf ist mindestens so leicht erreichbar wie die Erteilung und löst funktionsspezifische Bereinigung aus.

## Noch organisatorisch zu entscheiden

Verantwortliche Stelle, Kontaktdaten, Rechtsgrundlagen je Pflichtfunktion, Auftragsverarbeiter, konkrete Fristen, Empfänger eines Löschersuchens und Freigabe der Pilotgruppe müssen vor Produktivbetrieb verbindlich beschlossen und in den Dokumenten ersetzt werden.

## Ergänzende Modulprüfung

- **Einladungen:** E-Mail, gehashter Einmaltoken, Ablauf und Nutzung; Klartexttoken nur bei Ausgabe, danach nicht rekonstruierbar.
- **MFA und Passkeys:** Authenticator-/Credential-Metadaten für Kontoschutz; Geheimnisse und private Schlüssel werden nicht protokolliert.
- **Rollen und Klassenmitgliedschaften:** Rolle, Gültigkeit, Schuljahr und Status steuern sämtliche Objektzugriffe.
- **Geschützte Downloads:** Dokument, Variante, Klasse und minimierter Abrufnachweis; keine öffentlichen Medienpfade.
- **Wollino-Speisepläne:** derzeit nur vorgesehene externe Quelle, nicht produktiv angebunden. Vor Aktivierung sind Zweck, Datenumfang, Zielhost, Frist und eigenes Gate festzulegen.
- **Schuljahreswechsel:** Mitgliedschaften, Rollen, Inhalte und Freigaben werden nicht stillschweigend in ein neues Jahr übernommen; Archivierung/Löschung folgt einer kontrollierten Abschlussprüfung.
- **Datenschutzverletzungen:** technische Administration sichert Fakten und begrenzt den Vorfall; Bewertung, Meldung und Betroffeneninformation trifft erst die festgelegte verantwortliche Stelle.

Damit sind auch vorgesehene, noch nicht aktivierte Module erfasst; ihre Erwähnung ist keine Betriebsfreigabe.
