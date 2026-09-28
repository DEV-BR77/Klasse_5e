# UI-Ist-/Soll-Abgleich

Stand: 24.09.2026. Grundlage sind die bereitgestellten Staging-Screenshots,
der aktuelle Django-Templatebestand und der zuletzt ausgerollte Staging-Build.
Die fachlichen Verwaltungsstrecken sind aktualisiert; die geschützte visuelle
Abnahme hinter dem Login bleibt als eigener Gate dokumentiert. Der aktuelle
Staging-Build wurde nach der letzten Navigation-/Kontextkorrektur neu gebaut;
Migrationen sind aktuell und der Health-Endpunkt antwortet erfolgreich.

## Kurzfazit

Der aktuelle Build verwendet für die überarbeiteten Portalbereiche ein
gemeinsames Shell-/Token-System. Die fachliche Verwaltung von
Schule → Klasse → Adapter → Modul → Zugang ist jetzt als Portalstrecke
erreichbar. Die sichtbaren Einstiege für Schulzugänge führen in den
Familien-/Kindkontext; die separate WebUntis-Route bleibt nur für bestehende
technische Rücksprünge und gespeicherte Zugangsdaten erhalten. Nicht
abgeschlossen ist die geschützte Browser-Abnahme aller Ansichten auf
Smartphone, Tablet und Desktop; sie benötigt eine gültige Staging-Anmeldung.

## Seitenabgleich

