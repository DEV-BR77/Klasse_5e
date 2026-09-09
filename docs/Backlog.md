# Offene Aufgaben

Stand: 09.09.2026. Diese Liste hält die vom Betreiber bestätigten
Folgeaufträge fest. `docs/Backlog.md` ist die zentrale Datei für die nächsten
abzuarbeitenden Aufgaben; neue offene Folgeaufträge werden hier gepflegt. Sie ersetzt keine Berechtigungsprüfung und keine
Abnahmetests.

## Dringend

- [x] **Schuldaten im Familienkontext ausrollen und prüfen.** WebUntis- und
  Lernportal-Daten eines Kindes müssen für das Kind selbst sowie für alle
  bestätigten Sorgeberechtigten mit Profilzugriff sichtbar sein. Die
  Berechtigung bleibt auf das jeweils zugeordnete Kind begrenzt.
  **Abgeschlossen am 08.09.2026:** Stundenplan, Hausaufgaben, Abwesenheiten
  und itslearning-Inhalte werden beim Lesen über das Kind autorisiert. Das
  Kind selbst und aktuelle bestätigte Sorgeberechtigte mit Profilzugriff sehen
  denselben Stand; fremde Klassenmitglieder und widerrufene Beziehungen nicht.
  Zugangsdaten, Synchronisation und Kursverwaltung bleiben beim jeweiligen
  Verbindungsinhaber. Die Regressionstests decken Kind, zweiten
  Sorgeberechtigten, Fremdzugriff und unmittelbaren Beziehungswiderruf ab.
- [x] **Hängenden Docker-Image-Export beheben.** Das fertig gebaute Image mit
  der Familienfreigabe muss zuverlässig geladen und ausschließlich der
  App-Container neu gestartet werden. Anschließend Zugriff mit einem zweiten
  Sorgeberechtigten prüfen. **Abgeschlossen am 09.09.2026:** Der Rollout-Skript
  baut, exportiert und prüft nur das App-Image, legt zuvor ein Rollback-Tag an
  und startet per `--no-deps --no-build --force-recreate` ausschließlich den
  App-Container. Der Build exportierte in 83 Sekunden und lud das Image in 27
  Sekunden. App, Datenbank und Vision waren danach gesund; die öffentlichen
  Health- und Login-Endpunkte lieferten HTTP 200. Ein isolierter, vollständig
  zurückgerollter Produktionscheck bestätigte den Lesezugriff eines zweiten
  Sorgeberechtigten auf die Schuldaten des Kindes sowie den sofortigen Entzug
  nach Widerruf.

- [x] **Installationsanleitung für Android und iOS.** Die App-Einstellung zeigt
  getrennte, kurze Anleitungen für Android sowie iOS-Geräte.
  **Abgeschlossen am 09.09.2026:** Unter „KlassID als App installieren“
  erklären zwei responsive Kacheln die Installation über Chrome beziehungsweise
  Safari; der direkte Browser-Installationsknopf bleibt zusätzlich erhalten.

## Kommunikation und Kontakte

- [x] **Private Nachrichten.** In der Kontaktkarte eine Person auswählen,
  einen privaten Gesprächsverlauf öffnen, antworten und neutrale In-App-/
  Push-Hinweise erhalten. Zugriff, Aufbewahrung, Moderation und Meldung
  müssen für diesen Nachrichtentyp definiert und getestet werden.
  **Abgeschlossen am 09.09.2026:** Die Kontaktkarte eröffnet idempotent eine
  paarweise, klassenbezogene Unterhaltung. Nur die zwei aktiven Teilnehmer
  können lesen, schreiben und Anhänge abrufen; auch Portaladmins sehen keinen
  Verlauf. Hinweise und Push-Mitteilungen bleiben neutral. Nachrichten und
  Anhänge werden nach 180 Tagen gelöscht, offene Meldungen stoppen die
  Löschung; die gemeldete Nachricht kann ausgeblendet werden, ohne den
  übrigen Verlauf für Moderatoren zugänglich zu machen. Tests decken Zugriff,
  Entzug, Hinweise, Meldung, Moderation und Aufbewahrung ab.
- [x] **Kontaktliste als Familienansicht.** Familienname einmal zeigen,
  darunter Vornamen der Erwachsenen und Kinder; keine doppelte Bezeichnung
  wie „Familie Familie Radke“. Die Freigabeschalter für Erwachsene und Kinder
  müssen einheitlich gestaltet und bedienbar sein; das gilt für Adresse,
  Telefonnummer, E-Mail und weitere freigebbare Kontaktdaten.
  **Abgeschlossen am 09.09.2026:** Haushalte werden mit bereinigtem
  Familiennamen dargestellt; darunter stehen die Vornamen der Erwachsenen und
  Kinder. Die Erwachsenen- und Kinderseite verwenden denselben zugänglichen
  Freigabeschalter für Telefon, E-Mail und Adresse. Freigegebene Adressen
  erscheinen ausschließlich in der Kontaktkarte und nur für aktuelle
  Klassenmitglieder.
