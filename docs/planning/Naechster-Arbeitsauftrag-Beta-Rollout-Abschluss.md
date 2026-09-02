# Nächster Arbeitsauftrag: KlassID-Beta-Rollout abschließen

Setze den Eltern-Beta-Auftrag ab dem aktuellen `origin/main` fort. Lies zuerst
`AGENTS.md`, die HomeOps-Vorgaben, `PROJECT.md`, `docs/Architecture.md`,
`docs/DecisionLog.md`, `docs/Roadmap.md` und
`docs/releases/0.2.0-beta.1.md`. Private Dateien und Secrets niemals ausgeben
oder committen.

## Verbindlicher Iststand

- Das lokale Qualitätsgate war grün: 147 App-/Push-Tests, 33 Vision-Tests,
  Ruff, compileall, Django-Checks, Migrationsdrift, Docker-Build und responsive
  Browser-E2E.
- Der reale WebUntis-Abruf war erfolgreich; nur anonymisierte Anzahlen sind im
  Releaseprotokoll festgehalten.
- Das Vorher-Backup liegt lokal unter
  `D:\Backups\Klasse_5e\pre-beta-20260902-004003` und enthält PostgreSQL,
  Medien, Vision-Daten, Container-/Image-Metadaten, Caddy, DNS und Prüfsummen.
- IONOS verwendet jetzt `https://api.hosting.ionos.com/dns/v1`. Die A-Records
  von `klassid.de` und `5e.klassid.de` zeigen auf `77.22.86.157`; die alten
  Parking-AAAA-Einträge sind inaktiv. Resend-DKIM sowie `rsend`- und
  `send`-CNAME wurden ergänzt.
- Der zuvor verwendete IONOS-Browsertab stand bei der Übergabe unerwartet auf
  `/keys/copy`. Der bereits in HomeOps gespeicherte Schlüssel funktioniert und
  wurde für Backup und DNS-Änderung genutzt. Im nächsten Lauf im
  Entwicklerportal prüfen, ob versehentlich ein zusätzlicher unbenutzter
  Schlüssel erzeugt wurde; nur nach eindeutigem Abgleich und neuem Backup
  gegebenenfalls widerrufen. Keine dort sichtbaren Schlüsselwerte ausgeben.
- Caddy leitet `klassid.de` und `5e.eventmonitor.eu` dauerhaft auf
  `https://5e.klassid.de` um und hat Zertifikate für Root und Klassenhost
  erfolgreich bezogen. Die Caddy-Änderung liegt im lokalen Repository
  `D:\Development\Repos\HomeInfrastructure`; dieses Repository hatte beim
  Übergabestand kein Git-Remote.
- Ein frisches VAPID-Schlüsselpaar ist DPAPI-verschlüsselt als
  `secret://projects/klasse-5e/vapid_private_key` und
  `secret://projects/klasse-5e/vapid_public_key` gespeichert und wird an die
  produktive App übergeben.
- Das korrigierte Image `klasse-5e-app:0.2.0b1` läuft produktiv und gesund;
  die Migrationen wurden angewendet. Ein erster Startversuch war wegen eines
  CRLF-Shebangs fehlgeschlagen, wurde sofort zurückgerollt und durch
  Normalisierung im Docker-Build dauerhaft behoben. Kein Release-Tag gesetzt.

## Noch zu erledigen

1. Vom Arbeitsplatz aus zuerst `https://5e.klassid.de` sowie die Weiterleitung
   von `https://klassid.de` testen. Status, Zertifikat, Loginseite und fehlende
   horizontale Überbreite prüfen. Der lokale Windows-Schannel-Aufruf des
   Klassenhosts endete mit `SEC_E_INTERNAL_ERROR`, obwohl Caddy die erfolgreiche
   Zertifikatsausstellung protokollierte.
2. In der bereits angemeldeten Resend-Oberfläche `KlassID Production` als
   sending-only API-Key, auf `klassid.de` beschränkt, erstellen. Das nur einmal
   angezeigte Token unmittelbar über den lokalen HomeOps-Dialog als
   `secret://providers/resend/klassid_api_key` speichern; niemals in Chat,
   Shellausgabe oder Git schreiben. Danach die DNS-Verifikation anstoßen und
   den Status `verified` abwarten. Die Browsersteuerung nahm zuletzt keine
   Klicks an; Bjoern kann die Fenster beim nächsten Lauf aktiv übernehmen.
3. Den produktiven E-Mail-Versand explizit konfigurieren und eine neutrale
   Registrierung plus echte Prüf-/Freigabe-/Aktivierungsmail testen. Prüfen,
   dass der Link `https://5e.klassid.de/...` verwendet. Bestehende Resend-Keys
   anderer Projekte nicht wiederverwenden.
4. Push auf genau einem eigenen Arbeitsplatzgerät aktivieren, den
   rate-limitierten Selbsttest ausführen, deaktivieren und die lokale
   Browser-Subscription abmelden.
5. Aktuelles `origin/main` erneut integrieren und das vollständige Gate bei
   beschreibbaren Testverzeichnissen nach den noch offenen Änderungen
   wiederholen. Nur bei weiteren Codeänderungen ein neues Releaseimage bauen
   und anhand des Vorher-Backups kontrolliert deployen.
6. HTTPS-, Health-, Login-, Registrierungs-, Kalender-, Stundenplan-, iCal-
   und Push-Smokes durchführen. Release-, Betriebs-, Datenschutz- und
   Rollbackprotokoll finalisieren.
7. Erst wenn alles grün ist, `origin/main` pushen und anschließend
   `v0.2.0-beta.1` auf exakt dem gebauten und ausgerollten Commit setzen und
   pushen. PDF SmartForms nicht beginnen.

Ungetrackte `.tmp-webuntis-main.js`, `schools.csv` und
`references/webuntis/private` dürfen niemals committed werden.
