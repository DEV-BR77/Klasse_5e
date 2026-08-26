# Lokale Personensuche – Phase 6

## Freigabe und Zweck

Verantwortliche Stelle ist **Björn Radke**. Freigegeben ist ausschließlich die
Entwicklung und technische Prüfung einer lokalen, einwilligungsbasierten Suche
in freigegebenen Testbildern. Eine Produktivfreigabe oder Verarbeitung echter
Klassenfotos ist damit nicht verbunden.

## Ablauf und Grenzen

Die Galerie muss das bereinigte Foto einzeln zur biometrischen Analyse
freigeben. Für jeden `StudentProfile` müssen alle aktuellen, verifizierten und
biometrieberechtigten Sorgeberechtigten derselben versionierten Biometrie-
Einwilligung zugestimmt haben. Danach erzeugt die App opaque Collection-,
Subject-, Image- und Actor-UUIDs. Namen verlassen die App nicht.

Vision liefert nur Vorschläge. Ein Moderator bestätigt oder verwirft sie; nur
bestätigte Zuordnungen erscheinen. Die Aufnahme als neue Referenz ist separat,
explizit und erfordert die Consent-Art `confirmed-match-reference`. Eltern
suchen ausschließlich nach eigenen verknüpften Kindern. Personen ohne
Einwilligung behalten alle nicht-biometrischen Plattformfunktionen.

## Löschung

- importierte Vision-Quelldatei: binnen 24 Stunden nach Embedding-Prüfung, bei
  dokumentierter manueller Prüfung spätestens nach sieben Tagen;
- Embeddings und Referenzen: binnen 24 Stunden nach Widerruf, Profillöschung,
  Testende oder Abschaltung;
- Zuordnungs- und Protokolldaten: binnen 30 Tagen nach Testende;
- minimierte sicherheitsrelevante Auditdaten: höchstens 90 Tage.

Widerruf sperrt das Profil zuerst lokal und löscht danach das opaque Subject in
Vision; dort fallen Referenzen und Embeddings mit weg. Lokale Treffer werden
gelöscht. Das Galeriefoto folgt unabhängig der separaten Fotoeinwilligung.
Fehlgeschlagene Remote-Löschung bleibt sichtbar als `deletion_pending` und wird
vom Reconcile-Befehl wiederholt.

## Transparenztext

> Die Bilderkennung läuft ausschließlich auf dem selbst betriebenen Server.
> Fotos, Gesichtsausschnitte und biometrische Vergleichsdaten werden nicht an
> externe KI-Anbieter übertragen. Die KI erstellt nur Vorschläge.
> Personenzuordnungen werden durch berechtigte Personen bestätigt.

„Lokal“ bedeutet im selbst betriebenen Vision-Container, nicht auf dem Endgerät.
Die Qualität ist nicht garantiert; Schwellenwerte sind keine Prozente. Der
InsightFace-Adapter bleibt mangels schriftlicher Gewichtsfreigabe deaktiviert.