- [x] **Kontaktkarte.** Einen deutlich beschrifteten Kontakt-Button anbieten;
  Details in einer mittigen Kachel öffnen. Freigegebene Telefon- und
  E-Mail-Adressen müssen `tel:` beziehungsweise `mailto:` verwenden.
  **Abgeschlossen am 09.09.2026:** Die Familienzeile öffnet über „Kontakt
  öffnen“ eine zentrierte, mobile Kachel. Freigegebene Telefon- und
  E-Mail-Adressen sind sichere `tel:`- und `mailto:`-Links; die Kontaktkarte
  zeigt nur nach aktueller Klassen- und Beziehungsprüfung sichtbare Angaben.
- [x] **Familienbild und Ersatzdarstellung.** Optionales Familienfoto für die
  Kontaktkarte; ohne Bild einen Initialen-Kreis aus dem Familiennamen.
  Sichtbarkeit nur mit erforderlichen Foto-Freigaben aller abgebildeten
  Personen.
  **Abgeschlossen am 09.09.2026:** Familienbilder sind klassenbezogen,
  enthalten eine ausdrückliche Liste der abgebildeten Personen und werden nur
  mit deren aktueller Foto-Freigabe geschützt ausgeliefert. Ein Widerruf
  blendet das Bild sofort aus; die Kontaktkarte zeigt dann die
  Familieninitialen.
- [x] **Adressfreigabe.** Einen gemeinsamen Schalter „Adresse im Portal
  anzeigen“ für Straße, Postleitzahl und Ort ergänzen.
  **Abgeschlossen am 09.09.2026:** Auf ausdrückliche Erweiterung der
  Familienansicht umgesetzt. Der Schalter setzt alle drei Adressfelder
  gemeinsam und zeigt die vollständige Adresse nur in der Kontaktkarte.

## Kinderschutz im Chat und bei Bildanhängen

- [ ] **Kinderschutz: Sprache maskieren und Bildanhänge pixeln.** Den bestehenden
  Chatfilter zu einer überprüfbaren Kinderschutzfunktion erweitern: erkannte
  Schimpf- und beleidigende Wörter werden in der sichtbaren Nachricht mit
  Punkten maskiert; Bildanhänge mit erkannten problematischen Inhalten werden
  vor der Auslieferung verpixelt oder gesperrt. Für die spätere Umsetzung sind
  `profanity-check` für die Sprachbewertung und FalconsAI für die
  Bildbewertung vorgesehen. Flask, Flask-SocketIO für einen möglichen
  Echtzeitkanal und deren Betrieb dürfen erst nach einer Architekturentscheidung
  eingesetzt werden, weil der aktuelle Chat bewusst im Django-Monolithen per
  Polling arbeitet. Die Aufgabe umfasst eine deutschsprachige Qualitätsprüfung,
  Modell- und Lizenzprüfung, keine Speicherung von Rohbewertungen oder
  Klartext-Moderationsprotokollen, sichtbare Kennzeichnung, menschliche
  Meldung/Überprüfung, unmittelbaren Zugriffsentzug und Regressionstests für
  Fehlklassifikation, Umgehungsversuche, Klassenisolation sowie Widerruf.

## Mobile Startseite und Navigation

- [ ] **Mobile Kopfzeile verdichten.** Rechtliche Links einklappbar machen,
  ohne Benachrichtigungen und Profilzugriff zu verdecken.
- [ ] **Mobile Dashboard-Navigation.** Aktuelles, Stundenplan,
  Hausaufgaben und Speiseplan als kleine Icon-Tabs darstellen.
- [ ] **Stundenplan kompakt darstellen.** Zeit in einer Zeile, Fach/Raum/
  Lehrkraft darunter; drei Einträge ohne übergroße Karten sichtbar machen.
- [ ] **Hausaufgaben vor Tagesmenü.** Hausaufgaben im Tagesbereich vor dem
  Menü platzieren; Tagesmenü ein- und ausklappbar machen.
- [ ] **Fahrgemeinschaft verschieben.** Aus der Startnavigation entfernen
  und in Klassengemeinschaft einordnen; Adressliste in die direkte
  Navigation aufnehmen.

## Bedienung und Einstellungen

