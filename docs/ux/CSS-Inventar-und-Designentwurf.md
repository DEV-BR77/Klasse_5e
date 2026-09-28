# CSS-Inventar und Designentwurf

Stand: 13.09.2026  
Zweck: Arbeitsgrundlage für die gemeinsame Neugestaltung. Dieses Dokument
beschreibt den Ist-Zustand und einen Vorschlag. Es ist noch keine Freigabe für
eine CSS- oder Template-Änderung.

## 1. Ergebnis der Bestandsaufnahme

Das Portal verwendet derzeit technisch eine zentrale Browser-Datei:

```text
base.html / allauth base
        └── css/dist/styles.css
             ├── Tailwind v4
             ├── app.css
             ├── auth.css
             ├── enhancements.css
             ├── mentions.css
             ├── onboarding.css
             ├── onboarding-v2.css
             ├── itslearning.css
             └── theme-previews.css
```

Das ist zwar ein zentraler Auslieferungspunkt, aber noch kein zentrales
Design-System. `styles.css` ist momentan eine Bridge und importiert die alten
Dateien weiterhin. Zusätzlich verwenden viele Templates Tailwind-Utilityklassen
direkt neben semantischen Klassen und teilweise älteren Komponentenklassen.

## 2. CSS-Quellen

| Datei | Rolle heute | Umfang ungefähr | Bewertung |
|---|---|---:|---|
| `app/theme/static_src/src/styles.css` | Tailwind-Einstieg, Imports und neue semantische Regeln | ca. 2.500 Zeilen | zukünftiger Einstiegspunkt, momentan noch Bridge |
| `app/theme/static_src/src/settings.css` | nachgeladene Regeln für Settings/Formulare | ca. 50 Zeilen | sinnvoller Komponentenbereich, muss in das System integriert werden |
| `app/static/app.css` | größter globaler Alt-/Basisbestand, teils minifiziert | ca. 102 KB | Hauptquelle für globale Seiteneffekte |
| `app/static/enhancements.css` | spätere Ergänzungen und Übersteuerungen | ca. 28 KB | viele Nachbesserungen; auf Komponenten verteilen |
| `app/static/auth.css` | Login- und Authentifizierungsdarstellung | ca. 6 KB | später in Auth-Komponenten überführen |
| `app/static/theme-previews.css` | Theme-Vorschaukarten | ca. 15 KB | separat prüfbar, aber Tokens müssen zentral sein |
| `app/static/onboarding.css` | älteres Onboarding | ca. 2 KB | mit `onboarding-v2.css` vergleichen und zusammenführen |
| `app/static/onboarding-v2.css` | neues Onboarding | ca. 6 KB | Kandidat für neue Flow-Komponenten |
| `app/static/itslearning.css` | kleines Modul-Fragment | ca. 0,4 KB | fachlich separat, visuell an Komponenten anbinden |
| `app/static/mentions.css` | Mention-Fragment für Chat | ca. 0,5 KB | in Chat-Komponenten überführen |
| `app/static/vendor/leaflet/leaflet.css` | Drittanbieter-Kartenbibliothek | extern | bleibt isoliert und darf globale Portalregeln nicht beeinflussen |
| `app/static/app.js` | kein CSS, aber relevant für sichtbares Verhalten | — | Passwortfeld, Dialoge, Navigation und Interaktionen mitprüfen |

Wichtig: Die Größen sind Dateigrößen bzw. grobe Quellumfänge, keine Aussage
über die tatsächliche Nutzung. Eine Regel gilt heute bereits dann global,
wenn sie importiert wird; ungenutzte Regeln werden nicht zuverlässig erkannt.

### Erste Wirkungsprüfung

Die vollständige Prüfung muss vor der ersten Seitenmigration erfolgen. Der
aktuelle Bestand bestätigt bereits:

- rund 109 HTML-Templates unter `app/templates`;
- eine zentrale Browser-Datei `css/dist/styles.css` für die Portal-Shell;
- `styles.css` importiert weiterhin `app.css`, `auth.css`,
  `enhancements.css`, `mentions.css`, `onboarding.css`, `onboarding-v2.css`,
  `itslearning.css` und `theme-previews.css`;
- `settings.css` wird zusätzlich am Ende des Tailwind-Einstiegspunkts
  eingebunden;
- dadurch erhalten die meisten Portal- und Auth-Seiten denselben globalen
  CSS-Bestand, auch wenn sie fachlich nur einen kleinen Teil davon benötigen;
- Django-Admin, Wagtail-Admin und die isolierte Modellvisualisierung werden
  als eigene Oberflächen getrennt bewertet.

Das bedeutet: Wir prüfen nicht nur die Login-Seite, sondern erstellen zunächst
eine Wirkungs-Matrix `Template → CSS-Quelle → Selektor/Komponente →
Konflikt/Entscheidung`. Erst danach werden alte Regeln zentral migriert oder
entfernt. So wird die globale Bereinigung nicht durch neue seitenbezogene
Ausnahmen ersetzt.

### Abgleich der Altregeln mit der zentralen Verwaltung

Die Altregeln werden zunächst nur zugeordnet. Eine Zuordnung ist noch keine
Freigabe zur Entfernung oder zur technischen Änderung. Die spätere Freigabe
erfolgt je Regelgruppe nach fachlicher Prüfung.

