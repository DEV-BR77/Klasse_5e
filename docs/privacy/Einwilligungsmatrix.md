# Einwilligungsmatrix

Alle optionalen Zwecke sind standardmäßig aus. Ein globaler Sammelschalter ist unzulässig.

| Schlüssel | Zweck | Betroffene Person | Erforderliche Entscheidung | Widerrufsfolge |
|---|---|---|---|---|
| `profile_contact_visibility` | Kontaktangaben in der Klasse zeigen | Erwachsene/Schüler | selbst bzw. alle aktuell verwaltungsberechtigten Sorgeberechtigten | Felder sofort verbergen |
| `photo_gallery` | erkennbare Fotos in geschützter Galerie | abgebildete Person | selbst bzw. alle berechtigten Sorgeberechtigten | neue Anzeige stoppen, Löschprüfung starten |
| `biometric_face_search` | biometrische Suche in privaten Galerien | abgebildeter Schüler | alle berechtigten Sorgeberechtigten; zusätzlich altersangemessene Beteiligung | Profil, Ausschnitte und Embeddings löschen |
| `push_general` | allgemeine Portal-Benachrichtigungen | Kontoinhaber | selbst | Kategorie und Endpunkt deaktivieren |
| `push_chat` | Benachrichtigung über Chats | Kontoinhaber | selbst | Kategorie deaktivieren |
| `push_events` | Erinnerungen an Termine | Kontoinhaber | selbst | Kategorie deaktivieren |
| `webuntis_timetable` | Stundenplan manuell abrufen | Schüler | alle dafür berechtigten bestätigten Sorgeberechtigten | Funktion aus, Zugang optional entfernen |
| `webuntis_homework` | Hausaufgaben manuell abrufen | Schüler | wie vor | Funktion aus |
| `webuntis_exams` | Prüfungen manuell abrufen | Schüler | wie vor | Funktion aus |
| `webuntis_absences` | Abwesenheiten manuell abrufen | Schüler | wie vor | Funktion aus |

Konflikte werden konservativ gelöst: Eine aktuelle Ablehnung oder fehlende aktuelle Entscheidung einer verwaltungsberechtigten Person hält die Funktion aus. Nur bestätigte, nicht widerrufene Beziehungen zählen. Entscheidungen bleiben je Zweck und Textversion nachvollziehbar.
