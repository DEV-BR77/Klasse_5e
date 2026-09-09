# Offene Aufgaben

Stand: 09.09.2026. Diese Liste hält die vom Betreiber bestätigten
Folgeaufträge fest. `docs/Backlog.md` ist die zentrale Datei für die nächsten
abzuarbeitenden Aufgaben; neue offene Folgeaufträge werden hier gepflegt. Sie ersetzt keine Berechtigungsprüfung und keine
Abnahmetests.

## Empfohlene Reihenfolge und Modellwahl

Die folgende Liste enthält alle derzeit offenen Aufgaben. Die Modelle sind
Arbeitsvorschläge: Bei jeder Aufgabe wird vor dem Start nochmals geprüft, ob
Aufwand und Risiko die Wahl rechtfertigen. Nach jeder Aufgabe folgt ein
Qualitätsgate, ein kleiner Commit und die Backlog-Aktualisierung.

| Reihenfolge | Aufgabe | Empfohlenes Modell | Begründung |
|---:|---|---|---|
| 1 | Rollenverwaltung und Familien-Datenschutz live abnehmen | GPT-5.6 Terra · hoch | Berechtigungen und sofortigen Zugriffsentzug im laufenden Portal prüfen. |
| später | BL-18 Schulmanager-Online-Adapter | GPT-6 Astra · hoch | Auf Wunsch zurückgestellt; Playwright, Geheimnisse und Datenschutz benötigen die stärkere Prüfung. |

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
- [x] **Portalvorstellung sichtbar ankündigen.** Präsentationstermine (Titel mit
  „Portal/KlassID“ und „Vorstellung/Kennenlernen“) erscheinen im Dashboard unter
  „Aktuelles“. Aktive Klassenmitglieder erhalten beim ersten Portalaufruf
  idempotent eine ungelesene, neutrale In-App-Benachrichtigung mit direktem Link
  zur Veranstaltung; spätere Konten werden dadurch ebenfalls erreicht.
- [x] **Erstlogin als Willkommensseite.** Der bisherige Cloud-/Schrittablauf
  ist beim Erstlogin durch eine kurze Willkommensseite für die Klasse 5e ersetzt.
  Sie verweist auf Familienverwaltung, Profil-/Freigabepflege, persönliche
  WebUntis-Zugänge am Kind und die Präsentationsveranstaltungen. Die bisherigen
  Datenschutzdetails bleiben optional über einen direkten Link erreichbar.
  **Abgeschlossen am 09.09.2026:** Die Live-Ansicht wurde zusätzlich für Hell-
  und Dunkelmodus geprüft; Text und Aktionsbereich sind klar getrennt, lesbar
  und auf schmalen Bildschirmen untereinander angeordnet.

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

- [x] **Kinderschutz: Sprache maskieren und Bildanhänge pixeln.** Den bestehenden
  Chatfilter zu einer überprüfbaren Kinderschutzfunktion erweitern: erkannte
  Schimpf- und beleidigende Wörter werden in der sichtbaren Nachricht mit
  Punkten maskiert; Bildanhänge mit erkannten problematischen Inhalten werden
  vor der Auslieferung stark verpixelt.
  **Abgeschlossen am 09.09.2026:** Neue und bearbeitete Nachrichten verwenden
  denselben serverseitigen deutschen Filter einschließlich einfacher
  Trennzeichen- und Ziffernumgehungen. `profanity-check` wurde nach Prüfung
  verworfen, weil die veröffentlichte Fassung englisch, seit 2019 veraltet und
  unter Python 3.12 mit aktuellem scikit-learn nicht lauffähig ist. Der lokal
  betriebene Vision-Dienst klassifiziert neu codierte, metadatenfreie Bilder
  mit dem auf eine Revision und SHA-256 gepinnten Apache-2.0-Modell
  `Falconsai/nsfw_image_detection`. Bei problematischer oder fehlgeschlagener
  Klassifikation zeigt der Chat das Bild weiterhin an, jedoch ausschließlich
  als vollständig verpixelte JPEG-Ableitung; es wird weder abgewiesen noch
  automatisch zur Prüfung eingereicht. Rohscores, Klartext und Bilddaten
  erscheinen nicht in Audit oder Logs. Der bestehende manuelle Meldeweg bleibt
  verfügbar. Django-Polling und der vorhandene Vision-Dienst bleiben bestehen;
  Flask, Flask-SocketIO, Redis und zusätzliche Worker wurden nicht eingeführt.
  Tests decken Maskierung, harmlose Wortteile, Bearbeitung, Modellfehler,
  Verpixelung, Klassenmitgliedschaft und unmittelbaren Zugriffsentzug ab.

## Mobile Startseite und Navigation

