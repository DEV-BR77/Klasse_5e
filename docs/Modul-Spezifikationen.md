# KlassID – Fachliche Modulspezifikationen

Dieses Dokument beschreibt die fachlichen Module unabhängig von den Django-
Modellen. Es legt fest, welche Aufgabe ein Modul hat, welche Daten es nutzt,
welche Rollen und Berechtigungen gelten und welche UI-/Designregeln später
umgesetzt werden.

## Globale Datenregel

Freie Textfelder sind für fachliche Auswahlwerte grundsätzlich zu vermeiden.
Sie bleiben nur dort zulässig, wo tatsächlich individueller Text erwartet
wird, zum Beispiel ein Name, eine Beschreibung oder eine Nachricht.

Fachliche Werte wie Schule, Klasse, Rolle, Modul, Ort, Status, Fach,
Empfänger oder Geltungsbereich werden über Relationen, Katalogmodelle,
kontrollierte Auswahlwerte oder technische Schlüssel abgebildet. Dadurch
bleiben Suche, Berechtigungen, Auswertungen und Darstellungen einheitlich.

Adressen werden nicht als uneinheitliche Freitextkombination behandelt. Land,
Postleitzahl und Ort werden kontrolliert ausgewählt beziehungsweise validiert.
Aus der vollständigen Adresse kann anschließend ein Geodatendienst die
Latitude-/Longitude-Werte ermitteln. Der Dienstanbieter und Datenschutzumfang
werden vor der Umsetzung festgelegt; Geokoordinaten bleiben optional.

Die Reihenfolge der Arbeit ist:

```text
Moduldefinition
→ Daten- und Rechtebezug
→ Bedienablauf
→ Benachrichtigungen
→ Aufbewahrung und Bereinigung
→ CSS-/Designsystem
→ technische Umsetzung
```

## Modul 1: Chat

### 1. Zweck

Der Chat ermöglicht Klassenräume, thematische Räume und private Gespräche.
Ein Chatraum gehört eindeutig zu einer Schule und einer Klasse. Ein Raum kann
optional mit einer Veranstaltung verknüpft werden.

### 2. Fachliche Struktur

```text
School
└── SchoolClass
    └── ChatRoom
        ├── ChatRoomAccess
        ├── ChatMessage
        ├── ChatReadState
        └── ChatRetentionCategory
```

Private Gespräche werden nicht als eigenes technisches Grundmodell geführt.
Sie sind ebenfalls `ChatRoom`-Datensätze mit dem Typ `direct` und genau zwei
aktiven `ChatRoomAccess`-Einträgen.

### 3. Chatraum

Ein `ChatRoom` enthält künftig mindestens:

- Schule;
- Klasse;
- optionales Event;
- Aufbewahrungsregel;
- Raumname;
- zugewiesenen Chat-Style;
- offen/geschlossen;
- Jugendschutz aktiv/inaktiv;
- Erstellungszeitpunkt.

Das Schuljahr wird nicht zusätzlich am Chatraum gespeichert. Die Klasse ist
bereits eindeutig einer Schule und einem Schuljahr zugeordnet.

### 4. Zielgruppe und Zugriff

Ein einfaches Textfeld `audience` reicht nicht aus. Der Zugriff wird über eine
separate Raumzuordnung abgebildet. Unterstützte Zielgruppen können sein:

- alle Mitglieder einer Klasse;
- Erziehungsberechtigte;
- Schüler;
- Lehrkräfte;
- Elternvertretung;
- eine bestimmte organisatorische Rolle;
- einzelne Personen;
- Kombinationen mehrerer Regeln.

Der Zugriff wird aus Schule, Klasse, `RoleAssignment`,
`GuardianStudentRelationship` und gegebenenfalls einer expliziten
Personenzuweisung ermittelt. Die Mitgliedschaft wird nicht händisch aus
mehreren Tabellen übersetzt.

### 5. Jugendschutz

Jeder Chatraum erhält eine Jugendschutz-Einstellung. Der Jugendschutz wirkt
auf Text, Bilder und künftig weitere Medien. Er ersetzt keine Rollen- oder
Zugriffsprüfung.

#### Textfilter

Der Textfilter wird nicht auf eine einzelne fest eingebaute Wortliste
begrenzt. Er verwendet administrierbare, versionierte Regeln. Eine Regel kann
unter anderem enthalten:

