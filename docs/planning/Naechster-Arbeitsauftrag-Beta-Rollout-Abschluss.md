# Nächster Arbeitsauftrag: KlassID-Beta live abnehmen

Setze vom aktuellen `origin/main` fort. Lies zuerst `AGENTS.md`, HomeOps,
`PROJECT.md`, Architektur, DecisionLog, Roadmap und das Releaseprotokoll.
Private WebUntis-Dateien, Schulliste und Secrets niemals ausgeben oder
committen.

## Zuerst gemeinsam im Browser

1. `https://5e.klassid.de` auf Smartphone, Tablet und Desktop prüfen:
   Navigation, neues Logo, Home, Monats-/Wochen-/Tageskalender samt Filtern,
   Kontakte/Schüler, Profil, Chat, Veranstaltungen, Galerie, Dokumente,
   PWA-Anleitung, Push und keine horizontale Überbreite.
2. Mit einem neutralen Testkonto den kompletten Ablauf durchführen:
   Registrierung, echte E-Mail-Prüfung, Adminfreigabe mit Schul- und
   Klassenzuweisung, einmalige Aktivierung, Login sowie verpflichtendes
   Datenschutz-/Profil-Onboarding. Alle Links müssen `5e.klassid.de` nutzen.
3. Als Admin Portalverwaltung und QR-Anmeldeblatt prüfen. Als normaler Nutzer
   bestätigen, dass Verwaltung und fremde Daten unsichtbar bleiben.
4. Pilot-Meldebutton einschließlich Seitenbezug, Beschreibung und optionalem
   Screenshot testen; nur intern speichern, keine automatische GitHub-Anlage.

## Externe Restpunkte

- In Resend den projektspezifischen Sending-only-Key für `klassid.de` sicher
  anlegen, per HomeOps als `secret://providers/resend/klassid_api_key`
  speichern und Domainverifikation abschließen. Falls Anmeldung/Resend/Björn-
  Konto nicht funktioniert, genauen Zustand ohne Geheimnisse dokumentieren.
- Push auf genau einem eigenen Gerät aktivieren, rate-limitierten Selbsttest
  durchführen, wieder deaktivieren und die lokale Browser-Subscription
  abmelden.
- Kontrollierten WebUntis-Elternkontoabruf über `/student-homework`
  durchführen; ausschließlich Status und Anzahlen dokumentieren.
- Die Schulliste weiterhin nur als Dry-Run prüfen; Herkunft/Lizenz ist offen.

## Releaseabschluss

Aktuelles `origin/main` integrieren, vollständiges Docker-Gate wiederholen,
neues Image bauen, Vorher-Backup/Rollbackplan kontrollieren und erst danach
deployen. HTTPS-, Health-, Login-, Kalender-, Stundenplan-, Hausaufgaben-,
iCal- und Push-Smokes dokumentieren. Nur bei vollständig grünem Gate
`origin/main` pushen und anschließend `v0.2.0-beta.1` auf exakt dem gebauten
und ausgerollten Commit setzen. PDF SmartForms noch nicht beginnen.
