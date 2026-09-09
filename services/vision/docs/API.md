# Interne API v1

`GET /v1/health` ist der einzige unauthentisierte Endpunkt. Alle übrigen
Endpunkte verlangen `Authorization: Bearer <Diensttoken>`; OpenAPI- und
Dokumentationsrouten sind deaktiviert.

- Modelle: `GET /v1/models`, `GET /v1/models/{pipeline_id}`
- Bildschutz: `POST /v1/safety/images/classify` nimmt ein Bild als Multipart-
  Upload entgegen und antwortet ausschließlich mit `decision`, gepinnter
  Modell-ID und Revision. Rohscores werden nicht ausgegeben oder gespeichert.
- Collections: `POST/GET/DELETE /v1/collections[/{collection_id}]`
- Subjects: `POST /collections/{c}/subjects`, `GET/DELETE .../{subject_id}`
- Bilder: `POST /collections/{c}/images`, `GET/DELETE .../{image_id}`,
  `POST .../{image_id}/analyze` und idempotentes `POST
  .../{image_id}/purge-source` zum isolierten Entfernen der importierten Quelle
  nach der Analyse; geprüfte Ableitungen bleiben bis zu ihrer eigenen Löschung.
- Jobs: `GET .../jobs/{job_id}`, `POST .../jobs/{job_id}/cancel`
- Faces/Matches: Listen, `confirm`, `reject` und `dismiss`
- Referenzen: Anlegen, listen und widerrufen unter dem jeweiligen Subject

IDs sind opaque und validiert. Schreibende Erzeugungs- und Analyseaufrufe
akzeptieren einen `Idempotency-Key`. Analyse ist ein persistierter Job; nach
Neustart werden laufende Jobs kontrolliert erneut eingereiht. Der Dienst ist
für genau eine aktive Instanz ausgelegt.

Die Bildschutzentscheidung lautet `approved` oder `blocked`. Ist das Modell
nicht installiert oder stimmt seine Prüfsumme nicht, antwortet der Dienst mit
HTTP 503; die Django-Anwendung behandelt diesen Zustand vorsorglich wie eine
zu verpixelnde Aufnahme.

Bestätigung und Ablehnung speichern eine opaque `actor_id`. Eine Bestätigung
erzeugt nur mit explizitem `add_as_reference=true` eine neue Referenz. Scores
sind modellabhängige Vergleichswerte, keine Prozentwahrscheinlichkeiten.
