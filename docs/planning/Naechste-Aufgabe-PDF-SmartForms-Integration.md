# Getrennter Folgeauftrag / nicht umgesetzt

## PDF-Formulare, Vorbefüllung und mobiler Rücksendeablauf

> Dieses Dokument ist ausschließlich ein Folgeauftrag nach dem aktuellen
> Qualitätsgate. Im laufenden Auftrag entstehen dafür keine Modelle,
> Migrationen, PDF-Engine, Menüpunkte oder Mail-/Share-Funktionen.

## Verbindliches vorgeschaltetes Architektur- und Lizenzgate

Die eigenständige Referenz liegt unter
`D:\Development\Repos\PDF-SmartForms-Studio`. Der am 1. September 2026
lesend geprüfte Bestand ist keine Git-Arbeitskopie, sondern eine gebündelte
Windows-Distribution mit EXE, Python-3.12-/PyQt6-/PyMuPDF-/Pillow-Laufzeit,
Dokumentation und einem `.psfstemplate`-Beispiel. Quellmodule, Commitverlauf und
automatisierte Tests sind darin nicht prüfbar. Die Dokumentation beschreibt
getrennte Domänen für PDF, Profile, Templates, Feldlexikon, Signaturen und
Export, AcroForm-Erkennung, Vorschläge für flache PDFs, manuelle Feldzuordnung,
einen visuellen Designer, portable JSON-/Templateformate und eine lokale
Sicherheitsvorschau.

Der vorhandene Lizenztext ist ausdrücklich ein Entwurf: Source Available, alle
Rechte vorbehalten und noch keine endgültige Nutzungslizenz. Vor Übernahme von
Code, Formaten oder Assets ist deshalb eine schriftliche Wiederverwendungs- und
Lizenzentscheidung erforderlich. Die Distribution wird weder blind kopiert
noch als verschachteltes Repository eingebunden. Bevorzugter Integrationsweg
ist ein getesteter, headless nutzbarer Bibliothekskern im modularen
Django-Monolithen. Ein separater PDF-CRUD-Microservice benötigt einen
nachgewiesenen technischen Bedarf und eine neue ADR.

Vor Implementierung ist die echte Quellarbeitskopie zu beschaffen und zu
prüfen: Architektur, Datenmodelle, AcroForm-/Flachfeld-Erkennung,
Profil-/Mappinglogik, Konfigurationsmodus, mobile Planung, Tests,
Abhängigkeiten/SBOM und wiederverwendbare Kernmodule. Das dokumentierte
Human-in-the-loop-Prinzip und die Trennung von Begriffsmapping und Profilwerten
sind fachlich wertvoll, gelten aber nicht als Nachweis eines direkt
übernehmbaren Bibliotheksvertrags.

## Zielbild und Versionierung

Berechtigte Administratoren legen in „PDF-Formulare“ Templates an,
versionieren, veröffentlichen und ziehen sie zurück. Bestehende geschützte
Dokumentdownloads bleiben erhalten. Ein ausdrücklich gestarteter Modus
„Formular konfigurieren“ beziehungsweise „PDF anlernen“ erkennt vorhandene
AcroForm-Felder. Für flache PDFs lassen sich kontrolliert neue Feldbereiche auf
Seiten positionieren.

Jede Felddefinition besitzt stabile ID, Seite, PDF-Koordinaten, Typ,
Bezeichnung, Pflichtstatus, Format/Validierung, Standardwert, Profil-Mapping
und Sichtbarkeitsregel. Touch- und Desktopbedienung unterstützen Zoomen,
Verschieben, Größenänderung, Feldliste, Vorschau und Rückgängig. Änderungen
erzeugen unveränderliche Versionen und werden vor Veröffentlichung mit
synthetischen Daten geprüft.

## Datenmodell

Plane mindestens:

- `PDFTemplate` für Schule/Klasse, Status und stabile Identität,
- `PDFTemplateVersion` für PDF-Hash, Version, Rückzug und Empfängerfreigabe,
- `PDFFieldDefinition` für Position, Typ, Pflichtstatus und Validation,
- `PDFProfileMapping` für ausschließlich erlaubte Profilquellen,
- `PDFRecipientConfiguration` für bestätigte Empfänger und Textvorlagen,
- `PDFAssignment` für persönliche/klassenbezogene Aufgabe und Fälligkeit,
- `PDFUserDraft` für fortsetzbare Eingaben und gewählte Person/Beziehung,
- `PDFGeneration`/`PDFExportEvent` für Idempotenz, Ablauf und Audit.

Generierte Binärdaten werden nicht unnötig dauerhaft gespeichert. Template,
Konfiguration und Ausgabe erhalten stabile Hashes, dokumentierte Löschung und
Isolation nach Schule, Klasse, Version und Berechtigung.

## Allowlist-basierte Vorbefüllung

Erlaubte Quellen sind fest definierte Felder wie persönlicher Name, Anschrift,
E-Mail, Telefon, bestätigter Schülername, Schule, Klasse und bestätigte
Beziehung. Freie Datenbankpfade, Templateausdrücke und Code sind verboten.
Vorbefüllung entsteht erst zur Laufzeit für den authentisierten Benutzer.

Vor Bestätigung zeigt die Oberfläche Wert und Herkunft. Zulässige Werte können
korrigiert und optional bewusst ins eigene Profil übernommen werden. Mehrere
Kinder und Beziehungen werden explizit ausgewählt; keine Heuristik setzt ein
Kind automatisch ein. Fehlende Pflichtwerte erhalten Rahmen, Icon, Text und
Fehlerzusammenfassung; der Fokus springt gezielt zum nächsten Fehler.

Persönliche Ausgaben besitzen opaque IDs und unpersönliche Dateinamen,
`Cache-Control: no-store`, kurze Aufbewahrung und direkte Löschbarkeit. Keine
ausgefüllten PDFs gelangen in Git, Logs, öffentliche Medienpfade oder
unverschlüsselte Exporte.

## Aufgaben-, Neuigkeits- und Bestätigungsablauf

Eine veröffentlichte Version kann als persönliche oder klassenbezogene Aufgabe
mit Fälligkeit erscheinen. Home und Glocke verwenden die persönliche,
revisionsbezogene Neuigkeitslogik. Push bleibt neutral und enthält keine
Formular-, Kinder- oder Reisedetails.

Statuswerte unterscheiden mindestens `neu`, `geöffnet`, `unvollständig`,
`bereit zum Export`, `heruntergeladen/geteilt` und `vom Benutzer als erledigt
markiert`. „Geteilt“ oder „Mailprogramm geöffnet“ gilt niemals als Eingang bei
der Schule. Eine Portalbestätigung ist keine qualifizierte elektronische
Signatur. Gezeichnete oder typisierte Unterschriften erfordern vor Umsetzung
eine fachlich-rechtliche Entscheidung; es wird keine Rechtswirkung behauptet.

## Download, Gerätespeicherung und Teilen

Die Oberfläche bietet „PDF herunterladen“, „Auf Gerät speichern“ und
„Teilen/E-Mail öffnen“. Auf unterstützten Mobilgeräten wird die Web Share API
mit File Sharing erst nach Capability-Prüfung genutzt. Ohne Unterstützung
bleibt der Ablauf stabil.

Ein `mailto:`-Link kann Empfänger, Betreff und Text vorbelegen, aber keinen
standardkonformen Anhang garantieren. Desktop-Fallback: PDF herunterladen,
Mailclient öffnen und deutlich „Bitte die gerade gespeicherte PDF-Datei
anhängen“ erklären. Eine lokal erzeugte `.eml`-Datei ist nur nach Sicherheits-
und Plattformtests eine optionale Ergänzung, nie der einzige Weg. Das Portal
speichert keine Eltern-SMTP-Passwörter oder OAuth-Tokens und sendet nicht im
Namen eines Elternteils.

