# Klassenchat

Phase 7 stellt einen bewusst kleinen, geschlossenen Textchat bereit. Räume
gehören genau einer Klasse und einem Schuljahr; optional kann ein Raum einem
Event derselben Klasse zugeordnet sein. Jeder Abruf und jede Änderung prüft die
aktuelle Klassenmitgliedschaft. Direktnachrichten, Anhänge, Audio/Video,
Federation und Ende-zu-Ende-Verschlüsselung gehören nicht zum Umfang.

Die Oberfläche kann `GET /chat/rooms/<opaque-id>/messages/?since=<timestamp>`
kurz pollen. Dadurch werden weder Redis noch WebSockets benötigt. Nachrichten
können beantwortet, vom Autor bearbeitet oder inhaltsleer zurückgezogen,
gemeldet und durch Moderatoren ausgeblendet werden.

Die Standardaufbewahrung beträgt 90 Tage. `manage.py purge_chat` zeigt nur die
Anzahl; erst `--execute` löscht. Push ist pro Raum opt-in. Ein Versand darf nur
einen neutralen Hinweis und einen Login-geschützten Link enthalten, nie den
vollständigen Nachrichtentext. Zustellung ist nicht garantiert.
