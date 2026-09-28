# Rollenrechte im laufenden Portal

Stand: 27.09.2026. Die Prüfung erfolgt lokal mit synthetischen Konten.

## Wirkung der Matrix

Die Seite „Rollenberechtigungen“ steuert zusätzliche Modulrechte für
Hauptadministrator, Content Manager, Redakteur und Moderator. Die zentrale
Auswertung steht in `core/module_permissions.py`. Änderungen wirken beim
nächsten Zugriff; eine erneute Anmeldung ist nicht nötig.

„Sichtbar“ und „Lesen“ sind Voraussetzungen für weitere Aktionen. Die
Voraussetzungen müssen zusammen mit der Aktion von derselben Rolle erfüllt
werden. Mehrere vollständige Rollenzuweisungen ergänzen sich.

Die Matrix ergänzt bestehende Fachrechte. Eine Klassenmitgliedschaft,
verifizierte Eltern-Kind-Beziehung, veranstaltungsbezogene Organisatorenrolle
oder lokale Chatmoderation kann unabhängig davon berechtigen. Ein ausgeschaltetes
Rollenrecht ist deshalb kein allgemeines Verbot für ein Konto. Die Oberfläche
erklärt diese Regel im aufklappbaren Hinweis „So wirken Rollenrechte“.

## Grenzen

- Die Zuweisung begrenzt den Zugriff auf Portal, Schule oder Klasse. Eine
  Plattformfreigabe erweitert keine auf eine Klasse begrenzte Zuweisung.
- Verwaltete Rollen benötigen eine aktuelle Zugehörigkeit zur Zielklasse.
  Die bestehende Ausnahme für Hauptadministratoren gilt bei Plattformrechten.
  Zugehörigkeit kann auch aus einem verifizierten, freigegebenen Kind folgen.
- „Eigene Daten“ benötigt einen ausdrücklich festgestellten Besitzbezug.
  Ohne diesen Bezug wird die Aktion abgewiesen. Bei neuen Objekten ist der
  handelnde Benutzer der Besitzer; bei Galerien der Ersteller, bei Nachrichten
  der Autor, bei Veranstaltungen ein zugeordneter Organisator.
- Gesperrte Konten und deaktivierte Module erhalten keine zusätzlichen Rechte.
- Private Chatverläufe bleiben ihren Teilnehmern vorbehalten. Gemeldete
  Nachrichten verwenden den bestehenden begrenzten Moderationsweg.
- Biometrische Suche benötigt weiterhin Aktivierung und Einwilligungen.
  Persönliche Schulzugänge, Kontaktfreigaben und Abholadressen werden durch
  Rollenrechte nicht freigegeben.
- Andere Fachrollen behalten ihre bisherigen Regeln. Rollenverwaltung und
  technische Superuser-Rechte sind eigenständige Verwaltungsrechte.

## Angeschlossene Aktionen

| Modul | Wirkung |
| --- | --- |
| Chat | Räume erstellen/bearbeiten; Mitglieder verwalten; Räume archivieren/löschen; Nachrichten moderieren; rollenbezogener Lese- und Schreibzugriff |
| Veranstaltungen | Erstellen und Veröffentlichen gemeinsam für neue Veranstaltungen und Terminumfragen; Bearbeiten für bestehende Veranstaltungen und Mitbringlisten; Lesen für Übersichten, Details und Umfragen |
| Kalender | Rollenbezogener Lesezugriff und Bearbeitung manueller Einträge; persönliche Abonnements bleiben an Mitgliedschaft gebunden |
| Galerie | Galerie erstellen und veröffentlichen; Bilder moderieren; zusätzliche Freigabe „Veröffentlichen“ für die Veröffentlichung eines Bildes |
| Photo Memory | Rollenbezogene Suche und Verwaltung innerhalb der bestehenden Einwilligungsregeln |
| Mobilität | Moderation innerhalb des Klassenbereichs; „Eigene Daten“ bezieht sich auf den Ersteller des Angebots |
| PDF-Formulare | Rollenbezogener Zugriff auf Dokumentübersicht und veröffentlichte Dateien |

Der Editor bietet nur Aktionen an, für die es eine entsprechende Fachfunktion
gibt. Persönliche Module erklären ihre eigenen Freigaben, statt wirkungslose
Checkboxen anzubieten. Unzulässige Aktionen werden auch bei direkten
Formularaufrufen zurückgewiesen. Fehlerhafte Formulare verändern keine Rechte.

## Nachweis und Fortsetzung

Die Tests prüfen die tatsächlichen Endpunkte, Entzug und erneute Freigabe,
Klassen- und Schulgrenzen, abgelaufene Mitgliedschaften, private Chats sowie
die unabhängigen Eltern- und Organisatorenrechte. Im Browser wird die Matrix
mit einer Administrationssitzung geändert und die Wirkung in einer zweiten
Benutzersitzung geprüft.

Testzahlen und Abnahmestand stehen in
[Redesign-Abnahme](ux/Redesign-Abnahme-2026-09-25.md).
Der nächste vereinbarte Block ist die vollständige Chat-Funktionsabnahme.