- [x] **Mobile Kopfzeile verdichten.** Rechtliche Links einklappbar machen,
  ohne Benachrichtigungen und Profilzugriff zu verdecken.
  **Abgeschlossen am 09.09.2026:** Auf kleinen Displays fasst ein zugänglicher
  Aufklapper „Rechtliches“ Datenschutz, Impressum und Hinweise zusammen.
  Benachrichtigungsglocke und Profilmenü bleiben dauerhaft als eigene,
  ausreichend große Bedienelemente sichtbar.
- [x] **Mobile Dashboard-Navigation.** Aktuelles, Stundenplan,
  Hausaufgaben und Speiseplan als kleine Icon-Tabs darstellen.
  **Abgeschlossen am 09.09.2026:** Vier gleich breite Tabs mit Icon und Text
  schalten tastaturbedienbar zwischen Stundenplan, Hausaufgaben, Aktuellem
  und Speiseplan; Veranstaltungen stehen unter „Aktuelles“.
- [x] **Stundenplan kompakt darstellen.** Zeit in einer Zeile, Fach/Raum/
  Lehrkraft darunter; drei Einträge ohne übergroße Karten sichtbar machen.
  **Abgeschlossen am 09.09.2026:** Die Startseite zeigt maximal drei
  Stundenplanzeilen. Auf Mobilgeräten stehen Zeit, Fach sowie Raum/Lehrkraft
  übersichtlich untereinander; weitere Einträge führen in die Tagesansicht.
- [x] **Hausaufgaben vor Tagesmenü.** Hausaufgaben im Tagesbereich vor dem
  Menü platzieren; Tagesmenü ein- und ausklappbar machen.
  **Abgeschlossen am 09.09.2026:** Hausaufgaben haben einen eigenen,
  unmittelbar erreichbaren Tab. Das Tagesmenü liegt im Speiseplan als
  geschlossener Aufklapper vor der Wochenansicht.
- [x] **Fahrgemeinschaft verschieben.** Aus der Startnavigation entfernen
  und in Klassengemeinschaft einordnen; Adressliste in die direkte
  Navigation aufnehmen.
  **Abgeschlossen am 09.09.2026:** Die direkte Navigation führt nun zur
  Adressliste; Fahrgemeinschaften bleiben unter „Klassenleben“ erreichbar.
  Die Übersicht verwendet ein passendes fünftes Rasterfeld für die Aktion.
  Die zentrierte Kontaktkarte zeigt Erwachsene und Kinder jeweils einzeln mit
  Profilbild oder Avatar, Name sowie ausschließlich freigegebenen E-Mail-,
  Telefon- und Adressdaten. Zulässige Direktnachrichten starten direkt an der
  jeweiligen Person. Auf Mobilgeräten stehen die Personenkarten untereinander.

## Bedienung und Einstellungen

- [x] **Abmeldebestätigung.** Dialog mit „Abbrechen“ und „Abmelden“ statt
  eigener ungestalteter Bestätigungsseite.
  **Abgeschlossen am 09.09.2026:** Das Profilmenü öffnet eine zugängliche
  Bestätigung mit eindeutigem Abbrechen- und Abmelden-Schalter. Die Abmeldung
  wird erst über den CSRF-geschützten POST ausgelöst.
- [x] **Anmeldung nach automatischer Abmeldung stabilisieren.** Ein aus dem
  Browser-Zwischenspeicher wiederhergestelltes Loginformular darf keinen
  CSRF-Fehler anzeigen.
  **Abgeschlossen am 09.09.2026:** Loginseiten werden nicht zwischengespeichert
  und bei einer aus dem Vor-/Zurück-Cache wiederhergestellten Seite neu
  geladen. Falls dennoch ein altes Token abgesendet wird, bleibt der
  CSRF-Schutz wirksam und es folgt eine frische Anmeldeseite statt einer
  403-Fehlerseite.
- [x] **Chatraum-Aktionen verdichten.** Bearbeiten und Löschen als kleine
  Aktionen unter dem Raum; auf Mobilgeräten Wischaktion nach rechts.
  **Abgeschlossen am 09.09.2026:** Eigene Nachrichten zeigen kompakte
  Bearbeiten- und Löschen-Aktionen. Beide öffnen eine eindeutige Bestätigung
  beziehungsweise Bearbeitungsmaske und nutzen weiter die vorhandenen,
  CSRF-geschützten Nachrichtenschnittstellen. Auf Mobilgeräten blendet ein
  Wischen nach rechts die Aktionen ein.
- [x] **Einstellungen sortieren.** Konto zuerst und geöffnet, dann
  Kommunikation, anschließend Klassenleben.
  **Abgeschlossen am 09.09.2026:** Das Menü beginnt mit dem geöffneten Bereich
  „Mein Konto“, gefolgt von „Kommunikation“ und „Klassenleben“. Die
  Verwaltungsgruppe bleibt für Berechtigte anschließend erreichbar.
