📂 Übersicht der geänderten und neuen Dateien

1. Die Datenbank-Struktur (Erweiterung)
Datei: core/models.py

Was wurde geändert?
In der Klasse Person wurde das Feld gender = models.CharField(max_length=10, choices=GenderType.choices, blank=True, null=True) für das biologische Geschlecht eingefügt.In der Klasse RelationshipType (TextChoices) wurden die Optionen "mother" und "father" entfernt, um die rechtliche Rolle (z. B. Sorgeberechtigt, Pflegeeltern) sauber von der Person zu trennen.
Am ganz linken/unteren Ende der Datei wurde die neue Klasse MenuItem für den dynamischen, unendlich tiefen Aufbau der Navigationshierarchie hinzugefügt.

2. Die API-Logik / Schnittstelle (Neu)
Datei: core/views.py

Was wurde geändert?

Am ganz unteren Ende der Datei wurde die Funktion @login_required @require_GET def get_portal_menu_data(request): hinzugefügt.
Diese Funktion liest die Menüpunkte (MenuItem) und Haushaltsmitglieder (GuardianChildRelationship ➔ student_person) aus und verpackt sie als JSON. Sie enthält integrierte Entwicklungs-Fallbacks (Björn, Mila, Lukas), falls die Tabellen in Staging noch leer sind.

3. Die Adressverwaltung / Routen (Erweiterung)
Datei: klasse5e/urls.py

Was wurde geändert?

In die Liste urlpatterns wurde die Route für den neuen API-Endpunkt eingetragen:path("api/portal-navigation/", views.get_portal_menu_data, name="api_portal_navigation"),Die bestehende Zeile für die Demo-Ansicht wurde so umgeschrieben, dass sie direkt auf unsere neue Hauptdatei verweist (Option 1):path("demo/", TemplateView.as_view(template_name="Navigation.html"), name="demo"),

4. Das HTML5-Frontend / Die Benutzeroberfläche (Neu)
Datei: templates/Navigation.html

Was wurde geändert?

Diese Datei wurde völlig neu angelegt (direkt neben Ihrer base.html).Sie enthält das mobile App-Layout (Sticky-Bottom-Leiste), das JavaScript für das seitliche Hineinschieben der Ebenen, die dynamische Farbcodierung (Lila für Töchter, Grün für Söhne), die Echtzeit-Fotovorschau per FileReader-API sowie das zentrierte, leicht transparente Erfolgs-Toast (Save-Feedback).