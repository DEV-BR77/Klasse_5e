# Lizenzanfrage für InsightFace-Modelle

Stand: 26.08.2026

## Versand

Die Anfrage wurde gestellt an:

- `recognition-oss-pack@insightface.ai`

**Subject:** Non-commercial model license request for a private self-hosted school-class photo platform

```
Dear InsightFace Licensing Team,

I am developing a small, private, non-commercial, self-hosted web platform for
the parents and teachers of a single school class in Germany.

The platform will include a protected photo gallery for class events such as
school trips. We would like to evaluate and potentially use an InsightFace face
detection and recognition model to help parents find photographs containing
their own child within the platform's protected area.

We are particularly interested in evaluating the following models or model
combinations:

- SCRFD with an ArcFace-based recognition model
- the buffalo_l model package
- optionally antelopev2 as an additional quality comparison

The intended use is limited as follows:

- use for one school class only
- approximately 25 to 35 children, their parents and two teachers
- no commercial use
- no subscription fees, advertising or other monetisation
- no sale or redistribution of the software or model weights
- deployment exclusively on a privately managed, self-hosted server
- no cloud-based face recognition
- no transfer of photographs or biometric comparison data to external providers
- no public API and no public photo gallery
- access restricted to authorised members of the class
- human review and confirmation of every suggested match
- no fully automated final identification
- separate and explicit consent for biometric face matching
- complete deletion of reference images, embeddings and assignments after consent is withdrawn
- parents may search only for photographs of their own children linked to their account
- an expected workload of approximately 100 photographs per school event, processed occasionally in batches

The software would store face embeddings and confirmed reference images only
locally and only for as long as they are required for the stated purpose and
the relevant consent remains valid. We are requesting permission that is not
limited to a single school year, but remains valid for the lifetime of this
specific class cohort, beginning in grade 5 and ending no later than graduation
or the end of grade 13, so that a new application is not required every year.
Individual withdrawal and deletion obligations would remain unaffected.

The models would be executed locally on a CPU using ONNX Runtime. We may convert
the models into an optimised or quantised ONNX representation for local
inference. The model weights would not be made available to third parties.

Could you please answer the following questions:

1. Is this private and non-commercial, but operational, use already permitted
   under the existing model licence?
2. If not, could you grant us written non-commercial permission or an
   appropriate licence for this specific use case?
3. Could this permission cover the buffalo_l model package, including its
   SCRFD detector and ArcFace-based recognition model?
4. Could antelopev2 also be included solely for a local quality comparison?
5. Is conversion or optimisation of the supplied model weights into another
   ONNX representation for local inference permitted?
6. May the models be used in a private Docker deployment, provided that the
   Docker image and model weights are not published or redistributed?
7. Are there any specific attribution, documentation, audit, privacy or
   deletion requirements that we must follow?
8. Could the permission remain valid, without annual reapplication, for the
   lifetime of this class cohort, beginning in grade 5 and ending no later than
   graduation or the end of grade 13? Would it otherwise be time-limited or
   restricted to specific model versions?

This is a parent-operated project and is currently neither a commercial product
nor an official product of the school.

I would be happy to provide further technical or organisational information if
required.

Please also let us know whether a no-cost non-commercial licence is available
for this strictly limited private use and which licence documents or licence
files we would need to retain.

Kind regards,

Bjoern Radke
Germany
```

## Deutsche Fassung

**Betreff:** Anfrage zur nichtkommerziellen Modelllizenz für eine private, selbst gehostete Klassenplattform

