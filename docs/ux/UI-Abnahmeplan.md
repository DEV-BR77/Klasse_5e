# UI-Abnahmeplan

Dieser Plan trennt verbindlich Gestaltung von Fachlogik. Jede Ansicht wird
erst nach Abschluss der zentralen Komponenten geprüft. Der finale Bericht
ergänzt pro Seite den gewählten Aufbau und verbleibende Punkte.

## 1. Zentrale Grundlage

- Design-Tokens: Farben, Typografie, Abstände, Radien, Tiefen, Zustände;
- globale Komponenten: Buttons, Icon-Buttons, Eingabefelder, Passwortfeld,
  Schalter, Karten, Tabellen, Hinweise, Dialoge;
- Tabs/Reiter: einheitliche Desktop- und Mobile-Variante;
- App-Hülle: Kopfzeile, Familienwechsel, Hauptnavigation, Seitenbreite.

## 2. Öffentlicher Zugang

- Login, Passwort vergessen, Passwort setzen;
- Einladung, Registrierung, Aktivierung und Offline-Seite.

## 3. Persönlicher und familiärer Bereich

- Mein Profil mit Reitern;
- Familienübersicht, Personenkarten, Kinderdetails, Einladungen und
  Einwilligungen;
- Kontakte, Benachrichtigungen und App-Installation.

## 4. Tagesgeschäft

- Dashboard, Kalender, Stundenplan, Hausaufgaben und Abwesenheiten;
- Veranstaltungen, Dokumente, Beiträge, Speiseplan und Lernportale.

## 5. Chat und Medien

- Chatübersicht, Chatraum, Reaktionen, Meldungen und Aufbewahrung;
- Galerie und Bildansichten.

## 6. Verwaltung

- Portalverwaltung, Schulen, Klassen, Adapter und Modulzuordnung;
- Rollenberechtigungen, Rollen & Personen, Einladungen, Themes, Menü,
  Monitoring und Systemstatus;
- Modellvisualisierung und Import-/Export-Ansichten.

## Abnahmekriterium je Seite

Eine Seite ist erst fertig, wenn sie ausschließlich zentrale Komponenten
nutzt, auf Desktop und Smartphone verständlich bleibt, Tastaturfokus besitzt
und keine funktionsverändernde CSS-Sonderlösung benötigt.

## Umsetzungs- und Abnahmestand

- Zentrale Grundlage: umgesetzt und per Django-Systemcheck, Migration-Check
  sowie Responsive-Smoke-Test geprüft. Tokens, Buttons, Eingabefelder,
  Passwortanzeige, Karten, Hinweise, Dialoge und Reiter kommen aus der
  gemeinsamen Komponentenebene.
- Öffentlicher Zugang: umgesetzt; Login-, Passwort- und Aktivierungsseiten
  verwenden die gemeinsame Shell und die zentrale `password-control`-
  Komponente.
- Persönlicher und familiärer Bereich: umgesetzt; Profil, Familie,
  Benachrichtigungen, Datenschutz, Sicherheit und App-Installation bleiben
  fachlich getrennt, verwenden aber dieselbe Reiter- und Kartenlogik.
- Tagesgeschäft: umgesetzt und responsiv geprüft für Startseite, Kalender und
  die kontextabhängigen Familien-/Kindansichten.
- Chat und Medien: umgesetzt; Räume, Mitglieder, Nachrichtenänderung,
  Löschen, Melden, Moderation, Anhänge, Bilder, Emoji-/Sticker-Auswahl und
  Aufbewahrung sind im UI und in den zugehörigen Flows berücksichtigt.
- Verwaltung: umgesetzt; Personenfilter/-detail, Rollen, Schulen/Klassen,
  Adapter/Module, Themes, Menü, Monitoring und Systemstatus verwenden die
  neuen Arbeitsflächen statt der alten Kachel-Navigation.

## Nachweis und verbleibendes Gate

- `tools/Test-SettingsRedesign.py` prüft die zentralen Portalwege bei 390,
  768 und 1280 Pixeln auf Overflow, JavaScript-Fehler, Tastaturfokus,
  Dialoge sowie Chat-, Theme- und Avatar-Aktionen.
- Der vollständige Django-Testbestand ist im dokumentierten Lauf mit `350
  passed` erfolgreich durchgelaufen. Ein erneuter Vollauf im aktuellen
  Staging-Container war in dieser Schleife nicht möglich, weil dessen
  separates Test-Setup den Entwicklungs-Testbestand nicht enthält; deshalb
  wird dieser historische Nachweis nicht als neuer Lauf ausgegeben.
- Die isolierte responsive Prüfung endet mit `PASS`; der Django-Test für
  Theme-Previews besteht vollständig; `check`,
  `makemigrations --check --dry-run` und `/health/` sind erfolgreich.
- Die visuelle Smoke-Aufnahme setzt vor jeder Route und nach dem Öffnen des
  Emoji-/Sticker-Pickers explizit auf den Seitenanfang. Dadurch werden
  Scroll-Artefakte nicht als Layoutfehler bewertet; der Chat prüft zusätzlich
  eine tatsächlich gerenderte Konversationszeile im DOM. Die Desktop-Shell
  reserviert den Seitenleistenbereich nur einmal und nutzt die verfügbare
  Arbeitsbreite für Chat, Dashboard und Verwaltung.
- Die aktuelle authentifizierte Staging-Abnahme vom 24.09.2026 hat drei
  sichtbare Abweichungen aus den Referenzaufnahmen als Korrekturblock erfasst:
  Chatraum-Komposition, dauerhaft sichtbare Meldeformulare und die mobile
  Kopfzeile/Avatar-Navigation. Der Korrekturblock baut die Chatfläche als
  zusammenhängende Arbeitsfläche neu auf, öffnet Meldungen ausschließlich per
  Aktion, stabilisiert die Avatar-Karussellsteuerung und ordnet den mobilen
  Header neu.
- Nach diesem Korrekturblock ist die automatisierte visuelle Abnahme über 390,
  768 und 1280 Pixeln erneut erfolgreich (`PASS`, kein Overflow und keine
  JavaScript-Fehler). Die manuelle Referenzprüfung bleibt für die weiteren
  Seitenblöcke ein fortlaufendes Gate; eine Seite wird erst freigegeben, wenn
  der jeweilige Referenzvergleich und der fachliche Bedienablauf beide
  bestanden sind.
- Der anschließende Staging-Lauf vom 24.09.2026 bestätigt zusätzlich den
  korrigierten Chatraum: Touch-Aktionen sind erreichbar, das Meldeformular
  bleibt geschlossen bis zur ausdrücklichen Aktion, und die Desktop-Shell
  bleibt bei 1280 Pixeln ohne Doppelversatz. Danach waren `check`,
  `makemigrations --check --dry-run` und `/health/` erneut erfolgreich.
