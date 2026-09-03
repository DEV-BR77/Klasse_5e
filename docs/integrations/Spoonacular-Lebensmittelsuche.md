# Spoonacular-Lebensmittelsuche

KlassID nutzt Spoonacular optional zur Ergänzung der Mitbringliste um einzelne
Lebensmittel. Die Oberfläche sucht keine Rezepte, sondern passende Produkte über
den im APIlayer-Angebot verfügbaren Endpunkt `food/products/search`.

Ohne API-Zugriff stehen lokale deutsche Gruppen wie Obst, Getränke, Saft,
Wurst, Käse, Brot, Brötchen und Gebäck zur Verfügung. Nur Organisatoren können
externe Vorschläge übernehmen. Erst ein CSRF-geschützter POST erzeugt eine
lokale Mitbringposition; doppelte Bezeichnungen werden verhindert.

An Spoonacular wird nur der Suchbegriff übertragen. Eltern-, Kinder-, Klassen-,
Event-, Standort- und Reservierungsdaten werden nicht gesendet. Der Schlüssel
`secret://klasse5e/spoonacular-api-key` wird ausschließlich zur Laufzeit aus
dem lokalen HomeOps-Secretspeicher in den Container gegeben und gehört nicht in
Git oder eine Projekt-`.env`.