| Altbestand | Aktuelle Wirkung | Ziel in der zentralen Verwaltung | Erste Einstufung |
|---|---|---|---|
| `--color-primary`, `--color-primary-dark`, `--color-primary-light` in `app.css` und `settings.css` | mehrere Primärfarbvarianten | `Themes → Farben` mit `brand`, `brand-strong`, `brand-soft` | zusammenführen |
| `--color-accent`, `--color-accent-soft` | zusätzliche Akzentfarben | `Themes → Farben` mit benanntem Akzent-Token | fachlich prüfen |
| `--color-success`, `--color-warning`, `--color-error` samt Soft-Varianten | Zustandsfarben | `Themes → Farben` und `Globale Komponenten → Statusanzeigen` | behalten, zentralisieren |
| `--gradient-brand` und feste Gradients in `auth.css` | visuelle Button- und Login-Verläufe | `Globale Komponenten → Buttons` bzw. Theme-Token | ersetzen durch Token |
| `--radius`, `--shadow-card`, `--space-*` | globale Größen, aber mit uneinheitlicher Benennung | `Themes → Abstände & Größen` sowie `Form & Tiefe` | umbenennen/vereinheitlichen |
| `--tp-*` in `theme-previews.css` | eigene Vorschau-Tokenfamilie | dieselben Theme-Tokens wie im Portal | nicht parallel behalten |
| `.auth-card form button` in `auth.css` | alle Auth-Buttons volle Breite, 48 px hoch | `Globale Komponenten → Buttons`, Variante `primary` | Regel aufteilen; Auge ausnehmen |
| `.password-toggle` in `styles.css` und Passwort-DOM aus `app.js` | kleines Icon im Passwortfeld | `Globale Komponenten → Formularfelder → Passwort` und `Icon-Katalog` | behalten, global normieren |
| `.status-banner` in `auth.css` | eigene Erfolgs-/Statuskachel mit Gradient | `Globale Komponenten → Meldungen/Statusanzeigen` | in Standardkomponente überführen |
| `.auth-card`, `.settings-panel`, `.welcome-card`, `.portal-module-card` | mehrere kartenähnliche Oberflächen | `Globale Komponenten → Karten` mit Varianten | Varianten definieren, nicht einzeln stylen |
| `.app-icon-button`, `.dashboard-refresh-button.icon-button` | eigene Icon-Button-Regeln | `Globale Komponenten → Buttons` und `Icon-Katalog` | zusammenführen |
| `.chat-room--classic/modern/math` | modulbezogene Raumfarben und Schatten | `Chat → Chat-Style` mit freigegebenen Style-Tokens | fachlich behalten, technisch tokenisieren |
| `.calendar-page *`, `.chat-room-page *`, `.family-*` | seitenbezogene Layout- und Button-Ausnahmen | globale Layout-/Komponentenregeln plus Modulkonfiguration | nur Struktur behalten; visuelle Duplikate prüfen |
| verstreute `@media`-Blöcke | eigene Breakpoints und mobile Sonderfälle | `Themes → Layout & Responsive` | Breakpoints vereinheitlichen |
| `onboarding.css`, `onboarding-v2.css`, Legacy/V2-Regeln | parallele Darstellungen | eine globale Komponentenbasis, eine freigegebene Variante | Duplikatprüfung |

Die vollständige Matrix wird im nächsten Prüfschritt aus allen Selektoren und
Variablen der eingebundenen Quelldateien erweitert. Für jede Regel werden dann
zusätzlich betroffene Templates, Sichtbarkeit im Browser, Priorität und die
fachliche Entscheidung dokumentiert. Erst Regeln mit der Einstufung
„behalten“ oder „ersetzen“ werden in die neue zentrale Verwaltung übernommen;
„entfernen“ bleibt bis zur bestätigten Migration liegen.

### Noch nicht eindeutig zentral definierte Tokens

Die Grundfarben, Hell-/Dunkelmodus, Statusfarben, Typografie, Abstände, Radien,
Schatten und Fokusdarstellung sind bereits als zentrale Bereiche vorgesehen.
Aus dem ersten Altregel-Abgleich bleiben folgende Kandidaten zur Entscheidung:

| Kandidat | Warum er auftaucht | Empfehlung |
|---|---|---|
| `accent` und `accent-soft` | bisherige Akzentfamilie in `app.css` | als zentrale Akzenttokens behalten |
| `on-primary` | Text/Icon auf Markenflächen | zentral behalten |
| `silver` und `silver-light` | alte neutrale Sonderfarben | nicht als eigene Farbe fortführen; auf `muted`/`border` abbilden |
| `hover`, `pressed`, `selected` | Zustände sind bisher häufig direkt in Selektoren berechnet | als Interaktionszustände zentral definieren |
| `disabled-surface`, `disabled-text`, `disabled-border` | für deaktivierte Buttons und Felder fehlt eine klare semantische Gruppe | als Formular-/Button-Zustände ergänzen |
| `input-surface`, `input-border`, `placeholder` | Eingabefelder verwenden bislang teilweise allgemeine Surface-/Border-Werte | als Formularfeld-Tokens ergänzen |
| `focus-ring` und `focus-ring-offset` | Fokus ist beschrieben, aber noch nicht als vollständig benannte Tokenfamilie | als zentrale Interaktionstokens ergänzen |
| `scrim`/`overlay` | Dialoge, Vorschauen und Hintergrundbilder benötigen eine Abdunklung | als Dialog-/Hintergrund-Token ergänzen |
| `success-soft`, `warning-soft`, `danger-soft`, `info-soft` | weiche Statusflächen werden bereits verwendet | als Status-Tokens behalten und vereinheitlichen |
| `brand-gradient` | alte Login-/Button-Gradients | zunächst entfernen; nur bei bestätigtem Bedarf als optionales Theme-Token behalten |
| `chat-style-*` | Chat-Räume besitzen eigene Erscheinungsvarianten | nicht globalisieren; unter `Chat → Chat-Style` führen |

Damit ist die erste Entscheidungsliste für die Farben abgeschlossen: Es fehlen
keine grundlegenden Farben, sondern vor allem semantische Zustands- und
Komponententokens. Diese Liste wird jetzt Punkt für Punkt mit „anlegen“,
„bestehenden Token verwenden“ oder „nicht übernehmen“ entschieden.

## 3. Aktuelle globale Risiken

1. **Globale Button-Regeln:** Ein Button wird abhängig vom Kontext teilweise
   automatisch auf volle Breite gesetzt. Dadurch wurden Icon-Buttons wie das
   Passwort-Auge oder Löschaktionen zu großen Flächen.
2. **Doppelte Zuständigkeiten:** `app.css`, `enhancements.css` und
   `settings.css` definieren teilweise dieselben visuellen Bereiche.
3. **Semantische Klassen und Utilityklassen gemischt:** Ein Template kann
   gleichzeitig `.button`, `.card`, `.settings-panel` und viele Tailwind-
   Utilities verwenden. Die Priorität ist dadurch schwer vorherzusagen.
4. **Neue und alte Navigation parallel:** `base.html`, `Navigation.html` und
   weitere Navigationsfragmente gehören nicht zu einem einzigen verbindlichen
   Navigationskomponentenmodell.
5. **Themes sind nicht vollständig tokenisiert:** Einige Regeln verwenden
   Variablen, andere feste Farben wie `#0756b9`, `#b42318` oder `#fff`.
6. **Responsive Regeln liegen verteilt:** Mobile Anpassungen befinden sich in
   mehreren Dateien und teilweise direkt im jeweiligen Modulbereich.
7. **Legacy- und V2-Templates parallel:** Unter anderem existieren
   `dashboard.html` und `dashboard_v2.html`, `calendar.html` und
   `calendar_v2.html` sowie mehrere Onboardingvarianten.
8. **CSS und Verhalten sind gekoppelt:** JavaScript erzeugt für Passwortfelder
   nachträglich Wrapper und Buttons. Solche DOM-Ergänzungen müssen Bestandteil
   einer definierten Komponente werden.

## 4. Seiten- und Funktionsinventar

Die folgende Matrix benennt die aktuell vorhandenen Seitenvorlagen und die
visuellen Bausteine, die bei der Neugestaltung jeweils geprüft werden müssen.
Sie ist die Arbeitsliste für die spätere Abnahme.