| Bereich | Im Screenshot sichtbar | Vereinbartes Ziel | Status |
|---|---|---|---|
| Startseite | Karten und Bereichs-Reiter für Stundenplan, Hausaufgaben, Abwesenheiten und Speiseplan | zentrale Modulansicht, einheitliche Karten und Zustände | teilweise vorhanden; fachliche Zuordnung ist nicht sichtbar |
| Kalender | Ansichtsumschalter, Filter und Zeitraster | zentrale Kalenderkomponente mit Modul-/Adapter-Herkunft im Hintergrund | Tagesansicht ohne unnötigen Seiten-Overflow; visuelle Staging-Abnahme offen |
| Chatübersicht | Raumliste, Suche, aktiver Raum und responsive Shell | zentrale Chat-Komponente, Gruppen-/Direktchat und Suche | umgesetzt; visuelle Staging-Abnahme hinter Login offen |
| Chatraum | Raumkopf, Nachrichtenbereich, Composer und Medien | stabiler Chatraum mit Mitglieder-/Rollenverwaltung, Moderation, Anhängen, Emojis/Stickers und Aufbewahrung | funktional umgesetzt; die gewünschte Verwaltung ist auf mehrere fachlich getrennte Karten/Wege verteilt, visuelle Abnahme offen |
| Mein Profil | Tabs vorhanden; eigener Anzeigename für den Chat | Personendaten, Profilbild/Avatar, Themes, Benachrichtigungen, Sicherheit | Chat-Anzeigename ist als fachlich getrennte Identitätseinstellung beibehalten; keine doppelte Kontaktfreigabe |
| Avatar | Avatar-Designer als Modal vorhanden | Foto und Avatar unabhängig pflegen und zentral darstellen | teilweise vorhanden; Chat-Katalog ist lokal ergänzt, Browserabnahme noch offen |
| Familien-Zentrale | Erwachsene und Kinder als getrennte Bereiche, Kind-Tab vorhanden | Erwachsene, Kinder, Rollen, Beziehungen sowie Schul-/Klassenbezug als zusammenhängende Familienverwaltung | Grundstruktur und Kinddetail vorhanden; WebUntis-Altroute bleibt für Kompatibilität bestehen |
| Kinderdetails | Stammdaten, Datenschutz und Schulzugänge als Tabs | Schulklasse, Adapter, Module, Zugangstyp und Aktivierung je Kind | einheitlicher Familien-Shell; Freigabe-Toggles lesbar ausgerichtet; Adapter-/Modulkatalog und Zugangsmodelle umgesetzt; visuelle Staging-Abnahme offen |
| Datenschutz/Synchronisation | globale Modul-Schalter je Kind | Module sichtbar; technische Adapter- und Zugangswahl im Hintergrund, nachvollziehbarer Status | Freigabestelle je Kind/Modul im Familienzentrum; alte globale Route leitet nur noch kompatibel dorthin weiter |
| WebUntis | separate Seite mit Kind-Auswahl sowie Benutzername/Passwort | Zugang beim Kind/Familienkonto, Adapter- und Modulzuordnung über die Schulverwaltung bzw. Familienkarte | falscher Einstieg; nur Zugangsdatenmaske, keine vollständige Modulverwaltung |
| Benachrichtigungen | Push/In-App-Tabelle | Modulbezogene Benachrichtigungen ohne entfernte Fahrgemeinschaft | teilweise vorhanden; gegen aktuelle Modulliste prüfen |
| Sicherheit/2FA | Portal-Sicherheitsseite mit Authenticator-App und Wiederherstellungscodes | zentrale Sicherheitskarte im Profil | gemeinsame Portal-Shell und responsive Karten umgesetzt |
| Adressliste | Tabelle mit Suche und Kontakt-Dialog | zentrale Tabelle, direkte Filterung, Rollen-/Freigaberegeln | strukturell vorhanden |
| Galerie | Galerie-/Fotokarten | zentrale Medienkarten, Status, Freigabe und Jugendschutzmeldung | Oberfläche vorhanden; mindestens ein Bildfehler sichtbar |
| Portalverwaltung | Verwaltung mit klaren Bereichen | zentrale Verwaltung mit klaren Bereichen und Pilotmeldungsverwaltung | umgesetzt; visuelle Staging-Abnahme offen |
| Rollenberechtigungen | Rollen-/Personenkarten | nur Hauptadministrator, Content Manager, Redakteur/Editor und Moderator in Phase 1 | lokale Einschränkung vorhanden, Staging zeigt alten Stand |
| Rollen & Personen | Auswahl und Tabelle | direkte Suche, Bearbeitungskarte, Rolle zuweisen/entziehen | umgesetzt; Aktionsspalten bleiben einzeilig; Staging-Abnahme hinter Login offen |
| Schulen & Klassen | Schule hinzufügen, Klasse anlegen | Schule öffnen → Stammdaten → Klassen → Adapter → Module → Status | Portalstrecke umgesetzt, inklusive Klassendetail und Klassenfreigaben |
| Adapterverwaltung | zentrale Anbieter-/Adapterkarten und schulische Einrichtungen | Zuerst zentralen Adapter mit Anbieter, Modulen und Zugangsmodell definieren; danach Schule/Klasse freigeben | umgesetzt: Definitionen, Module, Zugangsmodelle, schulische Adapter und Klassendetail mit Freigabe |
| Django-Admin Schule/Klasse | Django-Admin-Listen und englische Feldnamen | fachliche Verwaltungsmaske im Portal | klarer Zielverstoß; darf kein Standardweg sein |
| Modellvisualisierung | eigene Visualisierungsseite | Admin-Funktion für technische Modelle und Exporte | vorhanden, optisch eigener technischer Bereich zulässig |
| Pilotmeldungen | Feedback-Dialog aus dem Portal: Art, Beschreibung, optionaler Screenshot und aktuelle Seitenadresse | zentrale Verwaltungsansicht für berechtigte Administratoren mit offener/erledigter Meldung, Quelle, Zeitpunkt, Kategorie und sicherem Screenshotzugriff | umgesetzt, inklusive Bereichsprüfung, Statuswechsel und geschütztem Screenshot-Endpunkt |
| Automatische Abmeldung | globale Minutenangabe und Aktionen im Kartenrand | `0` = keine Leerlaufabmeldung, sonst 1–120 Minuten; Formularinhalt und Aktionsleiste mit zentralem Innenabstand; Speichern und Abbrechen zurück zur Portalverwaltung | Regel, Rücknavigation und lokale Formularstruktur korrigiert; die übergreifende Abstandskontrolle bleibt Teil der CSS-Abnahme |
| Systemstatus | technische Komponentenliste und zuletzt eingegangene Roh-Snapshots | **Systemstatus** als reine, datensparsame Betriebsübersicht; eigene Konfiguration für Messwertquellen, Grenzwerte, Aufbewahrung und Bereinigung | Betriebsübersicht und speicherbare Konfiguration umgesetzt; geschützte visuelle Abnahme offen |
| Menüstruktur | derzeit begrenzte Verwaltungsansicht | Nach der finalen Menüabnahme: Ober- und Unterpunkte, Sichtbarkeit und Reihenfolge zentral pflegen | bewusst nach Go-Live; keine vorgezogene Konfiguration einer noch nicht finalen Navigation |
| Themes | Theme-Auswahl, Portal-Miniatur und vollständige Vorschau | Theme-Verwaltung mit nachvollziehbarer Vorschau, Übernahme und bearbeitbaren Design-Tokens | Miniaturvorschau, vollständige Vorschau, Bearbeiten, Freigeben und Übernehmen umgesetzt |
| Sticker/Emojis | Auswahl im Chat | zentrale Pflegekarte für Emoji-/Sticker-Katalog inklusive Aktivierung und Reihenfolge | Pflegekarte, Katalog und Chat-Verwendung umgesetzt; Asset-/Browserabnahme offen |