- [ ] **Abmeldebestätigung.** Dialog mit „Abbrechen“ und „Abmelden“ statt
  eigener ungestalteter Bestätigungsseite.
- [ ] **Chatraum-Aktionen verdichten.** Bearbeiten und Löschen als kleine
  Aktionen unter dem Raum; auf Mobilgeräten Wischaktion nach rechts.
- [ ] **Einstellungen sortieren.** Konto zuerst und geöffnet, dann
  Kommunikation, anschließend Klassenleben.
- [ ] **Veranstaltungen und Termine verwalten.** Berechtigte Ersteller:innen
  können eigene Einträge bearbeiten oder löschen.

## Eingabe und E-Mail-Ablauf

- [ ] **Telefonnummern normalisieren.** Google libphonenumber einsetzen,
  internationale E.164-Speicherung, gut lesbare Anzeige und direkte
  Telefonwahl sicherstellen.
- [ ] **E-Mail-Prüfung vereinheitlichen.** Serverseitige Django-Prüfung an
  allen Eingabestellen verwenden; Konten zusätzlich nur nach E-Mail-Link
  aktivieren.
- [ ] **Bestätigungs-E-Mail überarbeiten.** KlassID statt Klassenkennung im
  Betreff und Text, persönliche Du-Anrede und klarer Bestätigungslink.
- [ ] **Doppelten Bestätigungsschritt entfernen.** Nach dem E-Mail-Link
  direkt die Anmeldung mit dem vorhandenen Erfolgshinweis anzeigen.


## Rollenverwaltung und Familien-Datenschutz veröffentlichen

- [ ] **Implementierte Änderungen zusammenführen, abschließend prüfen und veröffentlichen.**
  Auf `codex/personal-roles-and-family-privacy` sind Rollenverwaltung mit Benutzerliste,
  Portal-Admin-/Elternvertretungsrollen und Glockenmeldungen sowie die editierbare
  Einwilligungstabelle und die Schalterkorrektur umgesetzt und lokal getestet.
  Noch offen: Integration in den Veröffentlichungsstand, Abschlussprüfung einschließlich
  Migrationen und Freigabe des Rollouts. Danach im laufenden Portal Rollenvergabe/-entzug,
  Elternvertreter-Chat und Freigabe/Widerruf beim Kind prüfen. Nicht als bereits
  ausgerollt behandeln. Umsetzung: `cd3be7f` und `2cef1c4`.

## Adapter und Abwesenheitsmeldungen

- [ ] **BL-16: Zentraler Adapterkatalog, Schulzuordnung und persönliche Zugänge.**
- [ ] **BL-17: Abwesenheit direkt vom Dashboard melden und bei WebUntis rückprüfen.**

Die folgenden Details sind aus den bisherigen Aufgaben 16 und 17 in `Nextsteps.md`
übernommen. Status und Anforderungen werden ausschließlich hier weitergepflegt.

### BL-16 – Zentraler Adapterkatalog, Schulzuordnung und persönliche Zugänge

**Status:** offen; am 08.09.2026 ausdrücklich als Folgeaufgabe beauftragt.
Diese Aufgabe wird separat umgesetzt; die derzeitige schulgebundene Adapterverwaltung
ist noch kein vollständiger zentraler Katalog.

#### Ziel und Ablauf

1. Portal-Admins legen Adapter einmal im zentralen Katalog an und bearbeiten sie dort.
2. Schulen ordnen vorhandene Katalogadapter zu und schalten sie sowie ihre Module
   für die Schule beziehungsweise zulässige Klassen an oder aus.
3. Unter Familien-Zentrale → Kind → Schulzugänge erscheinen ausschließlich die
   für die Schule/Klasse freigegebenen Adapter. Berechtigte Benutzer entscheiden
   dort persönlich, welche Funktionen sie für dieses Kind verwenden möchten.
4. Zugangsdaten lassen sich direkt in diesem Bereich beim ausgewählten Kind
   anlegen, ändern, prüfen und entfernen; kein Wechsel in einen unzugeordneten
   globalen Zugangsdialog. Aktivierungsstatus und Verbindungsstatus sind getrennt sichtbar.

#### Verbindlicher Schalter am Adapter

Beim Anlegen und Bearbeiten gibt es einen Toggle **„Persönlichen Zugang erfordern“**.
Ist er aktiv, darf der Adapter ausschließlich mit dem persönlichen, dem jeweiligen
Kind und berechtigten Benutzer zugeordneten Zugang verwendet werden. Ohne vollständig
hinterlegte erforderliche Zugangsdaten bleibt die Nutzung gesperrt; die Oberfläche
zeigt „Zugangsdaten erforderlich“. Ein gemeinsamer Schulzugang oder globaler Fallback
darf diese Pflicht nicht umgehen. Änderungen der Pflicht gelten auch für bestehende
Verbindungen und werden protokolliert.