### A. Einstieg, Login und Kontozugriff

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `account/login.html` | `auth-card`, Formular, Passwortfeld, Auge, Primärbutton, Links | Eingabefeld, Passwort-Wrapper, Buttonbreite, Fehlermeldung |
| `account/password_reset_from_key.html` | `auth-card`, `form-stack`, `password-control`, `password-rules` | vertikaler Formularfluss, Regelkachel, Fokus, Auge |
| `account/password_reset_from_key_done.html` | Erfolgsbanner, Weiterleitung | Statusmeldung, Fade-out, Login-Ziel |
| `core/register.html` | `registration-page`, `registration-form`, `field-pair`, Passwortregeln | Desktop/Mobil-Aufteilung, Formularfelder, Button |
| `core/family_register.html` | Familienregistrierung, Personenfelder | Card-Struktur, Fehlerzustände, Touch-Ziele |
| `core/accept_invitation.html` | `access-flow`, Passwortfeld, Aktivierungsbutton | Einladungsfluss, Status und Fokus |
| `core/invitation_entry.html` | Codeeingabe | kompakte Eingabe, Fehler- und Erfolgszustände |
| `core/registration_received.html` | Bestätigungszustand | Statusseite, Handlungsoptionen |
| `core/registration_verified.html` | Verifizierungszustand | Statusseite, nächster Schritt |
| `core/registration_activated.html` | Aktivierungszustand | Statusseite, Login/Weiterleitung |
| `core/family_registration_received.html` | Familienantrag bestätigt | Statusseite |
| `core/invitation_invalid.html` | ungültige Einladung | Fehlerseite |
| `core/family_invitation_invalid.html` | ungültige Familienfreigabe | Fehlerseite |

### B. App-Rahmen und Navigation

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `base.html` | Topbar, Familienumschalter, Seiteninhalt, Bottom-Navigation | globaler Shell, Ebenen, mobile Positionierung |
| `allauth/layouts/base.html` | Auth-Shell | getrennte Auth-/App-Grundstruktur |
| `allauth/layouts/entrance.html` | Auth-Einstieg | Login-/Reset-Rahmen |
| `allauth/layouts/manage.html` | Konto-Verwaltung | Kontoaktionen |
| `Navigation.html` | experimenteller Navigationsentwurf | nicht als verbindliche Implementierung behandeln; separat bewerten |
| `ui/_settings_navigation.html` | Einstellungsnavigation | Tabs, mobile Überlaufstrategie |
| `ui/more.html` | Mehr-Menü und Module | Gruppierung, Beta-Bereich, Karten |
| `ui/menu_management.html` | Menüverwaltung | Admin-Listen, Reihenfolge, Status |

### C. Startseite und Übersicht

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `core/dashboard.html` | ältere Übersicht | Bestand, Abhängigkeiten, Ablösung prüfen |
| `core/dashboard_v2.html` | neue Übersicht | Hero, Tagesansicht, Tabs, Statuskacheln |
| `ui/dashboard.html` | UI-Übersicht | Dashboardkarten, Hausaufgaben, Stundenplan, Aktuelles |
| `ui/dashboard_v2.html` | UI-V2-Übersicht | gleiche Fachlichkeit mit neuer Struktur vergleichen |
| `core/offline.html` | Offline-Zustand | reduzierte Statusseite |
| `core/demo.html` | Demo-/Vorschauzustand | ausdrücklich von produktiven Seiten trennen |
| `ui/demo_states.html` | Zustandsdemo | nur Referenz, keine globale CSS-Abhängigkeit |

### D. Profil, Familie und Einwilligungen

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `ui/personal_profile.html` | Settings-Tabs, Settings-Panel, Profilbild, Sicherheit, Statuskarten | Tabmodell, Karten, Statusfarben, Formularabstände |
| `ui/personal_profile_data.html` | Profilfelder und optionale Module | Feldgruppen, Sichtbarkeit, keine unerwünschten Module |
| `ui/family.html` | Familienkarten, Kinder, Adapter-/Zugangsbereiche | Card-Hierarchie, Rollen, Formulare |
| `ui/family_overview.html` | Familienübersicht | Kinderauswahl, Status, Karten |
| `ui/family_child_data.html` | Kinddaten | Formulare, Abschnittsnavigation |
| `ui/family_invitations.html` | Einladungen | Listen, Status-Badges, Aktionen |
| `ui/consents.html` | Einwilligungsliste | Tabellen/Karten, Zustände, Widerruf |
| `ui/consents_v2.html` | neue Einwilligungsdarstellung | V2 gegen Bestand vergleichen |
| `ui/_family_person_card.html` | Personenkarte | einheitliche Familienkarte |
| `ui/_account_sections.html` | Kontoabschnitte | alte/neue Sicherheitselemente vergleichen |

### E. Kalender, Stundenplan und Abwesenheiten

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `ui/calendar.html` | ältere Kalenderansicht | Bestand und alte Selektoren prüfen |
| `ui/calendar_v2.html` | Timeline, Filter, Woche/Tag/Monat | responsive Zeitachse, aktive Filter, Touch-Ziele |
| `webuntis/calendar_settings.html` | Adapter-/Kalendereinstellungen | Settings-Formular, Status |
| `webuntis/connection.html` | Verbindungseinstellungen | Zugangsfelder, Passwortfeld, Status |
| `webuntis/connection_v2.html` | neue Verbindungsseite | V2 gegen Bestand prüfen |
| `webuntis/absences.html` | Abwesenheitsstatus und Formular | Datumspicker, Zeitfelder, Warn-/Erfolgszustände |
| `ui/system_status.html` | System-/Adapterstatus | technische Statuskarten |

### F. Chat und Nachrichten

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `ui/chat.html` | Chatübersicht | Raumliste, Neuer Raum, Split-/Stack-Layout |
| `ui/chat_overview.html` | Raumübersicht | Auswahlzustand, leere Zustände |
| `ui/chat_room.html` | Nachrichtenverlauf, Composer | Eingabe, Emoji, Datei, Mikrofon, Senden, Enter/Strg+Enter |
| `ui/chat_retention_settings.html` | Aufbewahrungseinstellungen | Settings-Formular |
| `ui/notification_list.html` | Nachrichten-/Hinweisliste | Unread-Badge, Karten, Aktionen |
| `ui/notifications.html` | Benachrichtigungspräferenzen | Kanäle, Schalter, Tabellen/Karten |