- [x] **Veranstaltungen und Termine verwalten.** Berechtigte Ersteller:innen
  können eigene Einträge bearbeiten oder löschen.
  **Abgeschlossen am 09.09.2026:** Organisator:innen können ihre eigenen
  veröffentlichten Veranstaltungen bearbeiten oder nach einer sichtbaren
  Bestätigung löschen. Aktive Klassenmitglieder können sich mit „Ich nehme
  teil“ anmelden; die Teilnehmerliste zeigt dann den Familiennamen und lässt
  sich jederzeit zurücknehmen. Änderungen und Teilnahme werden auditiert.
  Die alte Terminabstimmung wird nicht mehr in Veranstaltungen gezeigt; neue
  Veranstaltungen erfassen eine Beschreibung und optional einen Teams-Meeting-Link.

## Eingabe und E-Mail-Ablauf

- [x] **Telefonnummern normalisieren.** Google libphonenumber einsetzen,
  internationale E.164-Speicherung, gut lesbare Anzeige und direkte
  Telefonwahl sicherstellen.
  **Abgeschlossen am 09.09.2026:** `phonenumbers` 9.0.38 prüft Eingaben aus
  persönlichem Profil und Familien-Zentrale mit Standardregion Deutschland.
  Gültige Nummern werden als E.164 gespeichert, international formatiert
  angezeigt und als kanonischer `tel:`-Link ausgegeben. Die Migration bricht
  bei nicht sicher konvertierbaren Bestandswerten ab, statt Daten zu verlieren.
- [x] **E-Mail-Prüfung vereinheitlichen.** Serverseitige Django-Prüfung an
  allen Eingabestellen verwenden; Konten zusätzlich nur nach E-Mail-Link
  aktivieren.
  **Abgeschlossen am 09.09.2026:** Registrierung, Familienanmeldung,
  Familienprofile, persönliche Profile und Kontoerstellung verwenden dieselbe
  Normalisierung und Djangos E-Mail-Validator. Bestehende Aktivierungslogik
  erzeugt weiterhin erst nach bestätigtem E-Mail-Link und anschließender
  Freigabe ein aktives Konto. Regressionstests decken ungültige Eingaben und
  atomare Profilspeicherung ab.
- [x] **Bestätigungs-E-Mail überarbeiten.** KlassID statt Klassenkennung im
  Betreff und Text, persönliche Du-Anrede und klarer Bestätigungslink.
  **Abgeschlossen am 09.09.2026:** Beide Registrierungswege verwenden dieselbe
  persönliche KlassID-Mail mit Anrede, eindeutig benanntem Bestätigungslink,
  24-Stunden-Hinweis und neutralem Sicherheitsausweg für nicht selbst
  ausgelöste Anmeldungen.
- [x] **Doppelten Bestätigungsschritt entfernen.** Nach dem E-Mail-Link
  direkt die Anmeldung mit dem vorhandenen Erfolgshinweis anzeigen.
  **Abgeschlossen am 09.09.2026:** Ein gültiger Aktivierungslink führt ohne
  Zwischenansicht direkt zur Anmeldung. Dort erklärt ein einmaliger
  Erfolgshinweis, dass das persönliche KlassID-Konto bereit ist; ungültige,
  abgelaufene oder bereits verwendete Links bleiben als neutrale Fehlerseite
  sichtbar.


## Rollenverwaltung und Familien-Datenschutz veröffentlichen

- [ ] **Rollenverwaltung und Familien-Datenschutz im laufenden Portal abnehmen.**
  Rollenverwaltung mit Benutzerliste, Portal-Admin-/Elternvertretungsrollen und
  Glockenmeldungen sowie die gemeinsame Einwilligungsmaske mit einheitlichen
  Schaltern wurden am 09.09.2026 zusammengeführt, vollständig automatisiert geprüft
  und mit App-Image `klasse-5e-app:0.3.0b4` ausgerollt. Migrationen und Healthcheck
  sind erfolgreich. Noch offen ist die angemeldete manuelle Abnahme im laufenden
  Portal: Rollenvergabe und -entzug, Elternvertreter-Chat sowie Freigabe und Widerruf
  beim Kind prüfen. Umsetzung: `cd3be7f` und `2cef1c4`.

## Adapter und Abwesenheitsmeldungen

- [x] **BL-16: Zentraler Adapterkatalog, Schulzuordnung und persönliche Zugänge.**
- [x] **BL-17: Abwesenheit direkt vom Dashboard melden und bei WebUntis rückprüfen.**

Die folgenden Details sind aus den bisherigen Aufgaben 16 und 17 in `Nextsteps.md`
übernommen. Status und Anforderungen werden ausschließlich hier weitergepflegt.

### BL-16 – Zentraler Adapterkatalog, Schulzuordnung und persönliche Zugänge

