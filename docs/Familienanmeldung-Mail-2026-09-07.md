# Familienanmeldung und E-Mail-Versand (07.09.2026)

## Fehler und Korrektur

Die laufende Anwendung nutzte Djangos SMTP-Standard `localhost:25` ohne
Zugangsdaten. Die lokale Arbeitskopie enthielt zusätzlich einen Console-Mail-
Override und deaktivierte E-Mail-Verifikation. Diese beiden lokalen Overrides
wurden im Rahmen der Versandkorrektur entfernt; andere Benutzeränderungen
bleiben erhalten.

Der Versand verwendet jetzt Djangos SMTP-Backend mit `smtp.resend.com:587`,
STARTTLS, Benutzer `resend`, 15 Sekunden Timeout und `RESEND_API_KEY` aus dem
HomeOps-Speicher `secret://providers/resend/klassid_api_key`. Das Deployment
fordert diesen Schlüssel ausdrücklich an; er gehört niemals in Git oder `.env`.
Quelle: https://resend.com/docs/send-with-django-smtp

Die zweite erwachsene Person erhält ein eigenes Passwortfeld. Serverseitig
werden Vollständigkeit, Passwortstärke, E-Mail-Format und vorhandene Zugänge
geprüft. Die bisher fehlenden Django-Passwortvalidatoren sind jetzt aktiviert
(mindestens 12 Zeichen, keine verbreiteten oder rein numerischen Passwörter). Gespeichert wird nur ein Django-Passworthash. Nach administrativer
Freigabe und Aktivierung der ersten Person erhält die zweite Person weiterhin
einen persönlichen E-Mail-Link. Erst dessen Bestätigung aktiviert ihren Zugang.
Die Einladung ist transaktionssicher und einmalig; der temporäre Hash wird danach
entfernt. Ältere Einladungen ohne vorbereitetes Passwort bleiben nutzbar.

Ein SMTP-Fehler oder Versandresultat 0 rollt den Familienantrag inklusive Kindern
und Code-Verbrauch zurück. Im Formular werden keine Passwörter erneut ausgegeben.
Fehlerlogs enthalten nur die Fehlerklasse, keine SMTP-Antworten oder Zugangsdaten.

## Betrieb und Abnahme

- SMTP-Erreichbarkeit mit verifiziertem TLS aus dem produktiven Container bestätigt.
- Familien- und Identitätsprüfungen inklusive zwei Erwachsenen/zwei Kindern,
  Hash-Verwendung, separater E-Mail-Bestätigung und Wiederholung nach Versandfehler
  automatisiert getestet.
- SMTP-Anmeldung prüfen: `python manage.py check_email`.
- Bewusste Testmail: `python manage.py check_email --recipient <eigene-adresse>`.
- Der Befehl bestätigt nur die Annahme beim Versanddienst. Zustellung im Postfach
  beziehungsweise Resend-Zustellstatus zusätzlich prüfen.
- Ausstehend: KlassID-Schlüssel mit Sending-Zugriff ausschließlich auf `klassid.de`
  in Resend erzeugen, im HomeOps-Speicher sichern, deployen und echte Testmail senden.
  Die Browsersteuerung wurde beim Erstellen des Schlüssels automatisch gestoppt.
- Keine Schemaänderung oder Datenmigration erforderlich. Noch nicht produktiv ausgerollt.