### G. Inhalte und Klassenmodule

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `ui/events.html` | Veranstaltungsübersicht | Karten, Filter, Status |
| `ui/event_detail.html` | Veranstaltungsdetail | Header, Mitbringliste, Aktionen |
| `ui/event_poll.html` | Abstimmung | Auswahlkarten, Ergebniszustände |
| `ui/presentation.html` | Präsentationsansicht | Folien, Navigation, Vollbild |
| `ui/presentation_poll_settings.html` | Präsentationsumfrage | Adminformular |
| `ui/documents.html` | Dokumentencenter | Dokumentkarten, Downloadstatus |
| `ui/posts.html` | Beiträge | Feedkarten, Kommentare |
| `ui/post_detail.html` | Beitragsdetail | Inhalt, Kommentarbereich |
| `ui/teachers.html` | Lehrerliste | Personen-/Kontaktkarten |
| `ui/galleries.html` | Galerieübersicht | Medienraster, Consent-Zustände |
| `media/gallery_detail.html` | Galerie | Medienraster, Dialoge, geschützte Bilder |
| `meals/plans.html` | Speiseplan | Tageskarten, Wochenfilter |
| `meals/_codes.html` | Speiseplanbaustein | kleine Status-/Datenzeilen |
| `meals/_day_options.html` | Tagesauswahl | Filter/Optionen |
| `itslearning/portal.html` | Lernportal | Adapterkarten, externe Links |
| `itslearning/storage.html` | Lernportal-Speicher | Listen, Status |

### H. Verwaltung, Adapter und Betrieb

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `ui/portal_management.html` | Portalverwaltung | Tabellen, Filter, Karten |
| `ui/portal_adapter_management.html` | Adapterkatalog | Suche, Karten, Logo/Icon, Auswahl |
| `ui/portal_adapter_detail.html` | Adapterdetail | Formular, Status, technische Kennung |
| `ui/school_management.html` | Schulen | Verwaltungstabelle, Aktionen |
| `ui/school_detail.html` | Schuldaten | Settings-Panel, Adapterzuweisung |
| `ui/school_setup_import.html` | Schul-/Klassenimport | Datei-Upload, Vorschau, Fehlerliste |
| `ui/school_catalog_import.html` | Katalogimport | Import/Export, Tabellenzustände |
| `ui/role_management.html` | Rollen | Berechtigungslisten, Status |
| `ui/registration_invitation.html` | Einladungsverwaltung | Formular, Code-/Linkstatus |
| `ui/monitoring_dashboard.html` | Monitoring | KPI-Karten, Warnzustände, Speicher/Traffic getrennt |
| `ui/session_timeout_settings.html` | Sitzungsgrenze | Settings-Formular, Warnung |
| `ui/theme_management.html` | Themeverwaltung | Theme-Karten, Vorschau |
| `ui/theme_settings.html` | Theme-Einstellungen | Token-/Farbformulare |
| `ui/system_status.html` | Betriebsstatus | Health-Karten, Fehler-/Normalzustände |
| `admin/core/school/change_list.html` | Django-Admin-Liste | Django-Admin unabhängig vom Portal-CSS prüfen |
| `admin/core/school/import_csv.html` | Django-Admin-Import | Adminformular, Tabelle, Fehler |

### I. Onboarding, Rechtliches und Sonderseiten

| Template | Aktuelle Bausteine / Klassen | CSS-Schwerpunkte |
|---|---|---|
| `onboarding/overview.html` | Onboardingübersicht | Schrittstatus, Fortschritt |
| `onboarding/step.html` | Einzelschritt | Formular, Fortschrittsnavigation |
| `onboarding/experience_step.html` | Erfahrungs-/Einstiegsschritt | Auswahlkarten |
| `onboarding/missing_profile.html` | fehlende Profildaten | Hinweis und Aktion |
| `onboarding/paused.html` | pausiertes Onboarding | Statusseite |
| `onboarding/tutorial.html` | Tutorial alt | mit V2 vergleichen |
| `onboarding/tutorial_v2.html` | Tutorial V2 | Karten, Fortschritt, Navigation |
| `onboarding/_illustration.html` | Illustration | visuell isolieren |
| `privacy/information.html` | Datenschutzhinweise alt | Leseseite |
| `privacy/information_v2.html` | Datenschutzhinweise V2 | Leseseite |
| `legal/imprint.html` | Impressum | Leseseite |
| `legal/terms.html` | Nutzungshinweise | Leseseite |
| `legal/open_source_licenses.html` | Lizenzen | Leseseite |
| `includes/site_footer.html` | Footer | globaler Bestandteil |
| `ui/account_deleted.html` | Löschbestätigung | Statusseite |
| `ui/delete_account.html` | Konto löschen | kritische Aktion, Warnfarbe, Passwortfeld |
| `ui/template_preview.html` | Templatevorschau | nur internes Prüfwerkzeug |

## 5. Aktuell häufig verwendete Bausteine

Die statische Auswertung der Templates zeigt unter anderem:

| Baustein | Vorkommen grob | Problem heute |
|---|---:|---|
| `.button` | 254 | globale Regeln und Kontextbreiten nicht sauber getrennt |
| `.button-secondary` | 124 | mehrere Bedeutungen: sekundär, ruhig, Abbrechen |
| `.button-primary` | 107 | teilweise als Formularbutton, Link und große Aktion verwendet |
| `.form-stack` | 65 | sinnvoll, aber Feld- und Fehlerregeln zentralisieren |
| `.settings-panel` | 64 | gute Grundlage, aber alte Varianten parallel |
| `.content-card` | 44 | mit `.card`, Modul- und Spezialkarten vereinheitlichen |
| `.page-heading` | 43 | Headergrößen und mobile Umbrüche festlegen |
| `.form-actions` | 31 | Buttonbreiten und Reihenfolge definieren |
| `.icon-button` | 19 | explizite Icon-Größen und keine globale Vollbreite erforderlich |
| `.card` / `.card-grid` | 16 | mit Settings-, Modul- und Statuskarten abgleichen |
| `.status` | 16 | als Grundlage für einheitliche Status-Badges geeignet |
| Tailwind-Utilities | sehr häufig | schrittweise durch semantische Komponenten ersetzen |

## 6. Vorschlag für das zentrale Design-System

### Verbindliche Geltungsregel

Das Design-System gilt global für alle Seiten, Module und Zustände. Seiten
definieren ausschließlich fachliche Struktur und Reihenfolge; sie dürfen keine
eigenen Abstände, Kachelfarben, Buttonformen, Rahmen, Schatten oder
Statusfarben erfinden.

Fachliche Unterschiede werden über semantische Varianten und Design-Tokens
abgebildet, nicht über seitenbezogene CSS-Sonderregeln. Beispiele sind
`surface`, `surface-danger`, `status-success` oder `action-primary`. Eine
Ausnahme ist nur zulässig, wenn sie fachlich begründet, als Komponente
dokumentiert und für alle betroffenen Breakpoints gestaltet ist.

Damit gilt für jede Seite:

```text
Seite/Modul
└── globale Shell und Layoutregeln
    └── globale Komponenten
        └── globale Tokens und Themewerte
```

Nicht zulässig sind insbesondere:

