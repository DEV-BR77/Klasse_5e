# Reproduzierbares Evaluationsgerüst

Das Gerüst misst je Pipeline Detection-Recall/-Precision, übersehene und falsche
Faces, Top-1/Top-3, falsche Top-1, fehlende Vorschläge und den Rang der richtigen
Person. Betriebswerte sind Zeit pro Bild und 100 Bilder, Spitzen-RSS,
CPU-Auslastung, Startzeit und Modellgröße.

Manifestierte Fixtures beschreiben Quelle, Lizenz, erwartete Boxes/Subjects und
Szenario: Einzelporträt, Gruppe, kleines/seitliches Gesicht, Brille,
Verdeckung, Licht, Unschärfe und – nur bei rechtmäßigem Material – Aufnahmejahr.
Ohne geeigneten Datensatz werden Kennzahlen als `not_measured` ausgegeben;
öffentliche Benchmarkwerte werden nicht als eigene Messung dargestellt.

In Phase 1B werden keine Klassen- oder Kinderfotos verwendet. Schwellenwerte
sind nicht kalibriert. Der Vergleich ist ein Kandidatenranking und niemals eine
automatische Identifikation.