## Konkreter WebUntis-Befund

Die Zugangsdaten werden im aktuellen Stand an zwei Stellen vorbereitet:

- im Kind-/Familienbereich über die Adapter-Zeilen in `ui/family.html`;
- zusätzlich über die separate WebUntis-Seite `webuntis/connection.html`.

Das ist genau die von dir kritisierte Doppelstruktur. Es fehlt eine einzige
fachliche Kette:

`Adapterdefinition → Moduldefinition → Zugangsmodell → Schule → Schulklasse → Freigabe → Kind/Familie → Zugang`

Der Zugang darf nicht der sichtbare Mittelpunkt der Oberfläche sein. Die
Verwaltung muss zuerst zeigen, welche Module die Schule bzw. Klasse anbietet;
danach wird pro Kind oder Familie der passende Zugangstyp gepflegt und der
Abrufstatus angezeigt.

## Adapter-Katalog: verständliche Benennung

Die im aktuellen Staging sichtbaren Begriffe sind keine Module, sondern
missverständliche, generische Namen für Adapterkarten:

- **„Schuldaten-Zugang“** bezeichnet derzeit technisch den Adapter
  **WebUntis**.
- **„Lernplattform-Zugang“** bezeichnet derzeit technisch den Adapter
  **itslearning**.
- **„Eigenes Portal“** ist ein unkonfigurierter Platzhalter für eine noch
  nicht technisch geprüfte Integration – kein nutzbarer Standardadapter.

Im Zielkatalog erscheinen Adapter ausschließlich mit ihrem echten,
administrativ nachvollziehbaren Namen, etwa **WebUntis**, **itslearning**,
**Schulmanager Online** oder **MensaMax**. Die zugehörigen Funktionen stehen
erst innerhalb des ausgewählten Adapters als Module. Ein unkonfigurierter
Platzhalter wird nicht als regulärer Adapter angeboten, sondern als klar
bezeichneter Vorgang „Adapter anfragen / technisch prüfen“ behandelt.

## Adapterpflege: aktueller Befund und Ziel

Die aktuelle Maske ist auch in ihrer Bedienlogik nicht die Pflege eines
globalen Adapterkatalogs:

- „Name des Schuladapters“ ist ein nachgelagertes, redundantes Feld. Der
  fachliche Adaptername muss aus der Adapterdefinition kommen.
- „Adapter veröffentlichen“ und „Adapter aktivieren“ vermischen globale
  Katalogfreigabe, schulische Freigabe und technische Verbindung. Diese
  Zustände müssen getrennt sichtbar sein: **im Katalog veröffentlicht**,
  **für Schule/Klasse freigegeben** und **Verbindung getestet**.
- „Bereits angelegte Adapter“ muss die zentrale Übersicht der
  Adapterdefinitionen sein, nicht eine unklare Liste schulischer Datensätze.
- Jeder Eintrag muss eine bearbeitbare Detailseite öffnen. Dort gehören
  Anbieter, Beschreibung, Schnittstellenart, Ziel-URL, unterstützte Module,
  notwendige Zugangsdaten, Zugangsmodell, Status, technische Prüfung und
  schulische Freigaben hin.