- eigene Farbwerte direkt im Seitentemplate;
- individuelle Card-Paddings pro Seite;
- globale Komponenten, die durch Seiten-Selektoren überschrieben werden;
- neue Buttongrößen nur für eine einzelne Funktion;
- parallele „V2“-Komponenten mit gleicher fachlicher Aufgabe.

Die folgenden Tokens sind ein neutraler Startentwurf. Werte werden erst nach
der gemeinsamen Abstimmung verbindlich.

```css
:root {
  /* Farbrollen, keine Seitenfarben */
  --color-brand: ...;
  --color-brand-strong: ...;
  --color-brand-soft: ...;
  --color-accent: ...;
  --color-background: ...;
  --color-surface: ...;
  --color-surface-raised: ...;
  --color-text: ...;
  --color-text-muted: ...;
  --color-border: ...;
  --color-focus: ...;
  --color-success: ...;
  --color-warning: ...;
  --color-danger: ...;

  /* Typografie */
  --font-body: ...;
  --font-heading: ...;
  --text-xs: ...;
  --text-sm: ...;
  --text-md: ...;
  --text-lg: ...;
  --text-xl: ...;
  --text-display: ...;

  /* Rhythmus */
  --space-1: ...;
  --space-2: ...;
  --space-3: ...;
  --space-4: ...;
  --space-5: ...;
  --space-6: ...;
  --space-7: ...;
  --space-8: ...;
  --space-9: ...;
  --space-10: ...;

  /* Globale Größen */
  --content-max-width: ...;
  --control-height-sm: ...;
  --control-height: ...;
  --control-height-lg: ...;
  --icon-size-sm: ...;
  --icon-size: ...;
  --icon-size-lg: ...;

  /* Form und Tiefe */
  --radius-sm: ...;
  --radius-md: ...;
  --radius-lg: ...;
  --radius-pill: 999px;
  --shadow-card: ...;
  --shadow-dialog: ...;

  /* Interaktion */
  --control-height: 48px;
  --control-height-large: 56px;
  --focus-ring: ...;
  --motion-fast: ...;
  --motion-standard: ...;
  --ease-standard: ...;
}
```

### Vorgeschlagene Komponentenstruktur

```text
Design Tokens
├── Layout: shell, container, stack, cluster, grid
├── Navigation: topbar, bottom-nav, section-nav, tabs
├── Actions: button, quiet-button, icon-button, fab
├── Forms: field, field-group, select, textarea, password-field
├── Surfaces: card, panel, dialog, sheet
├── Feedback: badge, notice, toast, empty-state, progress
├── Content: list, person-card, module-card, timeline-entry
└── Media: avatar, image-frame, gallery-tile
```

Grundregel: Eine visuelle Entscheidung wird an einer Komponente definiert,
nicht erneut in jeder Seite. Eine Ausnahme braucht einen fachlichen Grund und
eine eigene Komponentenschnittstelle.

### Administration: globale Komponenten

Neben der `Theme-Verwaltung` wird in der Portalverwaltung ein eigener Bereich
`Globale Komponenten` vorgesehen. Er ist von den Theme-Tokens getrennt:

```text
Portalverwaltung
├── Themes
│   ├── Farben
│   ├── Typografie
│   ├── Abstände & Größen
│   ├── Form & Tiefe
│   └── Interaktion & Bewegung
└── Globale Komponenten
    ├── Buttons
    ├── Formularfelder
    ├── Karten
    ├── Statusanzeigen
    ├── Dialoge
    ├── Meldungen
    ├── Common Header
    ├── Navigation
    └── Icon-Katalog

Portalverwaltung → Chat
└── Reaktionspakete
    ├── Emoji-Pakete
    ├── Sticker-Pakete
    ├── animierte Assets
    └── Reaktionsvorschau
```

Jeder Eintrag ist ein eigener Bearbeitungsreiter mit eigener Vorschau für
Desktop und Smartphone. Die Änderungen werden global an der
Komponentendefinition vorgenommen und nicht an einzelnen Seiten.

Der Reiter `Formularfelder` enthält dabei auch die Untervariante
`Passwortfeld`. Der Reiter `Buttons` enthält normale Buttons, Icon-Buttons und
kritische Aktionen als globale Varianten.

### Globale Komponente: Common Header

Der `Common Header` ist der einheitliche Kopfbereich des Portals. Er wird in
der Verwaltung als eigene Komponente gepflegt und für Desktop und Smartphone
vorgezeigt.

Vorgesehene Bestandteile:

- Zurück- oder Startaktion;
- Seitenkontext und Überschrift;
- optionaler Familien-/Personenkontext;
- globale Aktionen wie Chat, Benachrichtigungen und Profil;
- zugeordnete Icon- und Buttonvarianten;
- responsive Anordnung und Umbruch;
- sichtbarer Fokus und zugängliche Beschriftungen.

Die Verwaltung kann die erlaubten Header-Bausteine, Reihenfolge, Abstände,
Icon-Zuordnungen und Buttonvarianten zentral bearbeiten. Der Header erhält
keine individuellen Seitenfarben oder Sonderabstände. Fachseiten liefern nur
ihren Titel und den fachlichen Kontext.

### Globale Navigationsverwaltung

Der Reiter `Navigation` pflegt nicht nur das Aussehen, sondern auch die
globale Anordnung der Navigationspunkte. Jeder Eintrag erhält mindestens:

| Angabe | Zweck |
|---|---|
| `position_slot` | Zielbereich, zum Beispiel Desktop-Leiste, Bottom-Navigation oder Mehr-Menü |
| `order` | Reihenfolge innerhalb dieses Bereichs: 1, 2, 3 usw. |
| `label` | sichtbare Bezeichnung |
| `icon_key` | Zuordnung zum globalen Icon-Katalog |
| `parent` | übergeordneter Navigationspunkt für Unterebenen |
| `visibility_rule` | Rollen-, Modul- und Kontextprüfung |
| `is_active` | verfügbar oder ausgeblendet |

Die Bearbeitung erfolgt als sortierbare Liste je Positionsbereich. Dadurch
kann beispielsweise ein Punkt Position `bottom-nav`, Reihenfolge `1` haben,
während ein anderer im `more-menu` an Position `2` steht. Die Vorschau zeigt
Desktop und Smartphone mit derselben fachlichen Navigation.

Für das Passwortfeld werden insbesondere vorgesehen:

- Auge rechts innerhalb des Eingabefelds;
- transparente beziehungsweise ruhige Icon-Fläche ohne aufgelegten Button;
- Auswahl eines freigegebenen Icons aus dem zentralen Icon-Katalog;
- Vorschau für verborgenes und sichtbares Passwort;
- Tastaturfokus und zugänglicher Name;
- einheitliche Größe und Position auf Desktop und Smartphone.