#### Abnahme

- Echte Trennung von Katalogdefinition, Schulfreigabe und persönlicher Einstellung;
  bestehende Adapter, Module und verschlüsselte Zugänge migrationssicher übernehmen.
- Deaktivierung im Katalog oder in der Schule sperrt auch direkte URLs, APIs und
  Synchronisationen. Persönliche Aktivierung kann eine übergeordnete Sperre nicht aufheben.
- Zugangsdaten und persönliche Feinsteuerung sind je Benutzer und Kind isoliert;
  Geschwister, getrennte Sorgeberechtigte und andere Schulen erhalten keinen fremden Zugang.
- Zugangspflicht wird bei Speichern, Verbinden und Synchronisieren serverseitig geprüft.
- Geheimnisse verschlüsselt speichern, niemals zurückanzeigen oder protokollieren;
  sichere Ersetzung und Löschung. Nur synthetische Zugangsdaten in Tests.
- Bearbeitungsrechte folgen der aktuellen bestätigten Beziehung und Schulzuordnung;
  Entzug wirkt unmittelbar. Freiwillige Einwilligungen bleiben getrennte Entscheidungen.
- Verständliche Tabelle und Formulare am Kind, mit sichtbaren Speichern-/Prüfen-Aktionen,
  auch per Tastatur und ohne JavaScript bedienbar.
- Tests für vollständigen Ablauf, Schul-/Familienisolation, übergeordnete Sperren,
  Pflichtzugang, fehlende/falsche Zugangsdaten, Widerruf und Bestandsmigration.
- Kurze Betriebsdokumentation, Sicherheitsprüfung und Abschlussgate vor Veröffentlichung.


### BL-17 – Abwesenheit melden und unmittelbar bei WebUntis rückprüfen

**Status:** offen; als Folgeaufgabe ausdrücklich beauftragt. Baut auf BL-16 auf.
Aktuell existieren nur die vorbereitete Einwilligung und ein technischer Lese-Endpunkt;
kein vollständiger Fachabruf und kein Formular zum Melden einer Abwesenheit.

#### Einstieg und Testbarkeit

Verbindlicher Einstieg: **Dashboard → Schnellzugriff „Abwesenheit melden“**.
Der Button steht oben in der Übersicht neben Stundenplan, Hausaufgaben, Aktuelles
und Speiseplan und öffnet das Meldeformular direkt. Kurzfristige Krankmeldungen
müssen ohne Umweg durch Familienverwaltung oder Schulzugänge erreichbar sein.
Das im Dashboard ausgewählte Kind wird übernommen und im Formular sowie in der
Bestätigung klar angezeigt; bei mehreren Kindern ist eine eindeutige Auswahl möglich.
Die Einrichtung der persönlichen Zugangsdaten bleibt beim Kind unter Schulzugänge.
Einen synthetischen Testablauf mit simuliertem WebUntis anbieten;
Tests dürfen keine erfundenen Fehlzeiten in produktive Schulkonten schreiben.
Ein echter End-to-End-Test erfordert einen ausdrücklich vorgesehenen Testzugang oder
eine reale, bewusst freigegebene Abwesenheitsmeldung.

#### Ablauf im Live-Betrieb

1. Berechtigter Benutzer trägt die Abwesenheit für sein ausgewähltes Kind ein und
   sendet sie ausdrücklich ab. Schule, aktiver Adapter, persönliche Zugangspflicht,
   bestätigte Beziehung und erforderliche Freigaben werden serverseitig geprüft.
2. Der Adapter übermittelt die Meldung über eine zuvor geprüfte, unterstützte
   WebUntis-Schreibschnittstelle. Der bisher ausschließlich lesende Adapter erhält
   dafür eine eng begrenzte, gesondert geprüfte Schreibfunktion.
3. Direkt danach wird automatisch ein frischer Abruf der Abwesenheiten ausgelöst;
   weder der lokale Datensatz noch eine erfolgreiche HTTP-Antwort genügen als Bestätigung.
4. Den zurückgelesenen Eintrag eindeutig dem Kind und der gerade gemeldeten Abwesenheit
   zuordnen: externe ID, soweit vorhanden, sowie Zeitraum und relevante übermittelte Felder.
   Bereits vorhandene ähnliche Einträge dürfen keine falsche Bestätigung erzeugen.
