# Rollen und Elternvertretung

Nur Haupt- und stellvertretende Portal-Admins können unter
`/verwaltung/rollen/` weitere Portal-Admins bestimmen oder entziehen. Die
delegierte Portal-Admin-Rolle gilt portalweit und unterliegt der bestehenden
Zwei-Faktor-Anmeldung.

Elternvertretungen werden je Klasse vergeben. Die Verwaltungsansicht akzeptiert
nur aktive, bestätigte Sorgeberechtigte mit gültigem Sichtrecht für ein Kind in
der gewählten Klasse. Ein Entzug sperrt den Zugang sofort.

Ein Chatraum mit dem Zugriff „Nur Elternvertretung“ prüft diese klassenbezogene
Rolle bei jedem Zugriff serverseitig. Für jede Nachricht erhalten die anderen
aktiven Elternvertretungen derselben Klasse einen persönlichen Hinweis in der
Glocke; Web-Push wird dabei nicht automatisch aktiviert.