Ein Icon kann dadurch ausgetauscht werden, ohne dass jedes Template oder jede
Seite einzeln angepasst werden muss. Freie CSS- oder HTML-Eingaben bleiben
ausgeschlossen.

### Globale Icon-Verwaltung

Der `Icon-Katalog` verwaltet alle funktionalen Icons zentral. Dazu gehören
unter anderem Start, Kalender, Chat, Mehr, Zurück, Schließen, Suche,
Passwort anzeigen/verbergen, Datei, Mikrofon, Benachrichtigung, Bearbeiten,
Löschen, Speichern und Statussymbole.

Für jedes semantische Icon wird eine Zuordnung gepflegt:

| Angabe | Zweck |
|---|---|
| `icon_key` | stabiler fachlicher Schlüssel, zum Beispiel `password-show` |
| `label` | verständlicher Name |
| `asset` | freigegebenes Icon aus dem zentralen Katalog |
| `size_token` | globale Icongröße |
| `stroke_token` | Strichstärke beziehungsweise Stil |
| `is_active` | verwendbar oder deaktiviert |
| `preview` | Darstellung in der Verwaltungsmaske |

Die Administration kann das hinterlegte Icon je Funktion austauschen und die
Auswirkung sofort in einer Komponenten- und Seitenvorschau prüfen. Die
fachliche Bedeutung bleibt dabei unverändert: Das Icon `password-show` darf
also optisch geändert werden, bleibt aber weiterhin dem Anzeigen des
Passworts zugeordnet.

Neue Icons werden nur durch berechtigte Administratoren in den Katalog
aufgenommen. Dabei werden Format, Lizenz, Abmessungen, Stil, Lesbarkeit und
Kontrast geprüft. Die Seiten referenzieren ausschließlich `icon_key` und
enthalten keine eigenen SVGs oder Bilddateien.

### Chat: Reaktionspakete und Sticker

Emojis, Sticker und Animationen werden nicht als funktionale Icons im
`Icon-Katalog` gepflegt. Dafür gibt es unter `Portalverwaltung → Chat` den
Bereich `Reaktionspakete`. Dort können berechtigte Administratoren Pakete
anlegen, Assets hinzufügen, ändern, deaktivieren und in einer Chatvorschau
testen.

Die Pflege umfasst:

- Paketname, Beschreibung und Pakettyp;
- Emoji-, Sticker- oder Animations-Assets;
- Vorschau und Reihenfolge;
- Alternativtext und Lizenznachweis;
- Größen-, Format-, Seitenverhältnis- und Sicherheitsprüfung;
- globale oder begrenzte Zuweisung zu Schule, Klasse oder Chatraum;
- Aktivierung und Rücknahme einzelner Assets;
- Vorschau der Schnellpalette mit den vier häufigsten Reaktionen und dem
  vollständigen „Mehr“-Bereich.

Die bisherigen `ChatReactionPack`- und `ChatReactionAsset`-Modelle bilden
dafür die fachliche Grundlage. Normale Benutzer können keine eigenen Assets
hochladen. Die Zuordnung zu einem Chat erfolgt über das freigegebene Paket,
nicht durch individuelle CSS- oder Template-Anpassungen.

### Portalverwaltung: zentrale Design-Token-Karte

In der Portalverwaltung wird eine zentrale Karte „Designsystem / Tokens“
vorgesehen. Sie ist die einzige fachliche Pflegeoberfläche für die globalen
Designwerte.

Die Karte enthält eine Theme-Auswahl. Zum Start werden genau zwei globale
Theme-Varianten verwaltet:

- `Hellmodus`;
- `Dunkelmodus`.

Die gewählte Variante wird jeweils separat bearbeitet und kann separat
vorgezeigt werden. Die Komponenten, Layouts und semantischen Token-Namen
bleiben in beiden Varianten identisch.

### Reiter und Bearbeitungsablauf der Theme-Karte

In der Theme-Verwaltung wird zuerst ein Theme ausgewählt, zum Beispiel
`Hellmodus` oder `Dunkelmodus`. Danach werden die globalen Tokenblöcke über
getrennte Reiter bearbeitet:

1. **Farben** – Farbrollen, Transparenzen, Statusfarben, Hintergrundbild und
   Überlagerungsfarbe;
2. **Typografie** – Schriftfamilie, Größen, Gewichte, Zeilenhöhen und
   responsive Typografiestufen;
3. **Abstände & Größen** – Abstandsskala, Inhaltsbreite, Feld-/Buttonhöhen
   und Icongrößen;
4. **Form & Tiefe** – Radien, Rahmen, Karten- und Dialogschatten;
5. **Interaktion & Bewegung** – Fokus, Hover, Übergänge, Animationen und
   reduzierte Bewegung.

Alle Reiter verwenden dieselben Zustände für Entwurf, Vorschau, Übernahme und
Rücksetzen. Änderungen werden immer im Kontext des ausgewählten Themes
angezeigt und können über mehrere Reiter hinweg gesammelt bearbeitet werden.
Die Vorschau kann zwischen Hell- und Dunkelmodus wechseln, ohne die fachliche
Seite oder ihr Layout zu ändern.

Der verbindliche Ablauf lautet:

```text
Theme auswählen
→ Reiter auswählen
→ globalen Tokenblock bearbeiten
→ Übersichtsseite in Desktop/Mobil prüfen
→ Änderungen speichern oder verwerfen
→ Theme erst mit „Übernehmen“ global aktivieren
```

Für jeden bearbeitbaren Token werden angezeigt:

- Tokenname und verständliche Beschreibung;
- aktuelle Farbe beziehungsweise aktueller Wert;
- Farbauswahl per Color-Picker;
- direkte Eingabe und Validierung eines Hexcodes;
- Transparenzwert beziehungsweise Alpha-Anteil;
- getrennte Werte für Hellmodus und Dunkelmodus;
- Vorschau des Tokens auf hellen und dunklen Oberflächen;
- Rücksetzen auf den freigegebenen Standardwert;
- geänderte, aber noch nicht übernommene Werte.

Über „Vorschau“ wird die Übersichtsseite mit den aktuellen Entwurfswerten
gerendert. Die Vorschau verwendet synthetische beziehungsweise vorhandene
Beispieldaten und verändert noch keine produktiven Einstellungen. Erst die
ausdrückliche Aktion „Übernehmen“ speichert die Token global im ausgewählten
Theme und macht sie für alle Seiten und Komponenten wirksam.

Die Karte muss außerdem anzeigen, welche Komponenten vom Token betroffen sind,
zum Beispiel Karten, Buttons, Eingabefelder oder Statusmeldungen. Es gibt
keine Möglichkeit, aus dieser Oberfläche eine Farbe nur für eine einzelne
Seite zu speichern. Globale Abweichungen werden ausschließlich als
dokumentierte Theme- oder Komponentenvariante angelegt.

### Hell- und Dunkelmodus