- Suchbegriff beziehungsweise normalisierte Wort-/Ausdrucksgruppe;
- Kategorie und Schweregrad;
- Variantenbehandlung (Groß-/Kleinschreibung, Trennzeichen, Schreibvarianten);
- Geltungsbereich (global, Schule, Klasse oder einzelner Chatraum);
- Aktion bei Treffer;
- Aktivstatus, Gültigkeit und Änderungsnachweis.

Die konkrete Wortliste bleibt damit erweiterbar, ohne den Chat-Code ändern zu
müssen. Die Administration darf Regeln nur über eine geschützte
Verwaltungsmaske pflegen; freie Regeln in einem normalen Benutzerformular
sind nicht vorgesehen.

#### Automatische Reaktion

Bei einem aktiven Treffer wird der betroffene Inhalt automatisch verborgen:

- Text wird im Chat ausgepunktet beziehungsweise unlesbar dargestellt;
- Bilder werden ausgepixelt beziehungsweise als gesperrte Vorschau gezeigt;
- die Nachricht bleibt für die berechtigte Prüfung technisch erhalten;
- es gibt zunächst keinen frei auswählbaren Moderationsstatus für normale
  Benutzer.

Bei einem automatisch maskierten Bild erhält der Benutzer unmittelbar eine
kurze Erklärung, zum Beispiel: „Das Bild wurde aufgrund von
Jugendschutzbestimmungen maskiert. Falls dies ein Fehler ist, kannst du eine
Prüfung anfordern.“ Über diese Aktion kann der Absender einen Bild-
Prüfantrag an den zuständigen Moderator senden.

Der Inhalt wird nicht automatisch als „genehmigt“ veröffentlicht. Der
Absender kann den eigenen ausgeblendeten Text oder das Bild anklicken und
eine Prüfung durch den zuständigen Moderator anfordern. Zum Start ist das der
Plattformadministrator beziehungsweise der Administrator der jeweiligen
Klasse. Die spätere Rolle `Chat-Moderator` bleibt vorbereitet.

#### Protokollierung und Eskalation

Jeder Treffer wird mit Nachricht, Absender, Zeitpunkt, Regel, Medium und
Ergebnis im technischen beziehungsweise Audit-Protokoll erfasst. Die
Nachricht speichert nur eine zusammengefasste Trefferinformation.

Wenn derselbe Benutzer innerhalb eines gleitenden Zeitfensters von 24 Stunden
mehrfach eine Jugendschutzregel auslöst, wird im Administrationsdashboard ein
Hinweis erzeugt. Der Hinweis enthält die Anzahl, den Zeitraum und die
betroffenen Regel-/Nachrichtenreferenzen, aber nicht automatisch eine
Sanktion. Die konkrete Prüfung und weitere Maßnahme bleibt eine
Administratorentscheidung.

#### Prüfungen und Meldungen

Der Einspruch gegen ein automatisch maskiertes Bild ist aktiv vorgesehen. Im
Administrationsdashboard erscheint ein Antrag mit Bildreferenz, Regel,
Messwerten, Benutzer, Chatraum und Zeitpunkt. Der Moderator kann den Antrag
prüfen, als Fehlalarm markieren und die Regel beziehungsweise Schwelle später
anpassen.

Eine allgemeine Funktion „diesen Chat melden“ wird technisch vorbereitet,
bleibt für normale Benutzer zunächst aber deaktiviert. Sie wird erst nach
einer eigenen Entscheidung zu Prüfprozess, Rückmeldung und
Missbrauchsschutz freigeschaltet.

#### Alters- und Chatprofile

Die Jugendschutzempfindlichkeit wird nicht hart im Chat-Code verdrahtet. Ein
Chat kann ein administrativ gepflegtes Jugendschutzprofil verwenden. Das
Profil bestimmt insbesondere:

- aktivierte Regelgruppen;
- Text- und Bildschwellen;
- erlaubte Medienarten;
- Verhalten bei Grenzfällen;
- ob ein Bild-Prüfantrag angeboten wird.

Damit kann ein Kinderchat mit einem strengeren Profil betrieben werden als ein
älterer Klassenkontext. Die Profile bleiben zentral versioniert und können
Schule, Klasse oder Chatraum zugewiesen werden.

### 6. Nachrichten

Eine Nachricht gehört zu einem Chatraum oder einer privaten Unterhaltung und
enthält mindestens:

- Absender;
- Inhalt;
- Erstellungszeitpunkt;
- optionalen Bearbeitungszeitpunkt;
- Lösch-/Moderationsstatus;
- optionalen Dateianhang;
- optionalen Bezug auf eine andere Nachricht.