5. Nur bei erfolgreicher Rückprüfung anzeigen: **„Abwesenheit ist angemeldet.“**
6. Bei fehlendem Eintrag oder Fehler anzeigen: **„Die Abwesenheit konnte nicht bestätigt
   werden. Bitte logge dich direkt bei WebUntis ein und prüfe die Meldung.“**
   Dazu die Schaltflächen **„Zu WebUntis“** und **„Abbrechen“** anbieten.
   Der WebUntis-Link führt zum freigegebenen Portal der ausgewählten Schule und enthält
   weder Zugangsdaten noch Abwesenheitsinformationen.

#### Fehlerverhalten und Abnahme

- Den Dashboard-Schnellzugriff auf Mobiltelefon und Desktop prüfen: Formular mit
  einem Aufruf erreichbar, korrektes Kind vorausgewählt, Kindwechsel eindeutig.
- Während der Rückprüfung „Bestätigung wird geprüft“ anzeigen. Verzögerte Sichtbarkeit
  mit wenigen begrenzten Lese-Wiederholungen berücksichtigen; keine Endlosschleife.
- Bei Timeout ist der Übermittlungsstatus möglicherweise unklar. Nicht behaupten,
  die Meldung sei sicher fehlgeschlagen, und nicht automatisch erneut schreiben.
- Doppelklicks und wiederholtes Absenden dürfen keine doppelten Abwesenheiten erzeugen.
- „Abbrechen“ schließt den Ablauf; eine möglicherweise bereits übermittelte Meldung
  wird dadurch nicht stillschweigend zurückgenommen. Dies im unklaren Fehlerfall erläutern.
- Abruf und Bestätigung unterliegen denselben Personen-, Schul- und Zugangsgrenzen;
  keine fremden Kinder oder fremden Benutzerzugänge lesen oder verwenden.
- Tests: erfolgreiches Melden mit Rücklesen, fehlender Eintrag, verzögerter Eintrag,
  falsches Kind/Zeitraum, bereits vorhandener Eintrag, Schreib-/Lesefehler,
  Timeout nach Übermittlung, Doppelabsenden, fehlende Rechte und deaktivierter Adapter.
- Datensparsame Auditierung ohne Freitexte, Diagnosen, Zugangsdaten oder Rohantworten.
- Schnittstellenfähigkeit und schulische Berechtigung vor Implementierung prüfen;
  fehlende WebUntis-Unterstützung ausdrücklich ausweisen, keinen Erfolg simulieren.
- Dokumentierter Testweg und Qualitätsgate vor produktiver Freigabe.


### BL-18 – Schulmanager Online: persönlicher Playwright-Adapter für Nachrichten und Elternbriefe

**Status:** offen; am 09.09.2026 als Folgeaufgabe erfasst. Baut auf BL-16 auf.

Schulmanager Online besitzt keine verwendbare API. Der Adapter verwendet daher
Playwright ausschließlich als kontrollierten, persönlichen Browseradapter.
Die Adapter-Modulverwaltung erhält eine Schulmanager-Online-Definition mit
benötigten Feldern für Benutzername und Passwort. Zugangsdaten werden je
berechtigtem Benutzer und Kind verschlüsselt gespeichert, nie erneut angezeigt,
in Logs geschrieben oder mit Benachrichtigungen übertragen. Ein fehlender,
abgelaufener oder falscher Zugang bleibt ein sichtbarer Verbindungsfehler.

Der Adapter liest nur Nachrichten und Elternbriefe, ordnet sie dem gewählten
Kind zu und erzeugt dafür neutrale In-App-Benachrichtigungen. Hinweise enthalten
keinen Nachrichtentext, keine Namen und keine Zugangsdaten; Inhalte sind nur
nach der bestehenden Kind-, Klassen-, Beziehungs- und Adapterprüfung sichtbar.
Der Abruf muss idempotent sein, Duplikate verhindern, Quelländerungen
nachvollziehbar behandeln und darf weder Formulare absenden noch andere
Schulmanager-Daten verändern.

Vor Umsetzung sind Nutzungsbedingungen, schulische Freigabe, technische
Stabilität der Browserstrecke, Verschlüsselung, Löschfristen und ein manueller
Fallback zu prüfen. Tests verwenden ausschließlich synthetische Playwright-
Antworten und Zugangsdaten; sie decken Familien- und Schultrennung,
Zugangstausch/-löschung, deaktivierte Adapter, doppelte Imports, fehlende
Nachrichten und sichere Fehlerbehandlung ab. Betriebsdokumentation,
Sicherheitsprüfung und Abschlussgate sind vor einer Veröffentlichung Pflicht.
