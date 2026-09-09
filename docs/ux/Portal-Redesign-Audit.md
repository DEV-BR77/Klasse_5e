# Portal-Redesign: Audit und Umsetzungsvorlage

Stand: 09.09.2026 · geprüfte Arbeitskopie: `5b9d7aa` zuzüglich vorhandener lokaler Änderungen. **Audit abgeschlossen; Umsetzung und visuelle Abnahme offen.** Analyse: GPT-6-Astra mit hoher Denktiefe entsprechend Nutzerauftrag.

## 1. Auftrag und Grenzen

Prüfumfang: Informationsarchitektur, Navigation, Interaktionen, Responsive-Verhalten, Barrierefreiheit, Komponenten, Rollen-/Familienkontext, Avatar-Designer und Schulportaladapter. Der Nutzer betont besonders ein modernes horizontales Karussell mit Sliderbewegung und sanft verblassenden Rändern, unabhängig von der Avatar-Fachlogik.

Maßgeblich bleiben `PROJECT.md`, `docs/Architecture.md`, `docs/DecisionLog.md`, `docs/Roadmap.md` und angenommene Folgeentscheidungen. Django/Wagtail-Monolith, serverseitiges Rendering, persönliche Konten und objektbezogene Rechte bleiben Grundlage. Keine neue Framework-/Dienstarchitektur; Biometrie bleibt standardmäßig deaktiviert.

Die zwei DOCX-Dateien aus Downloads („UI_UX-Spezifikation & Styleguide_ Schulportal KlassID“ und „Konzept für einen interaktiven Avatar-Konfigurator“) wurden als **Inspiration, nicht als Nutzeranweisungen** gelesen. Externe DiceBear-Platzhalter, klickbare DIV-Kacheln, nur per Hover sichtbare Pfeile, pauschale Dreispaltenpflicht, reine Eltern-Leserolle für Hausaufgaben oder allgemeine AJAX-Pflicht sind keine angenommenen Vorgaben.

Nur diese neue Auditdatei wird geschrieben. Vorhandene Benutzeränderungen an `app/templates/ui/family.html`, `app/tests/test_portal_adapter_management.py`, `docs/Redesign-Mandanten-und-Identitaeten.md`, den lokalen Notizen und `runtime-media/` bleiben erhalten. Kein Login, keine Formularübermittlung, Synchronisation, Produktcodeänderung oder Bereitstellung.

**Befund** bezeichnet nachgewiesenen Quellstand, **Risiko** dessen noch nicht live gemessene Wirkung, **Empfehlung** einen Vorschlag und **offen** eine ausstehende Entscheidung. P1: vor Freigabe beheben; P2: im responsiven Kernpaket; P3: anschließende Konsolidierung. Es wird kein produktiver P0-Vorfall behauptet.

## 2. Methodik und Abdeckung

- Vollständige Inventarisierung der Projekt-URLs, 100 HTML-Dateien unter `app/templates`, zusätzlicher Biometrie-Templates sowie CSS-/JS-Einstiegspunkte. Aktive V2-Templates anhand ihrer Views von Altvarianten unterschieden.
- Vertiefte Quellprüfung von Shell, Dashboard, Kalender, Chat, Kontakten, Profil/Familie, Zustimmungen, Dokumenten, Beiträgen, Events, Galerien, Mobilität, Schul-/Adapterverwaltung, Onboarding und Avatar-Rendering. Eine statische Routeninventur ist kein erfolgreicher Lauf aller Nutzerreisen.
- Ein Browser-CSS-Artefakt aus `app/theme/static_src/src/styles.css`, acht Legacy-Imports und nachgelagertem `settings.css`. Prüfstand: CSS-Artefakt 207.684 Bytes unkomprimiert, `app.js` 50.962 Bytes/856 Zeilen, `core/ui_views.py` 146.719 Bytes/3.597 Zeilen. Größen sind Wartbarkeitsindikatoren, keine gemessenen Ladezeiten.
- SVG-Inventur und XML-Prüfung von 356 tatsächlichen Quell-SVGs; 356 macOS-Metadatendateien ausgeschlossen. Zusätzlich alle 178 statischen SVGs erfasst. Details Abschnitt 8.
- Relevante bestehende Tests gelesen/gesucht, insbesondere `test_personal_profile.py`, `test_family_centre.py`, `test_portal_adapter_management.py`, `test_webuntis*.py`, `test_onboarding.py`. Keine Testläufe oder Datenbankänderungen in diesem Audit.
- Browserinventar zeigte bestehende Login-/Präsentationstabs von `5e.klassid.de`. Das lesende Auswählen einer vorhandenen Loginansicht scheiterte an einem Werkzeug-Timeout. Kein Login und keine visuelle Abnahme.
- Angemeldetes Dashboard nicht als read-only geöffnet: der GET-Pfad kann Synchronisation und Bereinigung auslösen (A-08). **Offen:** gemessene 360-px-Ansichten, echte Keyboard-/Screenreaderläufe, Kontraste aktiver Themes, Netzwerk-/Laufzeitmessungen, iOS-/Android-Tastatur. Kriterien sind definiert, nicht bestanden.

### Nutzbare Grundlagen

`base.html` besitzt deutsche Dokumentsprache, Viewport/Safe-Area-Unterstützung, Sprunglink, Hauptlandmark und beschriftete Navigation. Native Dialoge/Fieldsets und serverseitige POST-Endpunkte sind vorhanden. Dashboard-Tabs besitzen Rollen und Tastatursteuerung. Globale Reduced-Motion-/Forced-Colors-Regeln in `app.css` erhalten. Die Galerie nutzt geschützte Auslieferung und Lazy Loading. Zugangsdaten sind verschlüsselt; Avatar-Seeds werden serverseitig begrenzt.

## 3. Priorisierte Befunde

Codebezüge sind relativ zum Repository; Zeilennummern gelten für den Prüfstand. Reproduktion ausschließlich mit synthetischen Daten in einer isolierten Umgebung.