Die technische Composer-Oberfläche soll Emoji, Datei-Anhang und Spracheingabe
unterstützen. Enter sendet standardmäßig; `Strg+Enter` erzeugt einen
Zeilenumbruch.

#### Reaktionen, Emojis und Sticker

Auf Smartphone und Tablet öffnet ein 500 ms langer Druck auf eine Nachricht
eine kompakte Schnellpalette. Auf dem Desktop erscheint nach 500 ms Mouse-over
eine kleine Leiste mit den häufigsten Reaktionen. Die Reaktion wird erst nach
der Auswahl gesetzt. Eine fokussierte Nachricht öffnet die Palette außerdem
mit Enter oder Leertaste.

Ein einfacher Klick setzt keine Reaktion. Ein Doppelklick wird nicht als
Reaktionsgeste verwendet, damit Zoom, Auswahl, Tastaturbedienung und andere
Browserfunktionen nicht beeinträchtigt werden.

Direkt sichtbar sind die vier häufigsten Reaktionen; über „Mehr“ wird das
vollständige freigegebene Paket geöffnet.
Vorgesehen sind unter anderem Zustimmung, Daumen hoch, Lachen, Freude,
Überraschung sowie administrativ gepflegte Sticker und animierte Assets.

Die Reaktionspalette kann je nach Chat, Schule, Klasse oder Style aus einem
freigegebenen `ChatReactionPack` stammen. Eine Person kann ihre Reaktion
auswählen, ändern oder entfernen. Pro Nachricht und Benutzer wird die
Reaktion nachvollziehbar gespeichert.

### 7. Darstellung und Nachrichtenlayout

Die Standarddarstellung lautet:

```text
eigene Nachricht       → rechts
Nachricht anderer      → links
```

Das Verhalten wird zentral in der Chat-Oberfläche definiert und nicht pro
Nachricht gespeichert. Alternative Layouts können später über einen
`message_layout_key` des Styles bereitgestellt werden.

### 8. Chat-Styles

Ein Raum verweist auf einen administrativ gepflegten `ChatStyle`. Der Raum
speichert keine freien CSS-Regeln.

Die Pflege erfolgt als eigener Bereich der Portalverwaltung:
`Portalverwaltung → Module → Chat → Chat-Styles`. Der Chat ist damit ein
einstellbares Modul mit eigener Vorschau und nicht nur eine globale
Theme-Ausnahme.

Ein Style kann enthalten:

- automatisch erzeugten technischen Schlüssel;
- sichtbaren Namen;
- Grundtheme;
- Haupt-, Flächen-, Text- und Akzentfarben;
- definierte Schriftart und optionale Schriftstärke;
- Hintergrundbild oder Asset;
- Hintergrundbild-Deckkraft, Position, Skalierung und Wiederholung;
- optionaler Hintergrund-Overlay zur Lesbarkeit der Nachrichten;
- `effect_key` für einen visuellen Effekt;
- `message_layout_key` für eine Darstellungsvariante;
- Aktivstatus.

Beispiele:

```text
Standard
Schultafel
Sommerferien
Winter mit Schneefall
```

Ein neuer Style soll über eine Verwaltungsmaske aus vorhandenen Bausteinen
angelegt werden können. Neue Farben, Bilder, Schriftkombinationen und bereits
bereitgestellte Effekte benötigen keine Programmierung. Neue Effektarten oder
neues Verhalten müssen zunächst im zentralen Designsystem technisch ergänzt
werden.

Die Verwaltungsmaske bietet für jeden Chat-Style eine Desktop- und
Mobile-Vorschau. Das Hintergrundbild wird auf die Chatfläche begrenzt, mit
Deckkraft und optionalem Overlay lesbar gehalten und darf keine eigenen freien
CSS-Werte in Templates erzeugen. Ein Chatraum kann anschließend einen aktiven
Style auswählen; die Style-Auswahl bleibt von den globalen Hell-/Dunkel-Themes
getrennt, nutzt aber deren freigegebene Farb-, Typografie- und Tiefen-Tokens.

Für Emojis und Sticker werden administrierbare `ChatReactionPack`- und
`ChatReactionAsset`-Bausteine vorgesehen. Assets besitzen unter anderem Name,
Typ, Alternativtext, Reihenfolge, Aktivstatus, Geltungsbereich und
Herkunft/Lizenz.