## Empfänger und begrenzte Mailvorlage

Jede Formularversion referenziert einen in Schule/Klasse bestätigten Empfänger;
PDF-Text wird nicht als Empfängerquelle vertraut. Der Admin bestätigt ihn vor
Veröffentlichung. Empfängerzahl und Adresslänge sind begrenzt, Adressen werden
validiert und CR/LF-Header-Injection wird abgewiesen.

Betreff und Kurztext verwenden ausschließlich erlaubte Platzhalter, etwa
Formularbezeichnung und einen freigegebenen Familiennamen. Kinder- und
Gesundheitsdaten gehören nicht in den Betreff. Vor Übergabe sieht der Benutzer
Empfänger, Betreff, Text und Dateiname. From und Reply-To stammen aus seinem
Mailclient; das Portal fälscht keinen Absender.

## PDF-Sicherheit

Prüfe MIME und Magic Bytes, Größen-/Seitenlimits, Verschlüsselung,
Beschädigungen, JavaScript, Launch Actions, externe Ressourcen, Anhänge und
Formularaktionen. Gefährliche aktive Inhalte werden deterministisch entfernt
oder das Dokument wird abgelehnt. Dokumentenschutz wird nicht umgangen.

AcroForms werden sowohl über den kanonischen `/AcroForm/Fields`-Baum als auch
über Seiten-`/Widget`-Annotationen geprüft. Verwaiste Widgets dürfen nur bei
eindeutiger Beziehung repariert werden; doppeldeutige gleichnamige Felder
werden nicht blind neu angehängt. Nach Generierung wird die Datei neu geöffnet:
Feldwerte, Widgetwerte und Appearance Streams müssen konsistent sein. Für eine
explizit gewünschte flache Ausgabe dürfen weder Widgets noch AcroForm-Baum
verbleiben. Zusätzlich werden alle Seiten gerendert und visuell geprüft.

Rückzug sperrt neue Ausfüllvorgänge unmittelbar. Bereits bewusst
heruntergeladene Dateien können technisch nicht zurückgerufen werden; dies ist
verständlich zu erklären. Fonts, Umlaute/ß, Seitenrotation, Papierformate und
bestehende AcroForms gehören in den deterministischen Regressionstest.

## Mobile UX

Eltern durchlaufen große Kacheln und kurze Schritte statt technischer Tabellen:
Kind/Beziehung wählen, Werte prüfen, fehlende Werte ergänzen, Vorschau,
Export. Zurücknavigation, Fortschritt, Autosave, Fokusführung, Safe Areas,
virtuelle Tastatur, Hoch-/Querformat, Screenreader und Reduced Motion sind
Pflicht. Das Gesamtformular scrollt nicht horizontal; nur die PDF-Seite liegt
in einer klar begrenzten Zoom-/Pan-Fläche. Konfiguration bleibt Adminfunktion,
Ausfüllen bleibt besonders einfach.

## Pflichtgate

- abschließende Architektur-/Lizenzprüfung der echten Quellarbeitskopie,
- bestehende AcroForms und ein synthetisches feldloses PDF,
- Profilmapping mit mehreren Kindern und fehlenden Pflichtwerten,
- Umlaute/ß, Rotation, Papiergrößen und reproduzierbare Ausgabe,
- mobile/desktop Vorschau, Tastatur und Screenreader,
- Schul-/Klassenisolation, IDOR-Negativtests und zurückgezogene Version,
- beschädigte, verschlüsselte und aktive PDFs,
- idempotente Generierung, Ablauf/Löschung, Download und No-Store,
- Web Share mit Anhang auf unterstütztem Gerät,
- ehrlicher Desktop-mailto-Fallback ohne Anhangsversprechen,
- Empfänger-/Betreffvalidierung und keine Mailzugangsdaten,
- Datenschutzprüfung, Docker-Build und vollständige Tests.
