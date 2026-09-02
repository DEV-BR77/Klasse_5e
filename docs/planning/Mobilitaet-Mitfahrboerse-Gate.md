# UX- und Datenschutzgate: Mobilität und Mitfahrbörse

Stand: 02.09.2026 · Status: **erfüllt für die fachliche Implementierung**

Diese Spezifikation konkretisiert `Naechste-Aufgabe-Mobilitaet-Mitfahrboerse.md`. Sie erlaubt keinen Produktivbetrieb: Verantwortliche Stelle, Rechtsgrundlage, Löschfristen und Freigabetexte benötigen vor einem Realpilot eine ausdrückliche Bestätigung.

## Fachlicher Zuschnitt

Das Django-Fachmodul `mobility` ist klassenbezogen. Nur erwachsene aktive Mitglieder mit mindestens einer aktuell verifizierten Sorgeberechtigtenbeziehung dürfen Angebote und Gesuche für `auto`, `bicycle` und `walk` anlegen oder darauf reagieren. Kinderkonten dürfen dies nie.

Ein Eintrag enthält Richtung, Typ, Verkehrsmittel, Wochentage, Zeitfenster, Gültigkeit, groben Startbereich, optionale Kapazität, maximalen Umweg und moderierbaren Hinweis. Sein Lebenszyklus lautet `active`, `paused`, `matched`, `expired`, `withdrawn`; Reaktionen sind `interested`, `seat_offered`, `question`, `accepted`, `declined`, `withdrawn`. Private Rückfragen verweisen auf einen berechtigten Gruppenchat statt auf Telefon oder E-Mail.

Fahrrad- und Laufgruppen besitzen geordnete öffentliche Treffpunkte. Eine PKW-Fahrt kann nach beiderseitiger Annahme eine private `PickupDisclosure` erzeugen. Sie hält Empfänger, Präzision, Zweck, Widerruf, Ablauf und Auditnachweis fest; die Adresse wird nie in Angeboten, Karten, Pushes, Logs oder Adminlisten dupliziert.

## Standort- und Kartenpolicy

| Datenart | Sichtbarkeit | Grenze |
| --- | --- | --- |
| Schule | aktive Klasse | kanonischer Schulstandort |
| Treffpunkt | aktive Klasse | freiwillig gewählter öffentlicher Ort |
| Startbereich | aktive Klasse | gerastert/gerundet, nie Profiladresse |
| Route | aktive Klasse | nur zwischen öffentlichen Punkten und Schule |
| Exakte Abholadresse | nur angenommene Beteiligte | getrennte, widerrufbare Freigabe |
| Live- oder Hintergrundstandort | niemand | nicht implementiert |

Die Karte ist optional; der Listenfallback ist vollständig. Geocoding wird niemals aus Profiladressen vorbefüllt. Ein Kartenanbieter erhält weder Namen, Kontaktdaten noch Adressen; eine selbst gehostete Kartenbasis ist vor dem Realpilot zu entscheiden.

## Bedrohungsanalyse und Gegenmaßnahmen

| Risiko | Schutzmaßnahme | Abnahmetest |
| --- | --- | --- |
| Wohnort-Rückschluss | Rasterbereich/öffentliche Punkte, keine Profilübernahme | Karte, JSON und HTML enthalten keine Adresse |
| IDOR/Klassenwechsel | Query immer an `school_class`, aktive Mitgliedschaft pro Aktion | fremde IDs und entzogener Zugriff liefern 404 |
| Kind vereinbart Fahrt | serverseitige Guardian- und Beziehungsprüfung | Schülerkonto erhält 404/403 bei Schreibwegen |
| Kontaktpreisgabe | Chat statt Kontaktdaten, Disclosure erst nach Annahme | Interessent sieht keine Adresse/E-Mail/Telefon |
| Sperrbildschirm-Leak | neutraler Push ohne Ort, Kind, Route oder Grund | Payload enthält nur Änderung und geschützten Link |
| Doppeltipp/Konkurrenz | POST+CSRF, Idempotenz, Constraint und Transaktion | parallele Annahme bleibt konsistent |
| Missbrauch | Melden, Moderation, Sperren und Audit | Meldung ist nur für Fachmoderation sichtbar |
| Altbestand | Ablaufjob, kontrollierte Löschung | abgelaufene Einträge erscheinen nicht |

Aufrufe sind anonymisiert und dedupliziert: maximal ein Ereignis pro Eintrag, Person und Kalendertag; Selbstaufrufe und Schreibzugriffe zählen nicht. Gerätekennungen, Bewegungsprofile und präzise Standortdaten werden nicht erfasst.

## Berechtigungs- und Moderationsmatrix

| Aktion | Verifizierter Guardian der aktiven Klasse | Beteiligter | Moderator/Klassenadmin |
| --- | --- | --- | --- |
| Angebote/Karte sehen | ja | ja | ja, nur eigene Klasse |
| Eintrag anlegen/ändern | nur eigener | – | bestehende Fachpolicy |
| reagieren | ja, nicht auf eigenen Eintrag | eigener Vorgang | – |
| exakte Adresse sehen | – | nur nach Freigabe | nein, außer selbst beteiligt |
| melden/moderieren | melden | melden | moderieren/sperren |

Alle Änderungen werden minimiert auditiert. Moderatoren erhalten keinen pauschalen Zugriff auf private Disclosures.

## Prüfkatalog

- Die Flüsse aus [Mobilitaet-Wireframes.md](../ux/Mobilitaet-Wireframes.md) funktionieren bei 320 px, ohne Karte und ohne Push.
- Klasse, Mitgliedschaft, Guardian-Status und Besitz werden pro View und Service geprüft.
- Ablauf, Rückzug, Meldung, Moderation und Löschung sind automatisiert getestet.
- Reaktionen, Chat-Links und Pushes geben keine privaten Standort- oder Kontaktdaten preis.
- Jeder Standort- und Disclosure-Widerruf wirkt sofort.
- Der Freigabetext klärt freiwillige Vermittlung sowie die Verantwortung der Erwachsenen für Aufsicht, Versicherung, Fahrerlaubnis und Kindersitze.

## Offene Betriebsentscheidung vor Realpilot

1. Verantwortliche Stelle, Rechtsgrundlage und Löschfristen.
2. Kartenanbieter bzw. selbst gehostete Kartenbasis und Datenflüsse.
3. Versionierter Text für Standort- und Kontaktfreigabe.
4. Moderations- und Eskalationsverantwortliche.