Die Asset-Pflege erfolgt zunächst ausschließlich durch den
Plattformadministrator. Später kann sie gezielt für ausgewählte
Klassenadministratoren freigegeben werden. Eine allgemeine Nutzerfunktion zum
Hochladen eigener Emojis oder Sticker ist nicht vorgesehen.

Die Verwaltungsmaske prüft Dateiformat, Dateigröße, Seitenverhältnis,
Abmessungen, Sicherheitsstatus und Lizenzangabe. Als Richtwerte werden unter
anderem kompakte Formate wie 48 × 48 Pixel oder 48 × 24 Pixel vorgesehen;
konkrete Grenzen werden mit dem finalen Chat-Design festgelegt. Assets, die
die Vorgaben nicht erfüllen, werden nicht freigegeben.

### 9. Benachrichtigungen

Chatereignisse können `UserNotification` erzeugen. Die Benachrichtigung
enthält den fachlichen Bezug zu:

- Schule;
- Klasse;
- Schüler, falls relevant;
- Chat-Modul;
- gegebenenfalls Adapter;
- konkretem Chatraum oder Ereignis.

Ob eine Meldung als In-App- oder Push-Nachricht zugestellt wird, entscheidet
`NotificationPreference` zusammen mit der automatisch registrierten
`PushSubscription` des Geräts.

### 10. Aufbewahrung und Bereinigung

Jeder Chatraum kann eine `ChatRetentionCategory` verwenden. Die zentrale
Datenpflege muss dafür anbieten:

- Aufbewahrungsdauer;
- automatische Löschung an/aus;
- Vorschau und Testlauf;
- geplante Bereinigungsjobs;
- Ergebnis- und Fehlerbericht;
- Schutz relevanter oder gesperrter Daten;
- dokumentierte Freigabe vor Automatisierung.

### 11. Verwaltungsoberfläche

Die Administration benötigt für Chat mindestens:

- Chatraum anlegen, ändern, schließen und archivieren;
- Schule und Klasse zuordnen;
- Zielgruppen und Einzelberechtigungen verwalten;
- Jugendschutz konfigurieren;
- Aufbewahrungskategorie auswählen;
- Chat-Style auswählen oder anlegen;
- gemeldete Nachrichten prüfen;
- persönlichen Rückfrage-Chat aus einem Feedbackeintrag öffnen.

### 12. Offene Entscheidungen

- endgültige Felder und Regeln von `ChatRoomAccess`;
- Rollen- und Einzelpersonenzuweisung im Detail;
- genaue Schwellenwerte und Normalisierungsregeln des Textfilters;
- erlaubte Dateitypen und Größen;
- Sprachaufnahme: Browserfunktion, Upload oder beides;
- endgültige Chat-Styles und visuelle Effekte;
- technische Löschfristen je Chatkategorie;
- Detailablauf für Einspruch, Prüfung und spätere Chat-Moderatoren;
- Freigabeprozess für die zunächst deaktivierte allgemeine Chat-Meldung;
- späterer eigener Bildprüfprovider beziehungsweise eigenes lernendes Modell.

## Modul 3: Marketing-Demo und Adapter-Schnelltest

Dieses Modul erhält eine hohe Umsetzungspriorität. Es dient ausschließlich
der zeitlich begrenzten Produktdemonstration und ist kein Ersatz für die
reguläre Registrierung.

### Einladungs- und Demoablauf

1. Die Administration erstellt eine ansprechende, kurze Marketing-E-Mail.
2. Der Empfänger öffnet einen einmaligen Demo-Link.
3. Eine bekannte Schule kann bereits vorausgefüllt sein.
4. Der Empfänger ergänzt mindestens die Klasse; ein Name ist optional.
5. Fehlt ein Name, wird ein klar als Demo gekennzeichneter Platzhaltername
   verwendet, zum Beispiel „Tim Taler“.
6. Der Empfänger wählt den passenden Adapter und gibt die Zugangsdaten ein.
7. Die Adapter werden live abgefragt und die verfügbaren Module werden
   strukturiert als Demo-Dashboard angezeigt.
8. Die Demoansicht läuft nach 30 Minuten ab und der Link wird ungültig.

Die Zugangsdaten werden verschlüsselt und nur für die Laufzeit des
Testvorgangs verwendet. Sie werden nicht in ein reguläres Familien- oder
Benutzerkonto übernommen. Ein erneuter Test wird über einen neuen, separaten
Link beziehungsweise eine neue E-Mail gestartet.