Hell- und Dunkelmodus verwenden dieselben semantischen Token-Namen, aber
jeweils eigene Werte. Zum Beispiel bleibt `surface` der Name der Oberfläche;
die konkrete helle beziehungsweise dunkle Farbe wird in der jeweiligen
Theme-Variante gepflegt. Seiten und Komponenten müssen dadurch nicht wissen,
welcher Modus aktiv ist.

Die Design-Karte bietet dafür einen Modus-Umschalter und zeigt beide Varianten
parallel oder nacheinander in einer Vorschau. Die Übernahme kann nur erfolgen,
wenn beide Modi die Kontrast- und Lesbarkeitsprüfung bestehen.

Transparenz wird als eigener globaler Tokenwert gepflegt. Für Statusflächen,
aktive Filter, Warnungen und Abwesenheitsanzeigen können so beispielsweise
16 %, 20 % oder 24 % Deckkraft eingestellt werden. Die Komponente mischt den
semantischen Farbtoken mit der jeweiligen Oberfläche; Seiten speichern keine
eigenen Alpha-Werte.

### Globales Hintergrundbild

Jede Theme-Variante kann optional ein globales Hintergrundbild erhalten. Das
Bild wird hinter der gesamten Portaloberfläche dargestellt und nicht als
individueller Seitenhintergrund gespeichert. Vorgesehen sind:

- Bild-Upload mit Format-, Größen- und Sicherheitsprüfung;
- optionale Bildreferenz statt direkter Seiten-CSS-Regel;
- Transparenz beziehungsweise Deckkraft;
- Positionierung, Skalierung und Wiederholung;
- optionale Überlagerungsfarbe zur Sicherung der Lesbarkeit;
- Vorschau auf der Übersichtsseite in Hell- und Dunkelmodus;
- Rücksetzen auf keinen Hintergrund.

Damit können beispielsweise saisonale Hintergründe für Weihnachten oder
Ostern hinterlegt werden. Karten, Formulare und Navigation bleiben trotzdem
globale Komponenten mit eigener Oberfläche. Die Hintergrundgrafik darf weder
Textkontrast noch Bedienbarkeit beeinträchtigen; die Übernahme wird deshalb
mit Lesbarkeitsprüfung angezeigt.

Für eine sichere Pflege sind zusätzlich vorgesehen:

- Entwurf, Vorschau und Übernahme als getrennte Zustände;
- Änderungsnachweis mit Administrator und Zeitpunkt;
- Rücksetzen auf die letzte freigegebene Version;
- Prüfung von Kontrast und Lesbarkeit vor der Übernahme;
- Vorschau für Desktop und Smartphone;
- Hintergrundbild je Theme mit Deckkraft und Positionierung;
- keine freien CSS-Regeln oder CSS-Code-Eingaben.

### Seitenvorschlag: Hellmodus

Der Hellmodus verwendet eine ruhige, helle Portaloberfläche:

| Rolle | Vorschlag |
|---|---|
| Seitenhintergrund | kühles, sehr helles Blau `#F4F8FC` |
| Karten und Formulare | Weiß `#FFFFFF` |
| erhöhte Oberfläche | blaues Weiß `#F8FBFE` |
| Primäraktionen | KlassID-Blau `#087EBD` |
| starke Akzente | Tiefblau `#075985` |
| Haupttext | dunkles Blau-Schwarz `#17324D` |
| Nebentext | gedämpftes Blau `#5D7890` |
| Rahmen | helles Blau-Grau `#C9DCEB` |

Die Übersichtsseite erhält dabei einen hellen Seitenhintergrund, weiße Karten,
klare blaue Primäraktionen und zurückhaltende Statusflächen. Aktive Elemente
sind blau gefüllt; inaktive Elemente bleiben hell mit blauem Text.

### Seitenvorschlag: Dunkelmodus

Der Dunkelmodus behält dieselben Layouts und Komponenten, verwendet aber eine
dunkle, kontrastreiche Oberfläche:

| Rolle | Vorschlag |
|---|---|
| Seitenhintergrund | tiefes Blau `#0F1D2E` |
| Karten und Formulare | dunkles Blau `#172A3D` |
| erhöhte Oberfläche | `#203A52` |
| Primäraktionen | helleres Blau `#28A9E0` |
| starke Akzente | `#7DD3FC` |
| Haupttext | sehr helles Blau-Weiß `#F1F7FB` |
| Nebentext | `#A9C0D1` |
| Rahmen | `#35536B` |

Die Übersichtsseite bleibt strukturell identisch. Karten werden nicht schwarz,
sondern dunkelblau dargestellt. Primäraktionen bleiben klar erkennbar, ohne
zu leuchten; Statusfarben erhalten eigene dunkle Flächen mit ausreichendem
Kontrast.

### Gemeinsame Seitenstruktur beider Modi

```text
App-Shell
├── globale Navigation
├── Seitenkopf mit Kontext und Titel
├── Inhaltsraster
│   ├── Primärkarte / Tagesübersicht
│   ├── Modul- und Statuskarten
│   └── Listen, Hinweise und leere Zustände
└── globale Aktionen und Rückmeldungen
```

Die Design-Karte soll diese Übersichtsseite in beiden Modi nebeneinander oder
per Umschalter anzeigen. Dadurch werden Unterschiede durch die Theme-Tokens
sichtbar, nicht durch zwei verschiedene Seitenentwürfe.

### Token-Block 2: Typografie – erster Vorschlag

Für das gesamte Portal wird zunächst eine einheitliche Sans-Serif-Schrift
vorgeschlagen. Überschriften und Fließtext verwenden dieselbe Familie; die
Hierarchie entsteht durch Größe, Gewicht, Farbe und Zeilenhöhe. Dadurch bleibt
die Darstellung von Login, Dashboard, Profil, Kalender, Chat und Verwaltung
konsistent.

```css
:root {
  --font-body: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-heading: var(--font-body);

  --text-xs: 0.75rem;       /* 12px */
  --text-sm: 0.875rem;      /* 14px */
  --text-md: 1rem;          /* 16px */
  --text-lg: 1.125rem;      /* 18px */
  --text-xl: 1.5rem;        /* 24px */
  --text-2xl: 2rem;         /* 32px */
  --text-display: 2.75rem;  /* 44px */

  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;

  --leading-tight: 1.2;
  --leading-normal: 1.5;
  --leading-relaxed: 1.65;
}
```

Empfohlene Verwendung:

- `display`: nur für große Seitenüberschriften;
- `2xl`/`xl`: Seiten- und Kartenüberschriften;
- `lg`: Abschnittsüberschriften;
- `md`: Standardtext und Formulare;
- `sm`: Hinweise, Metadaten und Sekundärinformationen;
- `xs`: nur für kompakte Status- und Hilfsinformationen.

