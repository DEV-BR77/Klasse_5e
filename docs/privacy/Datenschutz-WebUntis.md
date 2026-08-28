# Datenschutz: WebUntis-Anbindung

Die Anbindung ist eine freiwillige Komfortfunktion. Sie spricht ausschließlich den fest erlaubten Host `thgwob.webuntis.com` an, läuft im Django-Prozess ohne MCP-/Claude-Laufzeit und wird nur durch „Aktuell prüfen“ ausgelöst. Funktionskategorien sind einzeln und standardmäßig deaktiviert.

Zugangsdaten werden mit Fernet verschlüsselt gespeichert; Schlüssel und Klartextwerte liegen außerhalb von Git. Sitzungskennungen werden nach dem Abruf verworfen und nie protokolliert. Nur eine bestätigte Sorgeberechtigten-Kind-Beziehung mit passendem Verwaltungsrecht darf einen Zugang verbinden oder verwenden. Idempotency-Key, Sperre und Fehlerklassen verhindern doppelte oder unkontrollierte Läufe.

Je aktivierter Kategorie können Stundenplan-, Hausaufgaben-, Prüfungs- oder Abwesenheitsdaten betroffen sein. Der Pilot speichert keine produktiven Antworten dauerhaft. Eine spätere Speicherung braucht eine eigene Zweck-, Frist- und Empfängerfreigabe. Widerruf deaktiviert die Kategorie; auf Wunsch wird der verschlüsselte Zugang vollständig entfernt.
