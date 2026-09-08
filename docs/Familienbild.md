# Familienbild auf der Kontaktkarte

Ein Haushalt kann für eine Klasse optional ein Familienbild hinterlegen. Beim
Upload werden genau die darauf abgebildeten Personen ausgewählt. Das Bild wird
nur gespeichert, wenn für jede ausgewählte Person die aktuelle Einwilligung
`photo_gallery` wirksam ist. Erwachsene verwalten ihre eigene Foto-Freigabe in
der Familien-Zentrale; für Kinder gelten weiterhin die bestehenden
vertretungsberechtigten Sorgebeziehungen.

Die Bilddatei wird beim Upload neu als WebP gespeichert und nur durch die
geschützte Django-Ansicht ausgeliefert. Sie prüft aktive Klassenmitgliedschaft
und die aktuelle Einwilligung bei jedem Aufruf. Ein Widerruf oder der Verlust
einer erforderlichen Beziehung blendet das Bild deshalb sofort aus; es bleibt
bis zum bewussten Entfernen durch eine berechtigte Familienperson nicht in der
Kontaktliste sichtbar.

Die Kontaktkarte zeigt bei keinem hinterlegten oder keinem mehr zulässigen Bild
einen Kreis mit den Initialen des Familiennamens. Das Familienbild kann in der
Familien-Zentrale ersetzt oder entfernt werden. Die Abläufe sind mit
`test_family_photos.py` für vollständige Einwilligung, geschützte
Auslieferung, Widerruf und den Initialen-Ersatz getestet.
