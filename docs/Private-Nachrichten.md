# Private Nachrichten

Stand: 09.09.2026.

## Zweck und Einstieg

Private Nachrichten verwenden die bestehende Chat-Infrastruktur, erhalten aber
eine eigene, explizite Teilnehmerzuordnung. In der Kontaktkarte wird zuerst die
erwachsene Person ausgewählt. Pro Klasse und Teilnehmerpaar existiert genau eine
Unterhaltung; ein erneuter Start öffnet denselben Verlauf.

## Zugriff

- Nur die zwei zugeordneten persönlichen Konten dürfen den Verlauf, Nachrichten
  und Anhänge lesen oder neue Nachrichten senden.
- Beide Konten müssen weiterhin aktiven Zugang zur betreffenden Klasse haben.
  Ein beendeter oder widerrufener Zugang wirkt beim nächsten Request.
- Portaladministration und Moderation erhalten durch ihre Rolle keinen Zugriff
  auf private Verläufe. Die Chatübersicht und die ungelesene Anzahl enthalten
  nur Unterhaltungen, die das angemeldete Konto tatsächlich öffnen darf.
- Private Nachrichten sind innerhalb des geschützten Portals zugriffsbeschränkt;
  sie sind nicht Ende-zu-Ende-verschlüsselt.

## Hinweise

Die andere Person erhält standardmäßig einen neutralen In-App-Hinweis. Push
wird nur mit aktivierter Kategorie `push_chat` und aktivem Gerät versendet.
Titel und Texte nennen weder Absender, Kind, Nachrichtentext noch Anhang. Das
Klickziel führt direkt in die nur für das Teilnehmerpaar zugängliche Unterhaltung.

## Aufbewahrung, Meldung und Moderation

Private Nachrichten werden nach 180 Tagen automatisch gelöscht. Anhänge folgen
derselben Frist. Eine noch offene Meldung hält die betroffene Nachricht bis zur
menschlichen Prüfung zurück. Die andere Person kann eine Nachricht als
ungeeignet, datenschutzrelevant oder aus einem sonstigen Grund melden.

Moderatoren können private Verläufe nicht durchsuchen. Sie sehen im Django-Admin
nur gemeldete Inhalte und können die ausgewählte Nachricht dort ausblenden und
die Meldung abschließen. Ausgeblendete oder zurückgezogene Texte und Anhänge
werden in den Chatansichten und an den geschützten Anhangsrouten nicht mehr
ausgeliefert. Sicherheitsrelevante Erstellung, Meldung und Moderation werden
ohne Nachrichtentext im Audit festgehalten.

## Abnahmekriterien

- Auswahl einer Person in der Kontaktkarte öffnet idempotent genau einen Verlauf.
- Beide Teilnehmer können schreiben und antworten; gleiche Klassenmitglieder
  sowie Administratoren außerhalb des Teilnehmerpaars erhalten HTTP 404.
- Entzug des Klassenzugangs sperrt den Verlauf unmittelbar.
- In-App- und Push-Hinweise bleiben neutral und gehen nur an die andere Person.
- Meldung, report-basierte Moderation, Inhaltsausblendung und die 180-Tage-Regel
  einschließlich Schutz offener Meldungen sind automatisiert geprüft.