Die Schriftgröße soll auf kleinen Bildschirmen nicht zu stark schrumpfen.
Statt seitenbezogener Sonderwerte werden wenige globale responsive
Typografiestufen verwendet.

### Token-Block 3: Form & Tiefe – erster Vorschlag

Die Oberflächen sollen freundlich und modern wirken, aber nicht wie einzelne
schwebende Buttons. Deshalb werden Radien und Schatten zentral begrenzt:

| Token | Vorschlag | Verwendung |
|---|---:|---|
| `radius-sm` | 6 px | kleine Felder, Badges, kompakte Elemente |
| `radius-md` | 10 px | Eingabefelder und Standardbuttons |
| `radius-lg` | 16 px | Karten und Panels |
| `radius-xl` | 24 px | große Hero-/Dialogflächen |
| `radius-pill` | 999 px | Chips, Schalter und Pill-Elemente |
| `shadow-card` | sehr dezent | Karten bei erhöhtem Kontext |
| `shadow-dialog` | deutlich, weich | Dialoge und modale Ebenen |
| `shadow-focus` | farbiger Fokus | sichtbarer Tastaturfokus |

Karten erhalten standardmäßig einen feinen Rahmen und nur einen leichten
Schatten. Stärkere Schatten bleiben Dialogen, Popovers und geöffneten Menüs
vorbehalten. So bleibt die Seite ruhig und die visuelle Hierarchie wird nicht
durch überall gleich starke Schatten verwischt.

### Token-Block 5: Interaktion & Bewegung

Für Fokus, Übergänge und Animationen gelten global:

| Token | Vorschlag | Verwendung |
|---|---:|---|
| `focus-ring` | 2 px plus 2 px Abstand | Tastaturfokus |
| `motion-fast` | 120 ms | Hover und kleine Statusänderungen |
| `motion-standard` | 200 ms | Karten, Buttons und Tabs |
| `motion-slow` | 300 ms | Dialoge, Panels und Seitenwechsel |
| `ease-standard` | `ease-out` | Standardbewegung |
| `ease-emphasis` | `ease-in-out` | hervorgehobene Übergänge |

Hover verändert keine Elementgröße. Fokus bleibt sichtbar und darf nicht nur
über Farbe vermittelt werden. Touch-Ziele bleiben mindestens 44 × 44 Pixel
groß. Für reduzierte Bewegung werden Animationen deaktiviert oder deutlich
verkürzt.

## 7. Vorgeschlagene Bereinigungsreihenfolge

1. Dieses Inventar und die globale Geltungsregel gemeinsam bestätigen.
2. Tokens und Theme-Schnittstelle festlegen; noch keine Fachseite umbauen.
3. Einen neutralen globalen Komponenten-Katalog erstellen: Button, Icon-Button, Feld,
   Passwortfeld, Card, Badge, Meldung, Dialog und Navigation.
4. Alte globale Regeln aus `app.css` identifizieren und in drei Gruppen teilen:
   behalten, migrieren, löschen.
5. Login als erste Referenzseite vollständig auf den globalen Katalog umstellen.
6. Profil und Startseite als zweite und dritte Referenzseite umstellen.
7. Nach jeder Seite Desktop, Smartphone, Tastaturbedienung und Fehlermeldungen
   prüfen.
8. Erst danach Kalender, Chat, Familie und die übrigen Module migrieren.
9. Nicht mehr verwendete Legacy-Dateien und V2-Duplikate entfernen.
10. Staging neu bauen und erst nach visueller Abnahme produktiv übernehmen.

## Verbindliches Zielbild nach der Zusammenführung

Die zentral beschlossenen Theme-Tokens und globalen Komponenten sind die
einzige maßgebliche visuelle Quelle. Nach der Migration verbleiben in
fachlichen Seiten- und Modulregeln keine eigenen Definitionen für Farben,
Transparenzen, Farbverläufe, Typografie, Abstände, Größen, Radien, Schatten,
Button-, Formular-, Karten-, Dialog- oder Meldungsvarianten, Icons oder
responsive Grundregeln.

Fachliche Templates und Module liefern weiterhin Struktur, Reihenfolge,
Inhalte, Relationen, Sichtbarkeitsregeln und fachliche Zustände. Die visuelle
Umsetzung erfolgt ausschließlich über die zentrale Verwaltung und ihre
freigegebenen Tokens beziehungsweise Komponentenvarianten. Die Migrationsliste
bildet für jede Altregel den konkreten Ersatz-Token oder die Ersatzkomponente
ab; erst nach dieser Zuordnung wird die alte Einzelregel entfernt.

### Abschlussprüfung auf Dubletten

Die erste technische Konsistenzprüfung zeigt, dass die Zusammenführung im
Quellbestand noch nicht abgeschlossen ist:

- `app.css` enthält zwei eigene `:root`-Tokenblöcke mit unterschiedlichen
  Farb-, Radius- und Schattenwerten;
- `styles.css` definiert zusätzlich eigene Fallback-Tokens und weiterhin
  Kompatibilitätsnamen wie `--color-primary` statt der beschlossenen
  semantischen Zielnamen;
- `.button` und verwandte Komponenten sind sowohl in den importierten
  Legacy-Dateien als auch mehrfach in `styles.css` definiert;
- Formular-, Dialog-, Status- und Navigationsregeln werden durch die weiterhin
  importierten Altdateien mehrfach beeinflusst;
- feste Farben, Radien und Schatten stehen trotz zentraler Tokens noch in
  mehreren Modulregeln.

Bewusst zulässig und nicht als Fehler gewertet werden `--tp-*` innerhalb der
isolierten Theme-Vorschau sowie kontextbezogene Tokens wie
`--calendar-category`. Diese dürfen nicht in die Portal-Grundtokens gelangen.

Damit lautet das Ergebnis: Die fachliche Entscheidung ist abgeschlossen, die
technische CSS-Bereinigung aber noch nicht. Vor der eigentlichen Umsetzung
werden die zwei `:root`-Systeme, die mehrfachen Button-/Formularregeln und die
Kompatibilitätsnamen in einer kontrollierten Migration zusammengeführt.

## 8. Entscheidungen, die noch offen bleiben

Diese Punkte werden bewusst nicht angenommen:

- Anzahl weiterer Themevarianten neben Hell- und Dunkelmodus
- Schriftfamilie und typografische Hierarchie
- Karten flach oder mit Schatten
- Grundform und Gewicht der Buttons
- Form der Desktop-Navigation
- mobile Bottom-Navigation und Ebenenwechsel
- verbindliche Breakpoints
- Animationsumfang und reduzierte Bewegung
- Icon-Satz und Hosting der Icons

Sobald diese Punkte gemeinsam festgelegt sind, werden die Platzhalter in den
Tokens ersetzt und die erste Referenzseite umgesetzt. Bis dahin bleibt die
bestehende Anwendung unverändert.
