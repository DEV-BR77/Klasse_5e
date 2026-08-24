# Projekt Klasse 5e

## Ziel

Klasse 5e wird eine geschlossene, einladungsbasierte und selbst gehostete PWA
für genau eine Klasse. Sie soll für Eltern und Lehrkräfte auf Mobiltelefonen
einfach nutzbar und für einen privaten Betreiber sicher zu aktualisieren, zu
sichern und wiederherzustellen sein.

## Leitplanken

- Keine öffentliche Registrierung, Werbung, Tracker oder Cloud-KI.
- Personenbezogene Felder sind standardmäßig nicht sichtbar.
- Aktive Klassenmitgliedschaft wird bei jedem geschützten Zugriff geprüft.
- Foto- und biometrische Einwilligungen bleiben getrennt, freiwillig,
  versioniert und widerrufbar.
- Keine automatische endgültige Personenzuordnung durch ein Modell.
- Keine Microservices für Fachmodule des Klassenportals.
- Keine Vorwegnahme späterer Phasen.

## Kleinste sinnvolle erste Version

Das MVP endet nach **Phase 3** und umfasst:

1. Einladungslogin, verpflichtende starke Anmeldung für Administratoren,
   Rollen, Schuljahr und aktive Klassenmitgliedschaft.
2. Familien-, Sorgeberechtigten- und Kinderprofile mit versionierten,
   getrennten Einwilligungen und Audit-Protokoll.
3. installierbare PWA mit persönlichem Dashboard.
4. geschütztes Dokumentencenter, Lehrerübersicht und einfache Beiträge mit
   moderierbaren Kommentaren.
5. PostgreSQL, lokale geschützte Medien, Docker Compose, Caddy-Anbindung sowie
   dokumentierter Backup-/Restore-Grundweg.

Web Push und Vision werden vorher als technische Bausteine vorbereitet, sind
aber im MVP nur soweit eingebunden, wie eine freigegebene Fachphase es
erfordert. Events, Galerien, biometrische Suche, Chat, Kalender und
Schulportal-Integration sind nicht Teil dieses MVP.

## Qualitäts- und Sicherheitsnachweis je Umsetzungsphase

Jede Phase liefert einen begrenzten Umfang, Datenmodell oder Schnittstellen,
Implementierung, automatisierte Tests, Sicherheitsprüfung, kurze
Betriebsdokumentation und überprüfbare Abnahmekriterien. Sicherheitskritische
Tests umfassen insbesondere Rollen, Klassenisolation, Widerruf und geschützte
Dateiauslieferung.

## Phase-0-Abnahme

- [x] Sechs vorgegebene Projektbestände wurden untersucht.
- [x] Wiederverwendbares und neu zu Bauendes ist getrennt dokumentiert.
- [x] Push und Vision besitzen getrennte Architekturentscheidungen.
- [x] Modulgrenzen und zulässige Abhängigkeiten sind festgelegt.
- [x] Spätere Module sind geplant, aber nicht implementiert.
- [x] MVP und relative Komplexität sind benannt.
- [x] Es wurde kein Anwendungs- oder Microservice-Scaffolding erzeugt.
- [x] Fremde Repositories und vorhandene Benutzeränderungen blieben unangetastet.