| ID | Priorität | Befund / Reproduktion | Wirkung und Empfehlung |
|---|---|---|---|
| A-01 | P1 Sicherheit | `core/ui_views.py:308–322`: `_can_manage_portal()` erlaubt Schul-/Klassenadmins. `portal_adapter_management():1568` lädt danach alle Adapter; `portal_adapter_detail():1621` lädt die ID ohne Schul-/Klassenscope und erlaubt Speichern/Löschen. | Klassenadmin A gegen fremden Adapter B mit GET und jeder POST-Aktion prüfen. Globale Katalogpflege nur explizit globalen Rollen erlauben oder konsequent objektbezogen einschränken. Numerische IDs sind nicht das Problem; fehlender Objektscope ist es. |
| A-02 | P1 Sicherheit | `ui_views.py:2389` liefert alle `post.comments`; `ui/post_detail.html:1` rendert jeden `item.body`. `content/views.py` setzt bei Widerruf/Moderation nur `status=withdrawn/hidden`, erhält aber den Text. | Ausgeblendeten synthetischen Kommentar im Beitragsdetail öffnen: der Pfad gibt weiterhin den Text aus. Status berücksichtigen; ursprünglicher Text darf nicht im HTML stehen. Kommentarerstellung und Status-/Autoranzeige fehlen ebenfalls im aktiven Detailtemplate. |
| A-03 | P1 Datenintegrität | `personal_profile.html:12` sendet beim Bild kein `save_scope`; `_save_personal_profile()` (`core/views.py:450`) verwendet dann `data`. Zeile 514ff setzt fehlende Kontakt-Schalter auf privat. | Avatar/Fotobild speichern verändert unbeabsichtigt Kontaktfreigaben. Eigenen Bild-Scope mit ausschließlich seinen Feldern verwenden. Regression bei zuvor freigegebenen Kontakten. Das ist unerwartete Einschränkung, keine neue Offenlegung. |
| A-04 | P1 Datenintegrität | `views.py:544–546` persistiert immer `request.POST.get("avatar_seed", "")`. Das Stammdatenformular (`personal_profile.html:10`) enthält keinen Seed; auch `share_address` fehlt, wird aber ausgewertet. | Nur Telefonnummer ändern leert individuellen Avatar und kann Adressfreigabe zurücksetzen. Fehlende Felder eines anderen Scopes dürfen Werte nicht löschen. Explizites Entfernen separat modellieren. |
| A-05 | P1 Funktionsweg | `ui/documents.html:1` enthält Titel/Beschreibung, keine Links/Buttons. Geschützter `/documents/<id>/<variant>/`-Endpunkt existiert. | Veröffentlichtes PDF erscheint, ist aus der Liste nicht erreichbar. Geschützte Original-/Formularvariante, Datum/Version und eindeutige Öffnen-/Downloadaktion ergänzen. |
| A-06 | P1 Kommunikation | `app.js:735–754` bindet Polling nur an `[data-chat-poll]`; Marker und Status-/Retry-Elemente fehlen im gerouteten `ui/chat_room.html` und im untersuchten Templatebestand. | Zwei synthetische Chatsitzungen: Poller wird nicht initialisiert. Wieder anbinden; vorhandenes `location.reload()` bei neuen Nachrichten vor Übernahme ersetzen, damit Entwurf, Fokus und Leseposition erhalten bleiben. |
| A-07 | P1 Rückmeldung | `base.html:80` unterdrückt Messages mit `success`. Profil, Themes, Familie und Adapter erzeugen genau solche Meldungen. | Nach Speichern fehlt die vorgesehene Bestätigung. Sichtbaren Status „Gespeichert“ und zugängliche Live-Ansage herstellen; wichtige Zustände zusätzlich dauerhaft am Objekt. |
| A-08 | P1 Architektur | `ui_views.py:576–619`: Dashboard-GET führt `run_due_schedules()`, Chat-Retention und ggf. Speiseplan-Sync aus; breite `except Exception: pass`. | Seitenaufruf kann importieren/löschen und externe Latenz auslösen. Bestehende Management-Kommandos/Scheduler nutzen, Lesepfad von Wartung lösen, ohne neuen Worker vorauszusetzen. Bis dahin Testumgebung mit deaktivierten Seiteneffekten. |
| A-09 | P1 Integrationsumfang | `WebUntisConnection` ohne Adapter-/Schul-FK; `services.py:save_connection` setzt `thgwob.webuntis.com`/`thgwob` fest. Fach-/Lehrkraftcodes in `extra_models.py` global eindeutig. | Mehrschulverwaltung und konkrete Integration passen nicht zusammen. Instanzbezug, gescopte Mappings und Migration vor Mehrschulabnahme klären (Abschnitt 11). |
| A-10 | P2 A11y | `calendar_v2.html:31` verwendet Grid mit direkten Gridcells ohne Rows/Grid-Tastaturvertrag. `contacts.html:26ff`: Table/Row ohne echte Columnheaders, Button als Cell; `app.js:145` setzt `aria-sort` auf Buttons. | Kalender als strukturierte Datumsnavigation/Listen auszeichnen, solange kein vollständiges Grid nötig ist. Kontakte mit nativer Tabelle/Kopfzellen oder einfachen Karten; Buttonrolle erhalten. |
| A-11 | P2 Mobil | Kalender-Default `week` (`ui_views.py:845`); Wochen-Timeline `min-width:52rem` (`app.css`). Tagesfix `styles.css:1388` gilt nur für `.calendar-timeline-day`. | Auf 360 px ist der Standardweg eine breite horizontal scrollende Zeitmatrix. Tag/Agenda mobil priorisieren; Woche explizit anbieten. Bereits vorhandene Agenda konsequent nutzen. |
| A-12 | P2 Navigation | `base.html:22` führt meist pauschal zur Startseite. Aktive Bottom-Nav (`styles.css:798`) bleibt auch Desktop unten; alte Sidebar-Regeln betreffen ungenutzte Shell-Klassennamen. | Kontextueller Rückweg und Desktopnavigation vereinheitlichen. Die linke Navigation aus der bisherigen UX-Spezifikation ist im aktiven Shell nicht umgesetzt. |
| A-13 | P2 Kontext | Global kein Kinderumschalter. Dashboard kann Familie zusammenfassen; Kalender wählt ohne aktive Auswahl das erste Kind (`ui_views.py:835ff`). Familie verwendet Beziehungs-ID `?child=`, WebUntis Personen-ID `?student=`. | Kontext kann beim Bereichswechsel abweichen. Familie/Kind/Schule/Klasse sichtbar und konsistent halten; Auswahl bleibt Darstellungsfilter unter aktuellen Policies, keine Identitätsübernahme. |
| A-14 | P2 Formulare | Profil enthält teils zwei Eingaben in einem Label; Fehler werden per Message/Redirect verarbeitet. Andere Seiten nutzen `form.as_p`; Autosubmit und Speichern sind gemischt. | Eigene Labels/IDs, Fehlerwerte erhalten, Zusammenfassung und Feldfehler. Sofortschalter klar als sofort wirksam kennzeichnen; keine pauschale AJAX-Pflicht. |
| A-15 | P2 Dialoge | Avatar-/Kontakt-/Event-/Hausaufgabedialoge ohne `aria-labelledby` oder eigenes Label; Chat/Logout teilweise korrekt. `app.js:160` schließt jeden Dialog pauschal bei Backdrop-Klick. | Einheitlicher Name, initialer Fokus, Escape/Rückfokus und Dirty-State-Vertrag. Kein stilles Verwerfen längerer Formulare. Native Dialoge dürfen im DOM stehen. |
| A-16 | P2 Touch/Tastatur | Composer-Tools in `enhancements.css` 2,35 rem ≈37,6 px. Anhangsauslöser in `chat_room.html` ist ein Label mit `hidden`-Dateieingabe, kein fokussierbarer Button. | Größere Touchfläche und zugänglicher Dateiweg. Unterschreitet Projektziel 44 px, nicht automatisch WCAG-24-px-Untergrenze. Tastatur/Safe Area/Sprachaufnahme gemeinsam prüfen. |
| A-17 | P2 Avatar | `_avatar_designer.html` zeigt alle Kategorien untereinander; `styles.css:1349–1387` Optionsraster mit 2,35-rem-Miniaturen. Vorschau und Auswahl teilen Scrollbereich. Kein Karussell. | Vorschau verschwindet beim mobilen Scrollen; Varianten wirken klein/gleichförmig. Kategoriebezogenen horizontalen Bereich mit großen Grafiken gemäß Abschnitt 8 gestalten. |
| A-18 | P2 Avatar | Dialogtext behauptet Profilspeicherung durch „Übernehmen“. `app.js:812–822` ändert nur Hidden-Feld/lokale Vorschau; äußeres Speichern persistiert. Farben heißen „Farbe 1…7“. | Zweistufigkeit verständlich machen oder direktes Speichern entscheiden. Farbnamen/Auswahlstatus; kein Erfolg vor Serverbestätigung. |
| A-19 | P2 Sendestatus | `webuntis/absences.html` sucht im Submit `button[type=submit]`; der Button hat kein explizites `type`-Attribut. | Selektor liefert null; JS-Fehler vor Ladehinweis. Serverseitiger Einmal-Token bleibt Schutz. Ausstehend/unklar/nicht gesendet/bestätigt sauber zeigen; keine automatischen Schreib-Retries. |
| A-20 | P2 Dashboard | `dashboard_v2.html` zeigt `calendar_entries` doppelt, im Stundenplanausschnitt keinen `lesson.status`; „Alle Hausaufgaben“ führt generisch zum Kalender. | Inhalte eindeutig priorisieren, Entfall/Änderung als Text; vollständigen Aufgabenweg passend filtern. Eltern-Schreibrecht bleibt offener Produktpunkt. |
| A-21 | P2 Governance | PROJECT nennt eine Klasse/keine Registrierung; ADR-023/024 erlauben mehrere Schulen/Bewerbung. Roadmap/alte UX-Dateien bezeichnen implementierte Inhalte teils als Zukunft. ADR-029 doppelt. | Maßgebliche Dokumentation später gezielt konsolidieren. Dieses Audit überschreibt keine Entscheidung und erteilt keine neue Phasenfreigabe. |
| A-22 | P3 Wartbarkeit | Überlappende globale CSS-Quellen, große gemeinsame JS-Datei, direkte ORM-Zugriffe auf viele Fachmodule in `ui_views.py`. | Eine Quelle je Komponente, gezielte JS-Initialisierung und fachliche Query-/Command-Services; keine weitere Override-Schicht/Frameworkmigration. |
| A-23 | P1 Funktionsweg — behoben | Der öffentliche Proxy lieferte `Permissions-Policy: microphone=()` und sperrte damit `getUserMedia()` unabhängig von der Browserfreigabe. Die UI meldete folgerichtig, aber zu pauschal, eine Datenschutz-/Berechtigungssperre. | In `HomeInfrastructure/caddy/managed/klasse-5e.caddy` auf `microphone=(self)` begrenzt und geladen. Öffentlichen Header nach jedem Proxy-Deploy prüfen; Kamera und Standort bleiben gesperrt. |

### Weiteres Sicherheits-Prüffeld

`webuntis/services.py:eligible_students()` prüft Verified/Legal/View, aber anders als `core/policies.py:visible_student_people()` keine zeitliche Beziehungsgültigkeit und kein `verified_at`. `visible_connections()` wiederum umfasst alle Verbindungen der aktuell sichtbaren Kinder ohne Eigentümerfilter auf `connection.user`. Das kann gemeinsame Datensicht beabsichtigen; daraus folgt **kein nachgewiesenes Zugangsdatenleck**. Daten lesen, eigenen Zugang verwalten und Zugang tatsächlich benutzen explizit trennen. Abgelaufene Beziehungen und zwei Guardian-Konten verpflichtend testen.

## 4. Ziel-Navigation und Interaktionsprinzipien

Empfehlung: Mobil fünf direkte Bereiche **Home, Kalender, Chat, Adressliste, Menü** erhalten. Home → Start ist eine offene Sprachentscheidung. Desktop dieselben Ziele in einer dauerhaften linken Navigation; rechte Zusatzspalte nur bei echtem Nutzen. Formulare und Leseseiten bleiben schmal.

Header: kontextueller Rückweg, Bereich, nötigenfalls sichtbarer Kind-/Schulkontext, Glocke, persönliches Profil. Kinderumschalter für kindbezogene Ansichten; Klassenkontext für Chat/Events. Ein festes Objekt darf nach Kindwechsel nicht still dem neuen Kind zugeschrieben werden. URL, Policy und sichtbarer Kontext müssen zusammenpassen.

Menügruppen: **Klassenleben** (Aktuelles, Dokumente, Events, Mobilität, Fotos, Lehrkräfte), **Schule und Lernen** (freigegebene Schuldaten/Lernangebote/Speiseplan), **Mein Konto** (Profil, Familie, Datenschutz, Geräte/Benachrichtigungen, Sicherheit). Arbeitsbereich für Verwaltung separat. Menükonfiguration steuert Darstellung, niemals Berechtigung.

| Aufgabe | Zielweg / Vertrag |
|---|---|
| Tagesplan | Home → Datum → Kalender/Tag; Datum/Kind bleiben erkennbar, Entfall sichtbar, Quelle/Stand textlich. |
| Kindwechsel | Auswahl → dasselbe unterstützte Modul; Rechte neu prüfen, Objektseiten kontrolliert zur passenden Übersicht. |
| Kontakt | Adressliste → Person → Nachricht/E-Mail/Telefon; personengenaue Freigaben, tatsächlicher Actor. |
| Dokument | Suche/Filter → verfügbare PDF-Variante; geschützte Route, Suche beim Zurück erhalten. |
| Freigabe | Familie → Kind → Datenschutz → Zweck; Version, Wirksamkeit, Folge und Guardian-Entscheidungen getrennt. |
| Schulzugang | Familie → Kind → angebotene Funktion → Zugang; Freigabe, Opt-in, Credentials, Test und Datenstand getrennt. |
| Avatar | Profil → Profilbild → Designer → übernehmen → speichern; Draft/gespeichert unterscheiden. |
| Administration | Arbeitsbereich → Schule/Klasse → erlaubtes Objekt; lokale/globale Reichweite sichtbar. |

## 5. Komponentenvertrag

Empfehlung für die spätere Umsetzung; kein Auftrag für eine allgemeine UI-Bibliothek.

| Komponente | Vertrag |
|---|---|
| Shell/Seitenkopf | Ein H1, Kontextzeile, konsistenter Rückweg, höchstens eine Hauptaktion. Feste Leisten reservieren Platz einschließlich Safe Area. |
| Button/IconButton | Primär/sekundär/tertiär/destruktiv; Text oder zugänglicher Name, mindestens 44×44 px Projektziel, empfohlen 48×48 für häufige Touchaktionen. Fokus, Disabled-Grund, Ladezustand ohne Layoutsprung. |
| Link/Karte | Link navigiert, Button handelt; keine verschachtelten Interaktionen oder Klick-DIVs. Ganze Karte nur bei eindeutigem Ziel. |
| Field | Eindeutige ID/Label, Hilfe/Fehlerzuordnung, korrektes Type/Autocomplete, verständliche Pflichtangabe. Ein Label nicht für zwei Inputs. |
| Toggle | Native Checkbox, verständlicher Name/Textstatus/Reichweite. Sofort oder nach Speichern eindeutig; bei Fehler Rollback und Meldung. |
| Formular | Eingaben bei Fehlern erhalten, Zusammenfassung fokussieren, Feldfehler zuordnen. Zustände unverändert/geändert/speichert/gespeichert/Fehler. Jeder Save-Scope ändert nur eigene Felder. |
| Tabs | Links für URL-Unterseiten; ARIA-Tabs nur für Panels mit vollständiger Tastatursteuerung. Überlaufhinweis, Fokus sichtbar halten. |
| Dialog | Nativer Dialog, Name, passender Startfokus, Escape/Rückfokus, Close-Button, Dirty-State-Regel. Kein pauschales Bestätigungswort für harmlose Änderungen. |
| Status | Erfolg, ausstehend, leer, nicht freigegeben, veraltet, Quelle gestört, offline getrennt. Text/Icon zusätzlich zu Farbe, Live-Ansage nur bei Änderung. |
| Tabelle/Liste | Echte Überschriften, zugängliche Sortierung, mobile Labels erhalten; Nulltreffer mit Filter-zurücksetzen. |
| Datenstand | Quelle, letzter erfolgreicher Abruf und aktueller Versuch getrennt. Seitenreload bedeutet nicht automatisch frischen Import. |
| Auswahl-Karussell | Eigenständiger horizontaler Bereich mit Klick/Tastatur/Pfeilen/Wischen, eindeutiger Auswahl und bedingtem Fade; keine Rotation. |

