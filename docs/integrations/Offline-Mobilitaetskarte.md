# Lokale Mobilitätskarte

Die Mobilitätsansicht lädt beim Öffnen keine Kartenkacheln, Skripte oder
Schriftarten von externen Anbietern. Die Straßengeometrien im Umkreis von rund
zehn Kilometern um das Theodor-Heuss-Gymnasium werden als reduzierte lokale
JSON-Datei mit dem Anwendungsimage ausgeliefert.

Quelle sind OpenStreetMap-Daten, bereitgestellt unter der Open Database License
(ODbL). Die sichtbare Anwendung nennt deshalb dauerhaft
„© OpenStreetMap-Mitwirkende, ODbL“. Die Quelldaten wurden am 03.09.2026 über
die Overpass API abgerufen und mit `tools/Build-LocalMobilityMap.py` auf die für
die Kartendarstellung erforderlichen Straßengeometrien reduziert.

Die Karte erlaubt die Auswahl eines groben Startbereichs und öffentlicher
Treffpunkte ohne manuelle Koordinateneingabe. Exakte Wohn- oder Abholadressen
werden nicht auf der Karte dargestellt. Private Abholadressen bleiben getrennt,
verschlüsselt, zeitlich befristet und nur für angenommene Beteiligte sichtbar.