```
Sehr geehrtes InsightFace-Lizenzteam,

ich entwickle eine kleine, private und nichtkommerzielle, selbst gehostete
Webplattform für die Eltern und Klassenlehrer einer einzelnen Schulklasse
in Deutschland.

Die Plattform soll unter anderem eine geschützte Fotogalerie für
Klassenveranstaltungen wie Ausflüge und Klassenfahrten enthalten. Wir möchten
ein InsightFace-Modell zur Gesichtserkennung und zum Gesichtsvergleich
evaluieren und möglicherweise einsetzen. Damit sollen Eltern innerhalb des
geschützten Bereichs Fotos finden können, auf denen ihr eigenes Kind abgebildet
ist.

Wir interessieren uns insbesondere für folgende Modelle beziehungsweise
Modellkombinationen:

- SCRFD mit einem ArcFace-basierten Erkennungsmodell
- das Modellpaket buffalo_l
- optional antelopev2 als zusätzlicher Qualitätsvergleich

Der geplante Einsatz ist wie folgt begrenzt:

- Nutzung für genau eine Schulklasse
- ungefähr 25 bis 35 Kinder, deren Eltern und zwei Klassenlehrer
- keine kommerzielle Nutzung
- keine Abonnements, Werbung oder sonstige Monetarisierung
- kein Verkauf und keine Weitergabe der Software oder Modellgewichte
- Betrieb ausschließlich auf einem privat verwalteten, selbst gehosteten Server
- keine cloudbasierte Gesichtserkennung
- keine Übermittlung von Fotos oder biometrischen Vergleichsdaten an externe Anbieter
- keine öffentliche API und keine öffentliche Fotogalerie
- Zugriff ausschließlich für autorisierte Mitglieder der Klasse
- menschliche Prüfung und Bestätigung jedes vorgeschlagenen Treffers
- keine vollautomatische endgültige Identifikation
- separate und ausdrückliche Einwilligung zur biometrischen Gesichtssuche
- vollständige Löschung von Referenzbildern, Embeddings und Zuordnungen bei einem Widerruf
- Eltern dürfen ausschließlich nach Bildern ihrer eigenen, mit ihrem Konto verknüpften Kinder suchen
- ungefähr 100 Fotos pro Schulveranstaltung, die gelegentlich als Stapel verarbeitet werden

Die Software würde Gesichtsembeddings und bestätigte Referenzbilder
ausschließlich lokal und nur so lange speichern, wie sie für den beschriebenen
Zweck benötigt werden und die jeweilige Einwilligung fortbesteht. Die erbetene
Nutzungserlaubnis soll nicht auf ein einzelnes Schuljahr beschränkt sein,
sondern für die Dauer des bestehenden Klassenverbands gelten: beginnend in
Klassenstufe 5 und längstens bis zum Abschluss beziehungsweise Ende der
Klassenstufe 13. Damit soll keine jährliche Neubeantragung erforderlich sein.
Individuelle Widerrufs- und Löschpflichten bleiben davon unberührt.

Die Modelle sollen lokal mit ONNX Runtime auf einer CPU ausgeführt werden.
Möglicherweise würden die Modelle für diesen lokalen Betrieb in eine optimierte
oder quantisierte ONNX-Darstellung konvertiert. Die Modellgewichte würden nicht
an Dritte weitergegeben.

Könnten Sie uns bitte folgende Fragen beantworten:

1. Ist diese private, nichtkommerzielle, aber operative Nutzung bereits durch
   die bestehende Modelllizenz erlaubt?
2. Falls nicht: Können Sie uns für diesen konkreten Verwendungszweck eine
   schriftliche nichtkommerzielle Nutzungserlaubnis oder eine entsprechende
   Lizenz erteilen?
3. Kann die Erlaubnis das Modellpaket buffalo_l einschließlich des
   SCRFD-Detektors und des ArcFace-basierten Erkennungsmodells umfassen?
4. Kann antelopev2 zusätzlich für einen ausschließlich lokalen
   Qualitätsvergleich einbezogen werden?
5. Ist die Konvertierung oder Optimierung der bereitgestellten Modellgewichte
   in eine andere ONNX-Darstellung für die lokale Ausführung zulässig?
6. Dürfen die Modelle in einem privaten Docker-Deployment verwendet werden,
   sofern das Docker-Image und die Modellgewichte nicht veröffentlicht oder
   weitergegeben werden?
7. Bestehen besondere Anforderungen an Namensnennung, Dokumentation,
   Protokollierung, Datenschutz oder Löschung?
8. Kann die Erlaubnis ohne jährliche Neubeantragung für die gesamte Dauer des
   Klassenverbands – ab Klassenstufe 5 und längstens bis zum Abschluss
   beziehungsweise Ende der Klassenstufe 13 – gelten? Ist sie darüber hinaus
   zeitlich begrenzt oder an bestimmte Modellversionen gebunden?

Es handelt sich um ein von Eltern betriebenes Projekt und derzeit nicht um ein
kommerzielles Produkt oder ein offizielles Produkt der Schule.

Gerne stelle ich Ihnen bei Bedarf weitere technische oder organisatorische
Informationen zur Verfügung.

Bitte teilen Sie uns auch mit, ob für diesen stark begrenzten privaten
Verwendungszweck eine kostenfreie nichtkommerzielle Lizenz möglich ist und
welche Lizenzdokumente oder Lizenzdateien wir dafür aufbewahren müssen.

Mit freundlichen Grüßen

Bjoern Radke
Deutschland
```

Solange keine belastbare Erlaubnis erteilt wird, dürfen die betreffenden
InsightFace-Modellgewichte nicht produktiv verwendet werden. Adapter dürfen
vorbereitet werden; Modellgewichte, echte Klassenfotos und biometrische Daten
dürfen ohne geklärte Lizenz nicht eingesetzt werden.


## Nachverfolgung

Antwort von Insight noch offen.