**Status:** abgeschlossen am 09.09.2026. Der zentrale Katalog, die Schul-/Klassenfreigabe
und die persönliche Aktivierung je Kind sind umgesetzt. WebUntis und itslearning prüfen
die Freigabe serverseitig beim Speichern und Abrufen; deaktivierte Adapter sperren auch
direkte Zugriffe und automatische Synchronisationen. Verschlüsselte Zugangsdaten bleiben
bei den konkreten Adaptern und werden nicht im Katalog gespeichert.

**Nachbesserung am 09.09.2026:** Die Modulverwaltung verwendet kompakte, einheitliche
Kacheln mit Beschreibung und direktem Freigabeschalter; erweiterte Klassen- und
Zugangseinstellungen bleiben beim Umschalten erhalten. In der Familien-Zentrale werden
Module je Portal gruppiert. WebUntis zeigt Benutzername, Passwort und Speichern direkt
beim ausgewählten Kind, ohne gespeicherte Zugangsdaten zurückzugeben. MUNDO und weitere
öffentliche Lernangebote sind zusätzlich über den eigenen Menüpunkt „Lernportale“
erreichbar.

Die Datenschutzfreigaben eines Kindes verwenden ebenfalls kompakte, einheitliche
Schalter. Kurze Wirkungsbeschreibungen stehen direkt an der Freigabe; der vollständige
Einwilligungstext ist aufklappbar. Alle Änderungen werden mit einem gemeinsamen
Speichern-Button übernommen, während zentral deaktivierte Funktionen gesperrt bleiben.

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

**Status:** abgeschlossen am 09.09.2026. Schulmanager Online ist auf Wunsch
zurückgestellt und nicht Teil dieses Releases.
Der vorhandene Abwesenheitsimport und lokale Meldeentwurf bleiben die Ausgangsbasis.
Der Benutzer hat Playwright für Übermittlung und Rücklesen ausdrücklich festgelegt;
eine direkte API-Schreibintegration gehört nicht zum Auftrag.
Die Chrome-Prüfung hat die WebUntis-Seite `/student-absences` mit eingebetteter
Abwesenheitsübersicht und Schaltfläche „Abwesenheit melden“ bestätigt.
Das Meldeformular wurde ohne Absenden geprüft: Beginn, Ende und Anmerkung.
Die Zuordnung erfolgt über den beim Kind hinterlegten persönlichen Zugang;
bei externen Mehrkindkonten ist eine eindeutige Auswahl erforderlich.
Commit `622c7c1` ergänzt einmalige Übermittlung mit begrenzter Rückprüfung als
transportunabhängigen Baustein; Commit `3bb8bc6` verbindet Dashboard,
Kindauswahl, persönliches verschlüsseltes Login, ausschließlich UI-basiertes
Playwright-Übermitteln, persistente Token-Deduplizierung und maximal drei
frische Rückleseversuche. Er meldet Erfolg nur für einen neuen, passenden
Eintrag; bei jeder Mehrdeutigkeit bleibt die Meldung unbestätigt. Sendeprotokolle
sind frei von Freitext und Zugangsdaten und werden nach 30 Tagen gelöscht.
Die Browserstrecke wurde am echten Formular ohne Absenden geprüft; die Tests
verwenden ausschließlich synthetische Daten. Ein realer End-to-End-Test blieb
aus, weil keine reale Abwesenheit freigegeben wurde.

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
2. Der Adapter übermittelt die Meldung über das zuvor geprüfte WebUntis-Formular
   mit Playwright. Der Browserablauf erhält dafür eine eng begrenzte,
   gesondert geprüfte Schreibfunktion; keine direkten API-Schreibaufrufe.
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

**Status:** technische Umsetzung am 09.09.2026 begonnen; Live-Abnahme und
Produktivfreigabe bleiben offen.
Die angemeldete Chrome-Sitzung zeigt Nachrichten unter
`#/modules/messenger/messages` und Elternbriefe unter `#/modules/letters/view`.
Noch zu prüfen sind Login, eindeutige Kind-/Schulzuordnung, Detailansichten und
Nebenwirkungen auf Lesebestätigungen. Die Browserbrücke konnte die Sitzung
während der Umsetzung nicht zuverlässig auslesen. Es wurden keine
Nachrichtendaten in Git übernommen.
AGB-Erstprüfung: https://www.schulmanager-online.de/agb.html; daraus folgt noch
keine nachgewiesene schulische Freigabe für den automatisierten Betrieb.
Der Adapter besitzt nun einen kontrollierten, rein lesenden Playwright-Transport,
verschlüsselte Zugangsdaten pro Kind, idempotente neutrale Benachrichtigungen und
den Befehl `manage.py sync_schoolmanager`. Abschlussprüfung und Live-Abnahme
bleiben vor einer Veröffentlichung erforderlich. Baut auf BL-16 auf.

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
