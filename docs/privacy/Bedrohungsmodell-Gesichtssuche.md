# Bedrohungsmodell: Gesichtssuche

## Schutzgüter und Angreifer

Schutzgüter sind Fotos, Gesichtsausschnitte, Embeddings, Zuordnungen, Einwilligungsstatus und Suchergebnisse. Betrachtet werden neugierige Klassenmitglieder, kompromittierte Konten, privilegierte Insider, manipulierte Uploads, Schadsoftware und ein kompromittierter Container.

## Wesentliche Angriffspfade

| Pfad | Abwehr |
|---|---|
| direkte Objekt-ID oder Medien-URL | serverseitige Familien-/Klassenprüfung; keine öffentlichen Rohpfade |
| Aktivierung ohne gültige Zustimmung | globales Gate plus aktuelle Textversion und Zustimmung aller bestätigten Berechtigten |
| bösartiges/übergroßes Bild | Typ-, Größen- und Dekodierungsprüfung, Ressourcenlimits, getrennte Verarbeitung |
| Modell-/Template-Injection | fest versionierte lokale Modelle, keine Nutzereingaben als Code, Integritätsprüfung |
| Extraktion über viele Suchanfragen | engste Empfängergruppe, Rate-Limit, minimiertes Audit, keine Rohvektorausgabe |
| Secret-/Datenabfluss über Logs | strukturierte Redaktion; niemals Fotos, Embeddings, Passwörter oder Sitzungen protokollieren |
| Wiederauftauchen nach Löschung | Tombstone/Wiederherstellungsprüfung und rotierende Backups |

## Annahmen und Grenzen

Containertrennung allein ist keine Sicherheitsgrenze gegen Host-Administratoren. Biometrische Merkmale sind nicht wie Passwörter austauschbar. Daher wird das Restrisiko nicht als „null“ dargestellt; bei ungeklärter Organisation oder Sicherheitsabweichung ist Abschalten die Standardreaktion.