CSS: bestehende Theme-Variablen zu einem kleinen Tokenvertrag für Text, Oberfläche, Rand, Aktion, Status und Fokus konsolidieren. Semantische Statusfarben behalten Bedeutung. rem-Größen, wenige begründete Breakpoints; Komponentenregeln ersetzen alte Regeln statt neue Patchlagen anzuhängen. Server-HTML bleibt Grundweg, JS ergänzt Interaktionen.

## 6. Seiten- und Routenmatrix

Alle Oberflächenfamilien unten; Anhang inventarisiert jede explizite Projektroute. Allauth-/Django-/Wagtail-Unterpfade sind Bibliotheksgrenzen und nicht einzeln UI-getestet.

| Routenfamilie | Zielzustand / Prüfung |
|---|---|
| `/accounts/…`, `/einladung/`, `/invitation/<token>/` | Login, Timeout, MFA, Passwortmanager, neutrale öffentliche Fehler. |
| `/registrieren/`, `/familie/start/<token>/`, Verifizieren/Aktivieren | Nächster Schritt/Prüfstatus/Wiederaufnahme; keine Rechte durch Selbstbehauptung. |
| `/onboarding/…`, `/tutorial/…` | Fortschritt, freiwillige Zwecke, Pflicht/optional, Pause und Fortsetzung. |
| `/`, `/familie/ansicht/…` | Tages-/Kindkontext, vollständige Detailwege; Kontextwechsel bewusst und policygebunden. |
| `/hausaufgaben/<id>/erledigt/` | Lokaler Status mit Serverbestätigung/Rollback, offene Elternrolle. |
| `/kalender/`, `/kalender/verbinden/`, `/schedule/…` | Tag mobil/Woche Desktop, Filter/Datum erhalten, Abo-/Tokenrechte. |
| `/chat/`, `/chat/<uuid>/ansicht/`, `/chat/rooms/…`, `/chat/messages/…` | Liste/Verlauf, Polling/Entwurf/Fokus, Meldung/Rücknahme/Moderation. |
| `/chat/direkt/…`, `/chat/nachricht/…/anhang/` | Persönliche Unterhaltung/geschützter Anhang; keine Sicht allein durch Adminrolle. |
| `/kontakte/`, `/schueler/`, `/mehr/lehrkraefte/` | Personengenaue Freigaben, passende Table/Card-Semantik und Aktionen. |
| `/mehr/` | Stabile Begriffe, Gruppen und getrennter Arbeitsbereich. |
| `/mehr/dokumente/`, `/documents/…` | Erreichbarer geschützter Download, Varianten/Version, Suchzustände. |
| `/mehr/aktuelles/…`, `/posts/…`, `/comments/…` | Lesen/Schreiben/Status/Rechte; A-02 beheben. |
| `/mehr/veranstaltungen/…`, `/events/…`, `/items/…`, Reservierungsrouten | Eigene Teilnahme/Zusagen, Fristen, Menge, Belegung/Race-Konflikt, klare Bestätigung. |
| `/mehr/mobilitaet/…`, `/mobility/…` | Route zusätzlich als Liste, Treffpunkt ohne Drag-Pflicht, private Freigabe/Widerruf. |
| `/mehr/fotos/`, `/galleries/…`, `/photos/…` | Jahrgangs- und Ereignisübersicht, geschützte Thumbnails, Verarbeitung/Zuordnung, Kindfilter, Widerruf und Download-Gate nach Abschnitt 9. |
| `/biometrics/…` | Standardmäßig deaktiviert, nur nach Feature/Consent; keine Aktivierung durch Redesign. |
| `/mehr/speiseplan/` | Tag/Woche, Allergene als Text, veröffentlicht/fehlt/Quelle gestört. |
| `/einstellungen/profil/?tab=data` | Stammdaten, Save-Scope, Labels/Fehler, private Freigaben. |
| `…?tab=appearance`, `/profile/<id>/foto/`, `/familie/foto/…` | Bild-/Avatarvertrag, geschützte Auslieferung. |
| `…?tab=themes`, `/einstellungen/design/…` | Aktives Theme, reale Komponentenvorschau, Kontraste aller erlaubten Themes. |
| `…?tab=notifications/app/account`, `/mehr/benachrichtigungen/` | Kategorien/Gerät/Berechtigung trennen; parallele Einstellungen auf kanonischen Weg führen. |
| `/benachrichtigungen/…` | Postfach, ungelesen, neutraler Inhalt; Lesen-Aktion getrennt von reiner Navigation. |
| `/mehr/familie/?tab=overview/data/privacy/modules/add-child` | Kind-/Beziehungsstatus, Bildrechte, Zwecke und persönliche Schulzugänge getrennt. |
| `/mehr/einwilligungen/`, Widerrufrouten | Aktives Template heißt „Schuldaten auswählen“; Menüversprechen und gesamter Datenschutzumfang klären. |
| `/mehr/webuntis/…`, `/webuntis/kalender/<token>/` | Eigener Zugang, Featurefreigabe, Test/Sync/Datenstand und geheimes Abo getrennt. |
| `/abwesenheiten/` | Import, lokaler Entwurf, einmalige Meldung; Empfänger/Kind/Datum/Sendestatus eindeutig. |
| `/itslearning/…`, `/dav/…` | Lernplattform/Speicher, Quelle, Dateityp, Platz/Konflikt, geschützte Zugänge. |
| `/mehr/lernportale/` | Nur freigegebene Angebote; externer Wechsel kenntlich. |
| `/verwaltung/`, `/verwaltung/rollen/` | Rollen-/Objektscope sichtbar und serverseitig erzwungen. |
| `/verwaltung/schulen/…` | Schulen/Klassen, Suche, Importvorschau/Fehler und delegierte Reichweite. |
| `/verwaltung/adapter/…` | A-01/A-09; Freigabe getrennt von technischem Test/aktuellen Daten. |
| `/verwaltung/anmeldung/…`, `/verwaltung/familien-einladungen/` | Gültigkeit/Reichweite der Einladung, Tokens nicht dokumentieren/loggen. |
| `/verwaltung/themes/…`, `/verwaltung/menue/` | Darstellungsregeln, Rollen-Vorschau, Reihenfolge auch per Tastatur. |
| `/verwaltung/automatische-abmeldung/`, Chat-Aufbewahrung, Terminumfrage | Wirkungsbereich und Bestätigung; zentrale Policies erhalten. |
| `/mehr/systemstatus/`, `/mehr/ui-zustaende/`, `/pilot/melden/` | Diagnose im Arbeitsbereich; Feedback-/Fehlerstatus. |
| `/admin/`, `/cms/` | Bewusster Bereichswechsel, Rechte bei Direkt-URL; separate Bibliotheksabnahme. |
| `/praesentation/`, `/projekt/`, `/demo/` | Demo/Produkt klar, reduzierte Bewegung. |
| `/datenschutz/`, `/impressum/`, `/nutzung/`, `/open-source-lizenzen/` | Lesebreite/Erreichbarkeit, Inhalte separat fachlich prüfen. |
| Konto löschen, `/sessions/…` | Tragweite, Abbruch, Serverbestätigung; Polling verlängert Inaktivität nicht. |
| `/push/…`, Manifest, Service Worker, `/offline/`, `/health/`, `/scan/<token>/` | Neutrales Offline, keine dauerhaften privaten Caches; Token-/Objektprüfung. |

## 7. Responsive- und Accessibility-Kriterien

Testgrößen: 360×800 und 390×844 mobil, 320 px Reflow, 768×1024, 1024×768, 1440×900, 1920×1080; zusätzlich Smartphone quer, PWA und Softwaretastatur. Breakpoints aus Platzproblemen ableiten.

