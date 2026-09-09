# Kinderschutz im Chat

Direkte deutsche Beleidigungen werden beim Senden und Bearbeiten serverseitig
mit Punkten maskiert. Die Liste bleibt absichtlich klein und im Quellcode
prüfbar. Groß-/Kleinschreibung, gebräuchliche Ziffernersetzungen und eingefügte
Trennzeichen werden berücksichtigt; Wortteile harmloser Begriffe bleiben
unangetastet. Der Auditdatensatz enthält nur die Anzahl der Treffer und niemals
den Klartext.

`profanity-check` 1.0.3 wurde geprüft und nicht eingebunden. Das Paket ist auf
englische Texte ausgerichtet, seit August 2019 nicht veröffentlicht worden und
mit dem aktuellen Python-3.12-/scikit-learn-Stack nicht lauffähig. Eine alte,
englische Pickle-Datei wäre für den deutschen Klassenchat weder zuverlässig
noch wartbar. Flask und Flask-SocketIO werden ebenfalls nicht eingeführt: Der
bestehende Django-Chat mit Polling bleibt gemäß ADR-020 maßgeblich.

## Bilder

Bildanhänge werden lokal und intern authentisiert mit
`Falconsai/nsfw_image_detection` klassifiziert. Das Modell ist auf Revision
`96cb0d0342c7afb80cab76ecc58b265fa44da256` festgelegt. Gewichte werden getrennt
vom Repository im Modellvolume gespeichert und vor dem Laden per SHA-256
geprüft. Der Vision-Endpunkt gibt keinen Rohscore aus.

Vor Speicherung werden unterstützte Bildformate serverseitig dekodiert, nach
EXIF-Ausrichtung gedreht und als JPEG neu codiert. So gelangen weder EXIF-
Metadaten noch aktive oder formatfremde Dateiinhalte in die Auslieferung.

Bei `blocked`, einem Timeout oder einem nicht verfügbaren Modell zeigt der Chat
eine neu codierte, stark verpixelte JPEG-Fassung. Die Nachricht und der Anhang
werden dabei nicht abgewiesen und nicht automatisch einer Prüfung vorgelegt.
Nur bei `approved` wird nach erneuter Mitgliedschaftsprüfung das Original
ausgeliefert. Der sichtbare Hinweis erklärt die Verpixelung. Mitglieder können
eine Nachricht weiterhin bewusst über den normalen Meldeweg melden.

## Abnahme

- deutsche direkte Beleidigungen sowie einfache Schreibumgehungen werden
  vollständig maskiert, harmlose Wortteile nicht;
- neue und bearbeitete Nachrichten verwenden dieselbe Filterung;
- problematische und technisch ungeprüfte Bilder werden ausgeliefert, aber nur
  als verpixelte Ableitung;
- das Original bleibt über die normale Anhangroute unzugänglich, solange keine
  unauffällige Modellentscheidung vorliegt;
- Modellantwort, Audit und Logs enthalten weder Rohscore noch Klartext oder
  Bilddaten;
- Klassen- und Mitgliedschaftsprüfung gelten bei jedem Abruf erneut.