### Demo-Dashboard

Das Dashboard zeigt abhängig vom Testergebnis beispielsweise Stundenplan,
Hausaufgaben, Kalender, Vertretungen und weitere verfügbare Module. Nicht
verfügbare oder fehlgeschlagene Module werden verständlich erklärt. Die
Ansicht wird nach Ablauf der Demo vollständig gesperrt.

### Administrationsregeln

- Marketing-E-Mail mit freigegebenen Textbausteinen und Vorschau;
- bekannte Schule vorausfüllbar;
- Klasse verpflichtend, Name optional;
- Demo-Platzhalter deutlich als Demo kennzeichnen;
- einmalige Tokens und Ablaufzeit serverseitig prüfen;
- Rate-Limit und Protokollierung gegen Missbrauch;
- keine dauerhafte Speicherung von Testzugangsdaten oder Demo-Inhalten;
- erneuter Test nur über einen neuen Einladungsprozess.

## Weitere Module

Weitere Module werden nach demselben Raster ergänzt. Als nächste fachliche
Bereiche sind insbesondere Kalender/Stundenplan, Hausaufgaben, Abwesenheiten,
Veranstaltungen, Speiseplan, Inhalte und Adapterfunktionen vorgesehen.

## Modul 2: Familien- und Benutzerverwaltung

### 1. Zweck

Die Familien- und Benutzerverwaltung bildet Personen, Konten, Haushalte,
Beziehungen, Rollen, Einladungen und gezielte Berechtigungen ab.

### 2. Fachliche Struktur

```text
UserAccount
└── Person
    ├── HouseholdMembership ── Household
    ├── GuardianStudentRelationship ── Student-Person
    ├── ClassMembership ── SchoolClass
    └── RoleAssignment
```

Konto, Person, Haushalt, Schülerbeziehung und organisatorische Rolle werden
getrennt geführt. Der Einrichtungsassistent legt die notwendigen Relationen
automatisch an.

### 3. Personen- und Kontaktdaten

Die Verwaltung bietet strukturierte Eingaben für:

- Vorname und Nachname;
- Geschlecht und Geburtsdatum, soweit vorgesehen;
- E-Mail und Telefonnummer;
- Straße, Hausnummer, Postleitzahl, Ort und Land;
- optionale Geo-Koordinaten;
- Profilfoto und Avatar;
- Sichtbarkeit der Kontaktdaten.

Postleitzahl, Ort und Land werden aus kontrollierten Datensätzen ausgewählt.
Die Eingabe darf Vorschläge machen, aber keine beliebigen abweichenden
Schreibweisen als neue Orte erzeugen. Eine bestätigte Adresse kann zur
Geokodierung an den festgelegten Dienst übergeben werden.

### 4. Familienverwaltung

Der erste Erwachsene legt nach der eigenen Aktivierung den Haushalt an und
kann danach weitere Erwachsene und Schüler hinzufügen. Für jede Person werden
Haushaltsrolle und konkrete Schülerbeziehungen getrennt erfasst.

Ein weiterer Erwachsener erhält nach dem Anlegen einen persönlichen
Bestätigungslink. Erst nach der Bestätigung wird sein Benutzerkonto aktiviert.

### 5. Rollen und Berechtigungen

Die Oberfläche unterscheidet:

- Haushaltsrolle;
- konkrete Beziehung zu einem Schüler;
- Plattform-, Schul- oder Klassenrolle;
- Modul- und Sichtbarkeitsrechte.

Eine gemeinsame Haushaltszugehörigkeit erzeugt keinen automatischen Zugriff
auf alle Schüler. Jede Schülerzuordnung bleibt ausdrücklich und einzeln
prüfbar.

### 6. Datenschutz und Adressdaten

Adress- und Geodaten werden nur für festgelegte Zwecke verwendet. Die
Sichtbarkeit wird pro Kontaktfeld geregelt. Geokodierung darf nur nach
definiertem Verarbeitungsvorgang und mit dokumentierter Lösch-/Änderungslogik
erfolgen.

### 7. Offene Entscheidungen

- verbindliche Orts-/Adressquelle;
- Geokodierungsdienst und Datenschutzkonfiguration;
- Hausnummer als eigenes Feld oder Teil der Straße;
- Adresshistorie und Änderungsnachweis;
- genaue Rollen- und Modulrechte in der Verwaltungsmaske;
- Einladungs- und Bestätigungsablauf im Einrichtungsassistenten.