Die fachliche Reihenfolge lautet:

`Adapterübersicht → Adapterdetail → Module und Zugangsmodelle → technische Prüfung → Schul-/Klassenfreigabe`

Die aktuelle Portalstrecke erfüllt diese Reihenfolge. Die abschließende
Abnahme prüft zusätzlich die Rechtegrenzen und alle responsiven Darstellungen.

## Fehlende Verwaltungsbereiche

Die Punkte 1–10 sind umgesetzt oder in die fachlichen Wege integriert. Offen
bleibt die geschützte visuelle Abnahme.

## Nachweis des aktuellen Funktionsstands

- Django-Systemcheck: erfolgreich.
- Migrationsprüfung: keine ausstehenden Modelländerungen.
- Ruff-Prüfung der geänderten Navigations-/Kontextdateien: erfolgreich.
- Relevante Funktionssuite (Chat, Rollen, Familie, Schul-/Klassen-/Adapterkette,
  Schuldatenscope, Familienkontext, Profil und Admin-Workflows): **68 Tests
  bestanden** in einem isolierten, beschreibbaren Runtime-Mount.
- Isolierter Playwright-Responsive-Smoke-Test: **bestanden** für Login,
  Dashboard, Kalender, Kontakte, Dokumente, Chat, Navigation, Onboarding,
  Profil, Familie, Benachrichtigungen, MFA-Weiterleitung, Portal-/Schulverwaltung,
  Rollen, Berechtigungen, Themes und Avatar-Dialog bei 390 px, 768 px und 1280 px;
  kein Seiten-Overflow und keine JS-Fehler bei 390 px, 768 px und 1280 px.
  Breite Datentabellen scrollen nur
  innerhalb ihres eigenen Containers.
- Der Smoke-Test erzeugt zusätzlich einen synthetischen Chatraum mit Nachricht,
  Emoji-/Sticker-Auswahl und Dateianhang-Feld und prüft den aktiven Chatraum
  bei allen drei Viewportbreiten. Die Emoji- und Sticker-Picker werden dabei
  tatsächlich geöffnet und auf Sichtbarkeit geprüft.
- Aktueller Staging-Build: erfolgreich gebaut und gestartet; App, Datenbank
  und Vision gesund; `/health/` liefert `{"status": "ok"}`.
- Die erweiterte responsive Verwaltungsprüfung deckt Portalverwaltung,
  Schulverwaltung, Rollen & Personen, Rollenberechtigungen und Themes ab;
  die Abnahme-Screenshots werden als stabile Viewport-Aufnahmen bei 390 px,
  768 px und 1280 px erzeugt.
- Die Verwaltungsprüfung ruft zusätzlich den Systemstatus auf, speichert die
  Monitoring-Konfiguration mit Quellen, Grenzwerten und Aufbewahrung und prüft
  den Redirect zurück zur Betriebsübersicht bei allen drei Viewportbreiten.
- Die erzeugten Viewport-Aufnahmen wurden für Dashboard, Chat, Familien-Zentrale,
  persönliches Profil, Zwei-Faktor-Sicherheit, Rollenberechtigungen und Themes visuell geprüft. Dabei
  wurden die mobilen Zustände, Leerzustände, Kartenabstände, Bottom-Navigation
  und die Desktop-Hierarchie gegengeprüft. Die Profilnavigation bricht auf
  schmalen Desktop-/Tablet-Arbeitsflächen jetzt lesbar um und bleibt mobil
  horizontal bedienbar. Die MFA-Seite verwendet nun dieselbe Portal-Shell,
  Kartenlogik und responsive Navigation wie die übrigen Sicherheitseinstellungen.

## Konsequenz für die nächsten Schritte

Der aktuelle Stand ist auf Staging ausgerollt. Der verbleibende Ablauf ist:

1. Themes und Chatverwaltungswege visuell gegen die Referenzbilder abnehmen.
2. Angemeldete Staging-Ansichten auf Desktop, Tablet und Smartphone prüfen.
3. Abweichungen dokumentieren, Korrekturschleife ausführen und erneut prüfen.
