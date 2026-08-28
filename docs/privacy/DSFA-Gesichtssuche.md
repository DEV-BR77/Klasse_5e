# Datenschutz-Folgenabschätzung: Gesichtssuche

Status: technische Fassung, organisatorisch/rechtlich vor Aktivierung zu genehmigen.

## Beschreibung und Notwendigkeit

Aus einem freiwillig bereitgestellten Referenzfoto wird lokal ein biometrischer Merkmalsvektor erstellt. Dieser wird ausschließlich gegen Bilder in der geschützten Klassengalerie verglichen, um einem eng berechtigten Familienkreis Vorschläge zu zeigen. Der Zweck lässt sich auch durch manuelles Durchsehen erreichen; die Funktion ist daher Komfortfunktion, nie Voraussetzung.

## Verhältnismäßigkeit

Getrennte ausdrückliche Einwilligung, standardmäßig deaktivierte Schalter, lokale Verarbeitung, Zweckbindung, beschränkte Empfänger, Widerruf und kurze Löschwege reduzieren den Eingriff. Zustimmung aller aktuell verwaltungsberechtigten Sorgeberechtigten ist erforderlich. Die kindliche Perspektive wird verständlich erklärt und ein Widerspruch respektiert.

## Risiken und Maßnahmen

| Risiko | Eintritt/Auswirkung | Maßnahmen | Restrisiko |
|---|---|---|---|
| Fehlzuordnung | mittel/hoch | nur Vorschläge, Schwellenwert, keine automatische Veröffentlichung oder Entscheidung | mittel |
| unbefugter Zugriff | niedrig/hoch | Klassen-/Familienprüfung, private Medienauslieferung, MFA für privilegierte Rollen, Audit | niedrig–mittel |
| Modell-/Embedding-Abfluss | niedrig/hoch | lokaler Dienst, keine Secrets/Embeddings in Logs oder Git, getrennte Volumes, Verschlüsselung/Backupschutz | niedrig–mittel |
| Zweckausweitung | mittel/hoch | fest codierter Zweck, keine Anwesenheits-/Verhaltensnutzung, Änderungs- und DSFA-Gate | niedrig–mittel |
| unwirksame Einwilligung | mittel/hoch | granulare Version, alle Berechtigten, leicht erreichbarer Widerruf, kindgerechter Text | mittel |
| Restdaten nach Widerruf | mittel/hoch | synchrone Sperre, Löschauftrag für Profil/Ausschnitt/Embedding, Wiederherstellungssperre | niedrig–mittel |

## Freigabekriterien

Verantwortlichkeit und Rechtsgrundlage sind beschlossen; Einwilligungstexte und Altersmodell geprüft; Penetrations-/Berechtigungstest bestanden; Löschlauf inklusive Backup-Wiederherstellung getestet; Verantwortliche Person akzeptiert Restrisiko schriftlich. Vorher bleibt die Funktion aus.