Qualitätsziel nach [WCAG 2.2](https://www.w3.org/TR/WCAG22/): kein Verlust bei 200 % Textvergrößerung; Reflow bei 320 CSS-px für normale Inhalte; Textkontrast mindestens 4,5:1, große Schrift 3:1, wichtige Nichttextkontraste 3:1. Tastaturbedienung, sichtbarer/nicht verdeckter Fokus, beschriftete Felder, Fehler und Statusmeldungen prüfen. Zielgrößen nach 2.5.8 mindestens 24×24 px oder zulässige Ausnahme; strengeres Projektziel bleibt 44 px, empfohlen 48 px für häufige Touchaktionen. Dragging erhält eine Alternative (2.5.7). Keine rechtliche Konformitätsbescheinigung.

Produktspezifisch:

1. Lange Schul-/Kindnamen, Fachnamen, E-Mails/Dateinamen: wesentliche Texte umbrechen, kein Seitenoverflow.
2. Fokus in Carousel/Settings-Tabs vollständig sichtbar; Fade, Header und Bottom-Bar überdecken keinen Fokusrahmen.
3. Chat/Formulare mit Tastatur: Eingabe, Status und Senden erreichbar. `100dvh` allein garantiert keine korrekte Tastaturbehandlung; echte Geräte prüfen.
4. Reduced Motion ohne Smooth-Scroll-/Scale-Pflicht; Forced Colors mit Umriss/Marker, Fade bei Bedarf aus.
5. NVDA mit Firefox/Chrome und VoiceOver/Safari, zusätzlich TalkBack: Titel, H1, Regionen, Dialognamen, Auswahlzustände, sparsame Live-Ansagen.
6. JS-Ausfall: Inhalte/Formulargrundwege bleiben bedienbar oder klarer Ersatz. Carousel als Optionsliste; notwendige Inhalte nicht ausschließlich in unerreichbaren JS-Dialogen.

## 8. Avatar-Designer und Karussell-Spezifikation

### 8.1 Assetbestand

| Bestand | Prüfergebnis |
|---|---|
| `avatar/Flat Assets/Flat Assets` | 356 echte SVGs; weitere 356 AppleDouble-Dateien unter `__MACOSX` sind keine Assets. Alle echten SVGs XML-parsebar; einfache Prüfung ohne Script-/ForeignObject-/Eventhandler-/externen Linkmarker. Keine vollständige SVG-Sicherheitszertifizierung. |
| Separate Atoms | 167: Kopf 46, Gesicht 30, Körper 30, Bart 16, Accessoires 8, sitzende Pose 11, stehende Pose 23, komplette Person 3. |
| Vorlagen | 105 Bust, 18 Sitting, 30 Standing, 36 Covid. |
| Statisch ausgeliefert | 167 Atoms, acht feste Presets unter `vendor/open-peeps`, drei UI-Icons. |
| Aktuelle Auswahl | Körper 8, Kopf 11, Gesicht 11, Bart 5 + Ohne, Accessoires 5 + Ohne, Hintergrund 7. 49 Auswahlwerte über sechs Kategorien; 40 echte Atomdateien verwendet. |
| Geometrie | Unterschiedliche Zeichenflächen: Kopf 473×567, Gesicht 289×293, Körper 818×733, Bart 280×230, Accessoires 392×138. Aktueller Composer platziert Prozentboxen auf 240×324. Posen/komplette Personen nicht beliebig als Körper-Layer austauschbar. |
| Herkunft/Lizenz | Kein eigener Lizenz-/Manifestnachweis im geprüften Avatarordner; Open Peeps fehlt in `open_source_licenses.html`. Herkunft/Paketversion/Nutzungsrecht vor Katalogerweiterung dokumentieren; keine Lizenz aus Dateinamen ableiten. |

`avatar_designer.py` enthält erlaubte Optionen und Seedprüfung; `avatar_tags.py` und `app.js` duplizieren Reihenfolge/Geometrie. Der `v2:<Index>…`-Seed hängt an der Listenreihenfolge: kompatibel anhängen, bestehende Indizes nicht umsortieren. Schemawechsel benötigt Migration. Empfohlenes gemeinsames Manifest: stabile ID, lokale URL, Kategorie, deutscher Name, Zeichenbox, Transform/Anker, Kompatibilität, Ursprung.

**Grenze:** alle Dateien strukturell inventarisiert, nicht jede Kombination visuell abgenommen. Prozentboxen beweisen keine richtige Hals-/Gesichts-/Brillenposition. Jede Option gegen Referenz und gezielte Paare (große Haare, Hijab, Brille, Bart, breite Kleidung) bildlich prüfen. Bestehende Presets bleiben Fallback; Katalog nicht allein nach Dateinamen freigeben.

### 8.2 Moderne horizontale Auswahl, unabhängig vom Avatar

Empfehlung: eigenständige Auswahlkomponente; ihr Auswahlereignis aktualisiert den Avatar-Draft. Andere Formulare/Menüs werden dadurch nicht pauschal Karussells.

Desktop: großzügige Vorschau links, Kategorieauswahl und begrenzte Optionsreihe rechts, sichtbare Pfeile. Mobil: kompakte Vorschau oben, darunter Kategorien/große Kacheln, Aktionen unten im Designer. Kein endloses Durchscrollen aller sechs Raster. Bei niedriger Höhe Vorschau verkleinern und Sticky-Bindung lösen, bevor Aktionen unerreichbar werden.

Gestalterische Startwerte zur Abstimmung: mobil 88–104 px breite Kacheln mit angeschnittener nächster Kachel; Desktop 112–128 px, 12 px Abstand, Grafik 56–72 px. Kurze Namen bis zwei Zeilen. Auswahl zeigt Rand/Haken/Label; Hover hebt nur leicht an. Farb-/Positionswechsel etwa 120–180 ms, keine Zoom-/3D-/Parallax-Pflicht.

**Fade:** 16–24 px breite Randverläufe nur dort, wo weiterer Inhalt liegt. Anfang links ohne Fade, Ende rechts ohne Fade; kein Overflow = keine Fades. Innenabstand/Scroll-Padding schützen erste/letzte Option und Fokus. Dekorative Overlays mit `pointer-events:none` bevorzugen statt Maske über Text/Fokus. Fokus vollständig einblenden oder Fade dort aussetzen; Pfeile außerhalb der Fadefläche. Forced Colors kann Fades deaktivieren.

**Scroll:** nativer horizontaler Scroll für Touch/Trackpad, `scroll-snap-type:x proximity` als Ausgangspunkt. Vertikales Scrollen und Zoom erhalten. Pfeile bewegen eine sichtbare Gruppe mit Überlappung. Scrollen verändert keine Auswahl; Klick/Tastatur ändert genau eine Kategorie. Kein Autoplay/Loop/Hoverwechsel. Nach Kategorie-/Viewportwechsel Overflow neu berechnen und Auswahl sichtbar halten. Das Wort „Slider“ begründet keine numerische Range-Semantik: es sind diskrete Varianten.

### 8.3 Semantik und Draft-Vertrag

Pro Kategorie genau ein Wert: **native Radios im Fieldset**, Labels als Kacheln. Tab erreicht die Gruppe/gewählte Option; Pfeile wechseln Werte, Space wählt; Fokus sichtbar nachführen. Ohne Bart/Accessoire ist eine reguläre Option, Farben bekommen Namen. Das [WAI-ARIA-Radiogruppenmuster](https://www.w3.org/WAI/ARIA/apg/patterns/radio/) passt zur Exklusivauswahl. Kategorien als korrekt implementierte Tabs oder normale serverseitige Links.

Die Oberfläche ist kein rotierender Foliensatz. Daher nicht blind Carousel-/Slide-Rollen auf Radios legen. Beschriftete Navigationskontrollen und Kontrollierbarkeit aus dem [WAI-ARIA-Carousel-Muster](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) dienen als Orientierung; Optionssemantik bleibt Auswahl. Vorschau kurz beschreiben, dekorative Layer verbergen, Status sparsam ansagen (z. B. „Frisur Dutt ausgewählt“), nicht bei jedem Scrollpixel.

Drei Werte trennen: **gespeichert**, **Profilformular-Draft**, **Dialog-Draft**. Öffnen kopiert Formular-Draft; Escape/Abbruch verwirft Dialogänderungen. „Übernehmen“ aktualisiert nur Formular und meldet „Übernommen – Profilbild noch speichern“. Äußeres Speichern sendet nur Bild-Scope; erst Servererfolg heißt gespeichert. Direktes Speichern im Designer ist eine offene Alternative. Zufall ändert nur Draft, sinnvoll mit Rückgängig. Bei Assetfehler bisherige Vorschau erhalten, Fehler/Retry anzeigen.

### 8.4 Avatar-Abnahme

- 360 px: Vorschau, Kategorie, mindestens zwei große Optionen und Aktionen ohne Seitenoverflow erreichbar; Querformat/Zoom.
- Erste/letzte Option lesbar; Pfeile bei passendem Inhalt korrekt; kurze/lange Kategorien ohne veralteten Fade.
- Nur Tastatur: Kategorie/Option/Zufall/Abbruch/Übernahme und Rückfokus funktionieren; Fokus und Auswahl unterscheiden.
- Escape/Close/Backdrop senden keinen POST; Übernehmen ändert keine Freigaben, Stammdaten-Save erhält Avatar.
- Reload erhält Seed, Server-/Clientvorschau gleiche Position, Katalogerweiterung erhält Bestandsseeds, ungültige Werte abweisen.
- Kein externer Assetabruf, kein Foto-/Biometrierecht; beschädigte/leere Kategorien verständlich behandeln.

## 9. Fotos und Galerien

### 9.1 Zielbild und verbindliche Produktentscheidungen

Die Galerie ist ein geschützter Erinnerungsbereich der Klasse, keine offene Fotoablage. Beim Upload wählt die berechtigte Person zuerst mindestens **Schuljahr** und **Ereignis**; die Veröffentlichung erfolgt innerhalb der aktuell berechtigten Klassengemeinschaft. Die persönliche Zustimmung der hochladenden Person deckt ihren Upload ab. Die Darstellung anderer erkennbarer Personen bleibt an die im Projekt geltende Foto-Freigabe gebunden. Das ist keine neue zusätzliche Einzelfreigabe pro Bild, verhindert aber, dass ein Upload die zentrale Schutzentscheidung einer anderen Familie stillschweigend ersetzt.

Die von der Nutzerseite gewünschte Vereinfachung - Eltern stimmen grundsätzlich der internen Klassenfotogalerie zu - ist als **Entscheidung offen** zu dokumentieren: Sie würde den vorhandenen personengenauen Freigabe- und Widerrufsvertrag fachlich verändern. Bis zu einer bestätigten Anpassung bleibt die bestehende Widerrufslogik wirksam.

**Beschluss für die Präsentation:** Die KI-gestützte Zuordnung gehört zum vorgesehenen Funktionsumfang. Im Verwaltungsbereich wird sie pro Klasse kontrollierbar: das schnelle Modell kann für die Präsentation aktiviert, deaktiviert und für erste bestätigte Referenzen verwendet werden; das erweiterte Modell besitzt einen getrennten Schalter und bleibt zunächst nicht aktiv. Beide Modelle liefern ausschließlich Vorschläge. Eine berechtigte Person bestätigt oder verwirft jeden Treffer, bevor er als Zuordnung oder Referenz gilt. Diese Konfiguration ist jederzeit sichtbar und reversibel; Deaktivieren stoppt neue Analysen und lässt keine automatische Nachverarbeitung zu.

**Bestehender Stand:** Der Code hat derzeit nur einen globalen Umgebungs-Schalter `BIOMETRIC_SEARCH_ENABLED` und genau eine Pipeline-ID. Die Modelle können daher weder im Admin-Dashboard getrennt geschaltet noch pro Klasse unabhängig betrieben werden. Die vorhandene Vision-Strecke liefert bereits Vorschläge und kennt bestätigte Referenzen, aber sie muss vor dem Präsentationsbetrieb um einen administrativen Klassenmodus, getrennte Modellzustände und eine nachvollziehbare Trainings-/Referenzübersicht ergänzt werden. Die im Projekt dokumentierte Einwilligungs- und Widerrufsprüfung bleibt dabei Bestandteil jedes tatsächlichen Analyse- und Referenzvorgangs.

**Empfehlung für die Informationsarchitektur:**

1. **Galerien**: Schuljahre als ruhige, große Einstiegskarten, etwa „2025/26“, mit Anzahl der Ereignisse und einem repräsentativen, geschützten Vorschaubild.
2. **Ereignisse eines Schuljahrs**: Karten für Klassenfahrt, Weihnachtsfeier, Theaterbesuch oder Ausflug mit Datum/Jahr, Titel, Bilderanzahl und sichtbarem Verarbeitungsstand. Ein Hover kann Desktop-Karten behutsam vergrößern und Informationen einblenden; Mobil öffnet ein Tippen dieselbe Karte. Kein Inhalt darf nur durch Hover erreichbar sein.
3. **Ereignisgalerie**: wahlweise ein responsives Raster als Standard und eine einzelne fokussierte Ansicht als bewusste Option. Wischen/Pfeile wechseln Fotos; automatisches Abspielen ist standardmäßig aus und nur nach ausdrücklichem Start möglich, jederzeit stoppbar und bei Reduced Motion deaktiviert.
4. **Eigene Kinder**: Der Filter „Meine Kinder“ erscheint nur, wenn belastbare manuelle oder zugelassene KI-Zuordnungen existieren. Er filtert lokal sichtbare Ergebnisse; keine Zuordnung darf aus dem Filter abgeleitet oder sichtbar behauptet werden.

Die Referenz „Card Transition Shift Layout“ von FreeFrontend beschreibt eine per Mausbewegung reagierende, sich ausdehnende Karte. Übernommen wird lediglich das Prinzip einer klaren, ereignisbasierten Kartenhierarchie und sanfter Übergänge. Die stark mauszentrierte Interaktion ist für Touch und Tastatur kein primäres Bedienmuster. Keine Übernahme fremden Tailwind-/JavaScript-Codes.

### 9.2 Upload, Metadaten und Zuordnung

**Verbindliche Metadaten beim Anlegen eines Ereignisses:** Schuljahr, Ereigniskategorie, Ereignistitel, Datum oder Zeitraum, zugehörige Klasse/Schule und verantwortliche hochladende Person. Kategorien beginnen als kuratierte Auswahl (zum Beispiel Klassenfahrt, Weihnachtsfeier, Schulausflug, Theaterbesuch, Sporttag, Sonstiges); „Sonstiges“ verlangt einen Titel. Freitext-Tags wie Schnee, Strand oder Sport sind ergänzende, nachrangige Metadaten und keine Voraussetzung für den Upload.

Die personenbezogene Zuordnung wird vom Ereignis-/Uploadvorgang getrennt:

| Weg | Zweck | Rechte und Ergebnis |
|---|---|---|
| Upload | Bilder einem Ereignis hinzufügen | Berechtigte Person, Metadaten und Verarbeitungsstatus; keine erzwungene Namensauswahl beim Upload. |
| Manuelle Zuordnung | Personen auf bereits sichtbaren Bildern auswählen oder entfernen | Eigene, rollenbasierte Arbeitsseite; jede Änderung nachvollziehbar und widerrufbar. |
| KI-Vorschläge | Mögliche Personen nur vorschlagen | Schnelles Modell im Präsentationsmodus aktivierbar; erweitertes Modell separat steuerbar. Kein automatisches endgültiges Tagging, keine automatische Veröffentlichung aufgrund eines Vorschlags. |
| Filter „Meine Kinder“ | Bereits bestätigte Zuordnungen nutzen | Nur für aktuell berechtigte Sorgeberechtigte; leere Ergebnisse verständlich erklären. |

Eine Benachrichtigung „Neue Fotos von der Klassenfahrt“ darf Ereignis und Anzahl nennen, aber keine Namen, Bildinhalte oder KI-Vermutungen preisgeben. Sie ist eine Opt-in-Benachrichtigung pro Klasse/Ereigniskategorie; die tatsächliche Sichtbarkeit wird erst beim Öffnen erneut serverseitig geprüft.

### 9.3 Download-Gate und geschützte Auslieferung

**Aktuelle Entscheidung:** Es gibt vorerst keinen sichtbaren Download einzelner Bilder oder ganzer Ereignisse. Die geschützte Bildanzeige darf nicht durch eine Download-Schaltfläche oder ZIP-Funktion ergänzt werden.

**Entscheidung offen:** Falls Downloads später freigegeben werden, ist vor Umsetzung festzulegen, ob sie allgemein erlaubt, einzeln beantragt oder rollenbasiert möglich sind. Jeder erlaubte Download braucht eine serverseitige Autorisierung, eine nachvollziehbare Auditspur mit tatsächlichem Konto, Bild/Ereignis, Zeit und Zweck der Freigabe. Browserseitiges Verbergen eines Kontextmenüs oder eines `download`-Attributs wäre kein Schutz und zählt nicht als Download-Gate. Screenshots können technisch nicht verhindert werden; diese Grenze wird transparent benannt, ohne daraus den Downloadweg zu öffnen.

### 9.4 Gestaltung, Technik und Abnahme

- Karten verwenden feste Bildverhältnisse und serverseitig erzeugte, geschützte WebP-/AVIF-Thumbnails; Originale werden niemals in einer Übersichtsseite geladen. `loading="lazy"`, Breiten-/Höhenangaben und `object-fit:cover` verhindern Layoutsprünge.
- Das Ereignisraster passt die Spalten an verfügbaren Platz an; auf 360 px sind zwei ausreichend große Karten nur sinnvoll, wenn Titel, Status und Touchfläche lesbar bleiben. Sonst zeigt die Ansicht eine Karte pro Reihe. Desktop darf dichtere Raster zeigen.
- Bilddetail als nativer Dialog oder eigene Route: Name des Ereignisses, Bildposition, Vor/Zurück, Schließen und aktuelle Filterlage sind tastaturbedienbar; Fokus kehrt zurück. Pfeil-/Wischgeste ist Ergänzung, kein Ersatz.
- Zustände unterscheiden: Upload läuft, Verarbeitung offen, freigegeben, zurückgezogen, nicht sichtbar wegen Freigabe, schnelles Modell an/aus, erweitertes Modell an/aus, KI-Vorschlag offen, manuell zugeordnet. Farbe ist nie das einzige Signal.
- Testfälle: mehrere Schuljahre/Ereignisse, keine Bilder, lange Titel, 360 px, Touch/Tastatur/Screenreader, schnelles/erweitertes Modell je Klasse ein- und ausschalten, Referenz hinzufügen/widerrufen, ein Kind mit/ohne bestätigte Zuordnung, Widerruf nach Zuordnung, fremde Klasse, abgelaufene Mitgliedschaft, Thumbnail-/Originalrechte, kein Download-UI und späterer protokollierter Downloadweg.

## 10. Chat: Jugend- und Kinderschutz mit niedriger Latenz

### 10.1 Iststand und fachliche Grenze

Der aktuelle Filter ist **kein englisches Modell**: `chat/safety.py` maskiert eine kleine deutsche Liste direkter Beleidigungen per Regex und protokolliert nur die Trefferzahl. Er normalisiert bereits Groß-/Kleinschreibung, Akzente, Leerzeichen, Punkte und einen Teil der Leetsprache. Kontext, Wiederholung, Zielperson, indirekte Abwertung und Eskalation erkennt er nicht. Die Feststellung „Mobbing“ darf daraus nicht automatisch abgeleitet werden; sie verlangt immer eine menschliche Prüfung.

Der Filter muss insbesondere `A.R.S.C.H.L.O.C.H`, Leer-/Sonderzeichen, Unicode-Varianten, wiederholte Zeichen und gängige Ziffernersatzformen robust behandeln. Das Original darf weder in Audit-Events noch in einem separaten Sicherheitslog dupliziert werden. Es bleibt ausschließlich in der bereits geschützten Chat-Nachricht und unterliegt deren Zugriff- und Löschregeln.

### 10.2 Empfohlenes Zielsystem

Kein generatives LLM gehört in den Sendeweg. Es wäre für eine kurze Chatnachricht unverhältnismäßig langsam, schwer verlässlich zu kalibrieren und nicht gezielt nachtrainierbar. Vorgesehen ist eine lokale, mehrstufige **Hinweis- und Moderationsschicht** im bestehenden Django-Monolithen:

| Stufe | Aufgabe | Latenz- und Produktverhalten |
|---|---|---|
| 0: kanonisieren | NFKC/Casefold, unsichtbare Zeichen und Satzzeichen behandeln, Akzente/Leet-/Homoglyphen abbilden, Zeichenwiederholungen begrenzen; Original unverändert bewahren | deterministisch, serverseitig maßgeblich; clientseitig nur als sofortige UX-Hilfe zulässig |
| 1: Regeln | versionierte Wörter, Phrasen, Aliaslisten und Regexe für direkte Beleidigung/Drohung; eindeutige Treffer können wie heute maskiert und mit Grundcode versehen werden | im Request; kein Warten auf ein Modell |
| 2: deutscher Klassifikator | mehrere Hinweise bewerten: beleidigend, diskriminierend, bedrohlich, sexualisiert/grenzüberschreitend, gezielt gegen eine Person | nach dem Speichern; nie Nachricht oder UI für mehrere Sekunden blockieren |
| 3: Verlaufssignal | begrenztes Zeitfenster pro Raum und möglicher Zielperson: Wiederholung, mehrere Verfasser, Meldungen, Antwortketten, steigende Scores | erzeugt nur einen Moderationshinweis, keine automatische Sanktion |
| 4: Mensch | Moderationsliste mit Nachrichtreferenz, Gründen, Scores, Modell-/Regelversion und Entscheidung | bestätigt, verwirft oder korrigiert Labels; daraus entsteht kuratierter Trainingsbestand |

Der Browser zeigt nach Stufe 1 sofort den normalen Sendezustand. Stufe 2/3 laufen aus einer DB-gestützten Aufgabenliste nach Commit; die Polling-Aktualisierung kann einen späteren, neutralen Hinweis liefern. Dafür wird ein expliziter Management-Command/Scheduler eingesetzt, **nie** ein Dashboard-GET. Falls ein quantisiertes Modell auf Zielhardware wiederholt unter dem Messziel bleibt, darf Stufe 2 zusätzlich synchron nach dem Speichern laufen; die Nachricht bleibt in jedem Fall ohne Dreisekunden-Wartezeit sichtbar.

### 10.3 Modell- und Trainingsentscheidung

Als Startbasis wird kein angeblich universelles kostenloses Chat-LLM verwendet. Der passende Baustein ist ein lokal betriebenes, fein abstimmbares deutsches Encoder-Modell: **`deepset/gbert-base`** (MIT) als Trainingsbasis, zunächst mit einem eingefrorenen, versionierten Klassifikationskopf. Es ist deutschsprachig und für eigenes Fine-Tuning geeignet. Als ausschließlich zu evaluierender Ausgangscheckpoint kann `deepset/bert-base-german-cased-hatespeech-GermEval18Coarse` dienen; er ist auf GermEval-2018-Hassrede trainiert und CC-BY-4.0 lizenziert. Er darf nicht als fertiger Mobbingdetektor bezeichnet werden: GermEval enthält manuell annotierte öffentliche Beiträge, keine Klassenchat-Konversationen.

Die Auslieferung erfolgt als lokal abgelegtes, gepinntes und geprüftes ONNX-Modell mit ONNX Runtime; Quantisierung wird nur übernommen, wenn die Messung gegen die Float-Referenz keine unvertretbare Verschlechterung der relevanten Klassen zeigt. Beide Kandidaten und jede Modellrevision brauchen vor Aktivierung Lizenznachweis, SHA/Revision, Model Card, Herkunft der Trainingsdaten, deutsche Testmenge und Freigabeprotokoll.

Lernen erfolgt nicht automatisch aus privaten Chats. Moderierende Personen können einen Hinweis als zutreffend/falsch oder mit einer Kategorie versehen; erst nach Redaktionsprüfung und Datenminimierung fließen solche Beispiele in einen getrennten, zugriffsbeschränkten Trainingssatz. Zusätzliche Begriffe/Aliasformen werden als überprüfbare Regelrevision eingespielt. Jeder Modellwechsel wird offline evaluiert, kalibriert, versioniert und kann sofort auf die vorige Revision zurückgesetzt werden.

### 10.4 Sicherheitsprotokoll und Bedienoberfläche

Ein neues `ChatSafetyAssessment` referenziert genau eine Nachricht und speichert nur: Stufe, Status (`pending`, `complete`, `failed`), `severity` (`none`, `light`, `medium`, `high`), kategorisierte Grundcodes, Scores/Schwellen, Regel- und Modellrevision, Ausführungszeit, Prüffrist und Moderationsentscheidung. Der Verlaufshinweis referenziert die beteiligten Assessments statt Chattext zu kopieren. Sichtbar ist er nur für dafür berechtigte Moderation; das Kind erhält keine stigmatisierende Kennzeichnung. `high` erstellt eine vorrangige Prüfaufgabe, blockiert oder bestraft aber nicht automatisch.

Die Moderationsansicht erklärt knapp, dass es ein algorithmischer Hinweis ist, zeigt die Gründe getrennt von der Nachricht, ermöglicht „unauffällig“, „beobachten“, „ansprechen“, „regelwidrig“ sowie eine Korrektur des Labels und protokolliert die Entscheidung. Eine echte Chatmeldung bleibt ein gleichwertiger, sofort verfügbarer Weg. Die Ansicht wird mobil mit klaren Filterchips und ausreichend großen Aktionen geplant; sie ist kein überladenes Kontroll-Dashboard.

### 10.5 Mess- und Abnahmevertrag

- **Sendeweg:** 95 % der reinen Regelprüfung unter 30 ms auf Zielhardware; kein Modellaufruf darf das Absenden um mehr als 150 ms verzögern. Bei nicht verfügbarer Analyse wird die Nachricht gesendet und die Assessment-Aufgabe als fehlgeschlagen/wiederholbar markiert.
- **Modellweg:** p95 vom Speichern bis Assessment unter 2 Sekunden im normalen Präsentations-/Testbetrieb; tatsächliche CPU- und Lastmessung entscheidet über die endgültige Grenze. Kein unbewiesenes Millisekundenversprechen.
- **Robustheit:** Synthetische deutschsprachige Fälle für Punkte/Leerzeichen/Leet/Unicode/Zeichenwiederholung, direkte und indirekte Abwertung, Ironie, Gegenrede, Zitat, Gruppen- und Zielpersonenbezug. Keine echten Kinderdaten in Testfixtures.
- **Qualität:** separat pro Kategorie Präzision/Recall/F1, Fehlalarme, übersehene Meldungen und Kalibrierung ausweisen. Vor Aktivierung Grenzwerte zusammen beschließen; ein einzelner Gesamtscore genügt nicht.
- **Rechte/Datenschutz:** fremde Klassen, widerrufene Mitgliedschaft und Nachrichten außerhalb der Aufbewahrung erscheinen in keiner Moderationsliste. Audit enthält keine Nachrichtentexte, Tokenfolgen oder Rohprompts. Löschung einer Nachricht löscht/entkoppelt auch Assessments nach der festgelegten Frist.

Rechtsgrundlage, Rollen, Aufbewahrungsfrist, Einsichtsrecht und Umgang mit dringenden Gefährdungshinweisen werden vor realem Betrieb als eigene Fach- und Datenschutzentscheidung ergänzt. Für die Präsentation bleibt die Schicht deutlich als Demo/Hinweisfunktion gekennzeichnet.

Quellen für die Modellentscheidung: [`gbert-base` Model Card](https://huggingface.co/deepset/gbert-base), [GermEval-2018-Daten und Annotationen](https://github.com/uds-lsv/GermEval-2018-Data), [ONNX-Runtime-Optimierung und Quantisierung](https://huggingface.co/docs/optimum-onnx/onnxruntime/usage_guides/pipelines). Die GermEval-Forschung betont selbst die fehlende Gesprächs- und Teilnehmerkontextinformation; daraus folgt die menschliche Prüfung statt einer automatischen Mobbingentscheidung.

## 11. WebUntis-/Adapter-Datenmodellbefund

`PortalAdapter` hält Provider/Adresse/Schulzuordnungen, `PortalAdapterModule` Funktionen/Klassenfreigaben, `ChildModuleConnection` kindbezogenes Opt-in ohne Credentials. `WebUntisConnection` hält verschlüsselte persönliche Zugänge je User/Kind, Präferenzen und Importdaten. Unterricht/Aufgaben sind per Fingerprint je Verbindung eindeutig. Brauchbare Ausgangsbasis, noch kein generischer Mehrschulvertrag.

| Befund | Konsequenz / Empfehlung |
|---|---|
| Legacy-`school` und M2M-`schools` parallel; Policy verknüpft beide mit OR. | Eindeutige Quelle/Migration; Providerdefinition, Schule und konkrete Instanz unterscheiden. |
| Verbindung ohne Instanz-FK, fester Server/Schulcode. | Verwaltungsadresse beeinflusst tatsächlichen persönlichen Zugang nicht verlässlich. Explizite geprüfte Instanz; keine beliebige Ziel-URL aus Kinderformular. |
| Globale Fach-/Lehrkraftcodes. | Gleicher Code kann schulabhängig anders heißen. Scope auf Instanz/Schule und ggf. Referenzperiode, passende Unique-Constraints. |
| Kind/Modul-Opt-in gemeinsam, Credentials User/Kind; `set_connection_state()` aktualisiert Kindstatus für Provider. | Ein Guardian kann Verbunden sehen, obwohl nur anderer Credentials hat; Entfernen kann gemeinsamen Status zurücksetzen. Gemeinsames Opt-in von persönlichem Zugangsstatus trennen. |
| Katalogschalter, Modulstatus, Featurezustand, Credentialstatus und letzter Sync getrennt. | Freigegeben heißt nicht getestet/aktuell. UI zeigt Schule erlaubt / du aktiviert / Zugang geprüft / Datenstand separat. |
| Allgemeines Adapterdetail hat keinen Connection-Test; Aktivieren setzt READY. Persönlicher WebUntis-Test existiert. | Nur implementierte Testarten anbieten: Konfiguration, Credentials, Probeabruf. Speichern nicht als Verbindungserfolg ausgeben. |
| Core-Views importieren konkrete Fach-ORM-Modelle. | Modulgrenzen teilweise durchbrochen; kleine interne Query-/Command-Services und Anzeige-DTOs, kein Netzwerkdienst. |

**Zielvertrag, Entscheidung offen:** Providerdefinition beschreibt Adaptercode/Fähigkeit; konkrete Schulintegration Endpunkte/Instanz; persönliche Connection referenziert Integration, Actor, Kind. Freigabe, kindbezogene Aktivierung, Credentialzustand getrennt. Dies sind konzeptionelle Namen, keine angelegten Tabellen.

Anzeige-/Importvertrag: Quelle/Instanz, externe ID/Fingerprint, Kind-/Klassenscope, Zeitraum/Zeitzone, Fachstatus, Quelländerungs-/Abrufzeit und Löschfrist. Gemeinsame Anzeige-DTOs sind sinnvoll; nicht alle Fremddaten blind in ein universelles JSON-Modell verschieben. Lokaler Erledigtstatus getrennt von Quellaufgabe und tatsächlichem Actor.

Migration mit zwei Schulen/gleichen Codes, zwei Kindern/Guardians, abgelaufener Beziehung, Klassenwechsel, Modul-Deaktivierung, entfernter Verbindung und alten Abos testen. Idempotenz/Widerruf/Löschung erhalten. Abwesenheits-Browsermeldung bleibt innerhalb ADR-030; generischer Adaptervertrag erteilt keine Schreibfreigabe.

## 12. Umsetzungsetappen

Empfehlung für anschließende Freigabe, keine begonnene Umsetzung. Jede Etappe mit eigenem Gate; neue Fachfunktionen außerhalb.

| Etappe | Ergebnis / Gate |
|---|---|
| 0 Befunde/Beschlüsse | P1 synthetisch reproduzieren, Dokumentation/Entscheidungsreichweite klären; fremder Zugriff, verborgene Kommentare und Scope-Nebenwirkungen schließen. |
| 1 Funktionaler Unterbau | Dokument-/Kommentarwege, Chat, Status, Sendefehler; GET-Seiteneffekte auslagern. Kritische Wege mit Fehler/Abbruch/Rechten bestanden. |
| 2 Shell/Komponenten | Navigation/Kindkontext, Fields/Buttons/Toggle/Dialog/Status/Table; CSS-Verantwortung. 360 px, Keyboard, Zoom, Themes, Safe Area. |
| 3 Alltag | Dashboard/Kalender/Aufgaben/Chat/Kontakte; vollständige Wege, Datenstand, Suche, Entwurf, Kontextwechsel. |
| 4 Avatar | Auswahlkomponente, Manifest/Geometrie, Draft/Savevertrag; Abschnitt 8.4 und Profilregressionen. |
| 5 Übrige Bereiche | Familie/Consent, Events/Galerie/Mobilität, Verwaltung/Onboarding/öffentliche Seiten; Foto-Ereignismodell, Download-Gate, Rollen-/Klassenisolation und Widerruf. |
| 6 Abschluss | gezielte Regression, echte Geräte, kurze Doku, kleine nachvollziehbare Commits; Restpunkte explizit. Deployment nur im dafür freigegebenen Auftrag. |

Modellstrategie laut Nutzer: Astra für Audit/Architektur/Analyse, Terra für klar begrenzte Umsetzung nach Abstimmung, kleines Modell für knappe Zusammenfassung. Keinen technisch nicht erfolgten Modellwechsel behaupten. Keine langen Fortschrittsberichte allein zur Kommentierung.

## 13. Test- und Abnahmekriterien

| Test | Synthetischer Ablauf / Erwartung |
|---|---|
| Rechte | Klassenadmin A gegen Adapter B, GET/jede POST-Aktion: neutral verweigert, keine Änderung. |
| Kommentare | Ausblenden/zurückziehen und Detail/HTML lesen: kein Originaltext, korrekter Status. |
| Profil | Bildwechsel bei freigegebenen Kontakten, danach Stammdaten: nur Scopefelder ändern. |
| Dokumente | Suche/Original/Formular/fehlende Variante/fremde Klasse: richtige geschützte Datei oder neutraler Fehler. |
| Chat | Zwei Clients, neue Nachricht bei lokalem Entwurf, Ausfall/Retry: kein Entwurf-/Fokusverlust, keine doppelten Posts. |
| Chat-Kinderschutz | Kanonisierung/Regeln, asynchrones Assessment, Ziel-/Verlaufshinweis, Fehlalarmkorrektur, Rechte/Löschung und Messgrenzen nach Abschnitt 10. |
| Kontext | Zwei Kinder verschiedener Schulen, Home/Kalender/festes Objekt: sichtbarer korrekter Kontext, kein Datenmix. |
| Consent | Mehrere Guardians, fehlende/abgelaufene/widerrufene Zustimmung: wirksamen Zustand getrennt von Auswahl zeigen, sensible Verarbeitung sperren. |
| Kalender | Tag/Woche, parallele Termine, Entfall, lange Namen, Nulltreffer/veraltete Quelle: lesbar und vollständig. |
| Formular/Netz | Validierung, CSRF/403/500, Offline, Latenz/Doppelklick: Eingaben erhalten, kein falscher Erfolg/unzulässiger Retry. |
| Abwesenheit | Nicht gesendet/unklar/bestätigt/gleiches Token: Einmalschutz, Ladehinweis ohne JS-Ausnahme, unklar bleibt unklar. |
| Avatar | Kategorien/Ränder/Zufall/Abbruch/Speichern/Seed/Assetfehler: Abschnitt 8.4. |
| Galerie | Schuljahr/Ereignis/Metadaten, Filter, Freigabe/Widerruf, Detailansicht, KI-Status, leere Zustände und Download-Gate nach Abschnitt 9. |
| Vision-Betrieb | Schnelles und erweitertes Modell pro Klasse getrennt schalten; Deaktivierung stoppt neue Jobs; Vorschläge bleiben unbestätigt, Referenzen/Audit/Widerruf funktionieren. |
| Reflow/A11y | Viewports, 200 % Text, 320 px Reflow, Tastatur/Touch/Screenreader, Reduced Motion/Forced Colors/Themekontraste. |
| PWA/Sitzung | Offline/Idle-Logout/Polling/Zurück nach Logout: neutraler Offlinezustand, kein privater Dauercache, konsistenter Ablauf. |

Bestehende Django-Tests gezielt erweitern, dann betroffene Modul-/Integrationssuiten. UI-Checks prüfen geroutete echte Templates; ein CSS-Stringtest beweist keinen mobilen Ablauf. Keine implementierungsgleichen Scheintests. **Dieses Audit bescheinigt keine bestandenen Regressionen oder Produktionsfreigabe.**

## 14. Offene Entscheidungen

1. Adapterpflege ausschließlich global oder schul-/klassenweise delegiert? Grundlage für A-01.
2. Gemeinsames Datenlesen aus Guardian-Zugang oder strikt eigene Verbindung? Opt-in, Zugang, Einwilligung konsistent halten.
3. Mehrschul-Instanzmodell/Migration bestehender WebUntis-Daten und Mappingcodes.
4. Linke Desktopnavigation bestätigen; rechte Zusatzspalte nur nach Bedarf. Home/Start und Menü/Mehr vereinheitlichen.
5. Familienübersicht versus konkrete Kindwahl bei Mehrdeutigkeit und festen Objekten.
6. Eltern dürfen Aufgaben lokal abhaken? Aktueller Code erlaubt es für sichtbare Aufgaben; DOCX fordert restriktiveren Zustand, ist keine Policy.
7. Kuratierter Avatarumfang/weitere Posen erst nach Geometrie/Herkunft; zweistufig übernehmen/speichern oder direkt speichern.
8. Theme-/Schriftgrößenumfang; zusätzliche Themes, Schriftregler und Animationen optional.
9. Isolierte Umgebung und Zeitpunkt für tatsächliches Browser-/Gerätegate ohne Dashboard-Seiteneffekte.
10. Soll die interne Klassenfotogalerie durch eine klassenweite Grundfreigabe statt personengenauer Freigaben geregelt werden? Dafür Datenmodell, Widerruf und Bestandsdaten ausdrücklich entscheiden.
11. Welche Rollen dürfen Ereignisse anlegen, Bilder hochladen und Personen manuell zuordnen?
12. Unter welchen Bedingungen werden Bilddownloads freigegeben und welche Auditdaten gelten als ausreichend?
13. Welche Kriterien entscheiden, wann das erweiterte Modell aus dem Präsentationsmodus in den regulären Betrieb wechselt?
14. Welche Kategorien, Schwellen, Aufbewahrungsfristen und Eskalationswege gelten für Chat-Hinweise, und welche Rolle darf sie sehen/entscheiden?

## Anhang A: Vollständiges Routeninventar

Aus `app/src/klasse5e/urls.py` gelesen. Parameter sind Schemaplatzhalter; keine produktiven IDs/Tokens. Handlerzuordnung ist kein geprüfter HTTP-Methodenvertrag; Includes enthalten weitere Bibliotheksrouten.

Insgesamt 156 explizite Projektrouten.

| Route | Handler | Name |
|---|---|---|
| `/abwesenheiten/` | `absence_portal` | `absence-portal` |
| `/registrieren/` | `views.register` | `register` |
| `/einladung/` | `views.invitation_entry` | `invitation-entry` |
| `/familie/start/<str:token>/` | `views.family_register` | `family-register` |
| `/registrieren/email/<str:token>/` | `views.verify_registration_email` | `registration-email-verify` |
| `/aktivieren/<str:token>/` | `views.activate_registration` | `registration-activate` |
| `/datenschutz/` | `TemplateView.as_view(template_name='privacy/information_v2.html')` | `privacy-information` |
| `/projekt/` | `TemplateView.as_view(template_name='core/project.html')` | `project` |
| `/demo/` | `TemplateView.as_view(template_name='core/demo.html')` | `demo` |
| `/scan/<path:token>/` | `views.temporary_scan_access` | `temporary-scan-access` |
| `/onboarding/` | `onboarding_experience_views.onboarding_step` | `onboarding-resume` |
| `/onboarding/pausiert/` | `onboarding_experience_views.onboarding_paused` | `onboarding-paused` |
| `/onboarding/schritt/<int:step>/` | `onboarding_experience_views.onboarding_step` | `onboarding-step` |
| `/einwilligungen/<slug:key>/<int:subject_id>/widerrufen/` | `onboarding_views.consent_withdraw` | `consent-withdraw` |
| `/tutorial/` | `onboarding_experience_views.tutorial_step` | `tutorial-resume` |
| `/tutorial/schritt/<int:step>/` | `onboarding_experience_views.tutorial_step` | `tutorial-step` |
| `/` | `ui_views.dashboard` | `dashboard` |
| `/familie/ansicht/` | `ui_views.select_active_child` | `family-overview-select` |
| `/familie/ansicht/<int:student_id>/` | `ui_views.select_active_child` | `family-child-select` |
| `/hausaufgaben/<int:homework_id>/erledigt/` | `ui_views.homework_progress` | `homework-progress` |
| `/einstellungen/profil/` | `views.personal_profile` | `personal-profile` |
| `/einstellungen/design/` | `ui_views.theme_settings` | `theme-settings` |
| `/einstellungen/design/vorschau/<int:theme_id>/<slug:page>/` | `ui_views.portal_theme_preview` | `portal-theme-preview` |
| `/einstellungen/konto-loeschen/` | `views.delete_account` | `delete-account` |
| `/praesentation/` | `ui_views.presentation` | `presentation` |
| `/profile/<int:person_id>/foto/` | `views.profile_photo` | `profile-photo` |
| `/familie/foto/<int:photo_id>/` | `views.family_photo` | `family-photo` |
| `/benachrichtigungen/` | `views.notification_list` | `notification-list` |
| `/benachrichtigungen/<int:notification_id>/lesen/` | `views.notification_read` | `notification-read` |
| `/benachrichtigungen/alle-lesen/` | `views.notifications_read_all` | `notifications-read-all` |
| `/kalender/` | `ui_views.calendar` | `ui-calendar` |
| `/kontakte/` | `ui_views.contacts` | `ui-contacts` |
| `/schueler/` | `ui_views.students` | `ui-students` |
| `/chat/` | `ui_views.chat_overview` | `ui-chat` |
| `/chat/direkt/<int:person_id>/starten/` | `ui_views.start_direct_conversation` | `direct-conversation-start` |
| `/chat/<uuid:room_id>/ansicht/` | `ui_views.chat_room` | `ui-chat-room` |
| `/chat/nachricht/<uuid:message_id>/anhang/` | `ui_views.chat_attachment` | `ui-chat-attachment` |
| `/verwaltung/rollen/` | `role_views.role_management` | `role-management` |
| `/verwaltung/` | `ui_views.portal_management` | `portal-management` |
| `/verwaltung/automatische-abmeldung/` | `ui_views.session_timeout_settings` | `session-timeout-settings` |
| `/verwaltung/schulen/` | `ui_views.school_management` | `school-management` |
| `/verwaltung/schulen/<int:school_id>/` | `ui_views.school_detail` | `school-detail` |
| `/verwaltung/schulen/import/` | `ui_views.school_catalog_import` | `school-catalog-import` |
| `/verwaltung/adapter/` | `ui_views.portal_adapter_management` | `portal-adapter-management` |
| `/verwaltung/adapter/<int:adapter_id>/` | `ui_views.portal_adapter_detail` | `portal-adapter-detail` |
| `/verwaltung/anmeldung/` | `ui_views.registration_invitation` | `registration-invitation` |
| `/verwaltung/familien-einladungen/` | `ui_views.family_invitations` | `family-invitations` |
| `/verwaltung/themes/` | `ui_views.theme_management` | `theme-management` |
| `/verwaltung/themes/vorschau/<slug:template_key>/<slug:page>/` | `ui_views.template_preview` | `template-preview` |
| `/verwaltung/menue/` | `ui_views.menu_management` | `menu-management` |
| `/verwaltung/terminumfrage/` | `ui_views.presentation_poll_settings` | `presentation-poll-settings` |
| `/verwaltung/chat-aufbewahrung/` | `ui_views.chat_retention_settings` | `chat-retention-settings` |
| `/verwaltung/anmeldung/qr.svg` | `ui_views.registration_invitation_qr` | `registration-invitation-qr` |
| `/pilot/melden/` | `ui_views.pilot_report` | `pilot-report` |
| `/mehr/` | `ui_views.more` | `ui-more` |
| `/mehr/lernportale/` | `ui_views.learning_portals` | `ui-learning-portals` |
| `/mehr/dokumente/` | `ui_views.documents` | `ui-documents` |
| `/mehr/aktuelles/` | `ui_views.posts` | `ui-posts` |
| `/mehr/aktuelles/<int:post_id>/` | `ui_views.post_detail` | `ui-post-detail` |
| `/mehr/veranstaltungen/` | `ui_views.events` | `ui-events` |
| `/mehr/veranstaltungen/umfrage/neu/` | `ui_views.create_event_poll` | `ui-create-event-poll` |
| `/mehr/veranstaltungen/umfrage/<int:poll_id>/` | `ui_views.event_poll` | `ui-event-poll` |
| `/mehr/veranstaltungen/umfrage/<int:poll_id>/festlegen/` | `ui_views.finalize_event_poll` | `ui-finalize-event-poll` |
| `/mehr/mobilitaet/` | `mobility_views.overview` | `mobility-overview` |
| `/mehr/mobilitaet/<uuid:public_id>/` | `mobility_views.detail` | `mobility-detail` |
| `/mehr/mobilitaet/<uuid:public_id>/treffpunkt/` | `mobility_views.add_meeting_point` | `mobility-meeting-point` |
| `/mehr/mobilitaet/<uuid:public_id>/reagieren/` | `mobility_views.react` | `mobility-react` |
| `/mehr/mobilitaet/<uuid:public_id>/status/` | `mobility_views.change_status` | `mobility-status` |
| `/mehr/mobilitaet/<uuid:public_id>/melden/` | `mobility_views.report` | `mobility-report` |
| `/mehr/mobilitaet/<uuid:public_id>/moderieren/` | `mobility_views.moderate` | `mobility-moderate` |
| `/mobility/reactions/<int:reaction_id>/decision/` | `mobility_views.reaction_decision` | `mobility-reaction-decision` |
| `/mobility/reactions/<int:reaction_id>/pickup/` | `mobility_views.disclose_pickup` | `mobility-pickup-disclose` |
| `/mobility/pickups/<int:disclosure_id>/revoke/` | `mobility_views.revoke_disclosure` | `mobility-pickup-revoke` |
| `/mehr/veranstaltungen/<int:event_id>/` | `ui_views.event` | `ui-event` |
| `/mehr/veranstaltungen/<int:event_id>/bearbeiten/` | `ui_views.edit_event` | `ui-edit-event` |
| `/mehr/veranstaltungen/<int:event_id>/loeschen/` | `ui_views.delete_event` | `ui-delete-event` |
| `/mehr/veranstaltungen/<int:event_id>/teilnahme/` | `ui_views.set_event_attendance` | `ui-event-attendance` |
| `/mehr/veranstaltungen/<int:event_id>/mitbringliste/` | `ui_views.add_contribution_list` | `ui-add-contribution-list` |
| `/mehr/mitbringen/<int:item_id>/reservieren/` | `ui_views.reserve` | `ui-reserve` |
| `/mehr/veranstaltungen/<int:event_id>/freier-beitrag/` | `ui_views.free_contribution` | `ui-free-contribution` |
| `/mehr/reservierungen/<int:reservation_id>/zuruecknehmen/` | `ui_views.cancel_reservation` | `ui-cancel-reservation` |
| `/mehr/lehrkraefte/` | `ui_views.teachers` | `ui-teachers` |
| `/mehr/fotos/` | `ui_views.galleries` | `ui-galleries` |
| `/mehr/speiseplan/` | `meal_views.meal_plans` | `meal-plans` |
| `/mehr/familie/` | `ui_views.family` | `ui-family` |
| `/mehr/einwilligungen/` | `ui_views.consents` | `ui-consents` |
| `/mehr/benachrichtigungen/` | `ui_views.notifications` | `ui-notifications` |
| `/mehr/benachrichtigungen/einstellung/` | `ui_views.notification_preference` | `ui-notification-preference` |
| `/mehr/webuntis/` | `webuntis_views.connection` | `webuntis-connection` |
| `/mehr/webuntis/synchronisierung/` | `webuntis_views.toggle_sync` | `webuntis-toggle-sync` |
| `/mehr/webuntis/testen/` | `webuntis_views.test_connection` | `webuntis-test` |
| `/mehr/webuntis/entfernen/` | `webuntis_views.remove_connection` | `webuntis-remove` |
| `/mehr/webuntis/funktionen/` | `webuntis_views.update_features` | `webuntis-features` |
| `/mehr/webuntis/aktuell-pruefen/` | `webuntis_views.sync_now` | `webuntis-sync` |
| `/kalender/verbinden/` | `webuntis_views.calendar_settings` | `webuntis-calendar-settings` |
| `/mehr/webuntis/<int:connection_id>/kalender.ics` | `webuntis_views.download_calendar` | `webuntis-calendar-download` |
| `/mehr/webuntis/<int:connection_id>/kalender-abo/` | `webuntis_views.issue_calendar` | `webuntis-calendar-issue` |
| `/webuntis/kalender/<str:token>/` | `webuntis_views.calendar_feed` | `webuntis-calendar-feed` |
| `/itslearning/` | `itslearning_views.portal` | `itslearning-portal` |
| `/itslearning/zugang/` | `itslearning_views.save_connection` | `itslearning-save` |
| `/itslearning/<int:student_id>/kurse/` | `itslearning_views.add_course` | `itslearning-course` |
| `/itslearning/<int:student_id>/synchronisieren/` | `itslearning_views.sync_now` | `itslearning-sync` |
| `/itslearning/speicher/` | `itslearning_views.storage` | `itslearning-storage` |
| `/itslearning/speicher/einrichten/` | `itslearning_views.save_storage` | `itslearning-storage-save` |
| `/dav/<uuid:public_id>/` | `webdav` | `webdav-root` |
| `/dav/<uuid:public_id>/<path:resource>` | `webdav` | `webdav-resource` |
| `/mehr/ui-zustaende/` | `ui_views.demo_states` | `ui-demo-states` |
| `/mehr/systemstatus/` | `ui_views.system_status` | `ui-system-status` |
| `/health/` | `views.health` | `health` |
| `/admin/` | `admin.site.urls` | `include` |
| `/cms/` | `include(wagtailadmin_urls)` | `include` |
| `/accounts/` | `include('allauth.urls')` | `include` |
| `/invitation/<str:token>/` | `views.accept_invitation` | `accept-invitation` |
| `/sessions/revoke-all/` | `views.revoke_all_sessions` | `revoke-all-sessions` |
| `/sessions/idle-timeout/` | `views.end_idle_session` | `idle-session-timeout` |
| `/push/subscriptions/` | `views.push_subscriptions` | `push-subscriptions` |
| `/push/configuration/` | `views.push_configuration` | `push-configuration` |
| `/push/self-test/` | `views.push_self_test` | `push-self-test` |
| `/manifest.webmanifest` | `views.manifest` | `manifest` |
| `/service-worker.js` | `views.service_worker` | `service-worker` |
| `/offline/` | `views.offline` | `offline` |
| `/documents/<int:document_id>/<str:variant>/` | `content_views.document_download` | `document-download` |
| `/posts/<int:post_id>/comments/` | `content_views.create_comment` | `create-comment` |
| `/comments/<int:comment_id>/withdraw/` | `content_views.withdraw_comment` | `withdraw-comment` |
| `/comments/<int:comment_id>/moderate/` | `content_views.moderate_comment` | `moderate-comment` |
| `/events/<int:event_id>/` | `event_views.event_detail` | `event-detail` |
| `/events/<int:event_id>/recipes/<int:recipe_id>/import/` | `event_views.import_recipe` | `event-recipe-import` |
| `/impressum/` | `TemplateView.as_view(template_name='legal/imprint.html')` | `imprint` |
| `/open-source-lizenzen/` | `TemplateView.as_view(template_name='legal/open_source_licenses.html')` | `open-source-licenses` |
| `/nutzung/` | `TemplateView.as_view(template_name='legal/terms.html')` | `terms` |
| `/mehr/reservierungen/<int:reservation_id>/erledigt/` | `ui_views.fulfill_reservation` | `ui-fulfill-reservation` |
| `/events/<int:event_id>/food/<str:source_id>/import/` | `event_views.import_food_item` | `event-food-import` |
| `/items/<int:item_id>/reserve/` | `event_views.reserve_item` | `reserve-item` |
| `/reservations/<int:reservation_id>/cancel/` | `event_views.cancel_reservation` | `cancel-reservation` |
| `/galleries/<int:gallery_id>/` | `media_views.gallery_detail` | `gallery-detail` |
| `/galleries/<int:gallery_id>/upload/` | `media_views.upload_photos` | `gallery-upload` |
| `/photos/<uuid:photo_id>/kind-zuweisen/` | `media_views.assign_child` | `photo-assign-child` |
| `/photos/<uuid:photo_id>/kind/<int:person_id>/entfernen/` | `media_views.remove_child_assignment` | `photo-remove-child` |
| `/photos/<uuid:photo_id>/moderate/` | `media_views.moderate_photo` | `photo-moderate` |
| `/photos/<uuid:photo_id>/report/` | `media_views.report_photo` | `photo-report` |
| `/photos/<uuid:photo_id>/withdraw/` | `media_views.withdraw_photo` | `photo-withdraw` |
| `/photos/<uuid:photo_id>/<str:variant>/` | `media_views.photo_file` | `photo-file` |
| `/biometrics/` | `biometric_views.search_home` | `biometric-search` |
| `/biometrics/moderation/` | `biometric_views.moderation_queue` | `biometric-moderation` |
| `/biometrics/profiles/<int:student_id>/enable/<int:class_id>/` | `biometric_views.enable_biometric_profile` | `biometric-profile-enable` |
| `/biometrics/profiles/<uuid:public_id>/withdraw/` | `biometric_views.withdraw_biometric_profile` | `biometric-profile-withdraw` |
| `/biometrics/photos/<uuid:photo_id>/analyze/` | `biometric_views.analyze_photo` | `biometric-photo-analyze` |
| `/biometrics/matches/<uuid:public_id>/<str:decision>/` | `biometric_views.decide_match` | `biometric-decision` |
| `/chat/rooms/<uuid:room_id>/` | `chat_views.room_detail` | `chat-room` |
| `/chat/rooms/<uuid:room_id>/messages/` | `chat_views.messages` | `chat-messages` |
| `/chat/messages/<uuid:message_id>/` | `chat_views.edit_or_delete_message` | `chat-message` |
| `/chat/messages/<uuid:message_id>/report/` | `chat_views.report_message` | `chat-report` |
| `/chat/messages/<uuid:message_id>/moderate/` | `chat_views.moderate_message` | `chat-moderate` |
| `/schedule/classes/<int:class_id>/week/` | `schedule_views.week` | `schedule-week` |
| `/schedule/ical/<str:token>/` | `schedule_views.ical_feed` | `schedule-ical` |
| `/schedule/classes/<int:class_id>/ical-token/` | `schedule_views.issue_ical` | `schedule-ical-issue` |
