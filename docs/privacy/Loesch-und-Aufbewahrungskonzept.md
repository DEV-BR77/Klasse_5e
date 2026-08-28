# Lösch- und Aufbewahrungskonzept

Fristen sind Maximalwerte des Betriebsentwurfs und vor Pilot rechtlich/organisatorisch freizugeben.

| Datenklasse | Regelereignis | Ziel |
|---|---|---|
| Sitzungen/temporäre Tokens | Logout/Ablauf | sofort bzw. technische Kurzfrist |
| Push-Endpunkt | Abmeldung, Widerruf, Ungültigkeit | unverzüglich |
| WebUntis-Sitzung/Klartextzugang | Ende eines Abrufs | sofort aus Arbeitsspeicher; nie protokollieren |
| verschlüsselter WebUntis-Zugang | Entfernung/Beziehungsende | unverzüglich |
| Biometrieprofil/Ausschnitt/Embedding | Widerruf/Profilende | unverzüglich sperren, nächster kontrollierter Löschlauf |
| Fotos/Dokumente/Inhalte | Löschentscheidung/Zweckende | aus aktiver Ablage entfernen; Ableitungen einschließen |
| Konto/Person/Beziehung | bestätigtes Ende nach Prüfung abhängiger Pflichten | löschen oder irreversibel anonymisieren |
| Einwilligungs-/Auditnachweis | Ende notwendiger Nachweisfrist | minimiert sperren, anschließend löschen/anonymisieren |
| Backups | reguläre Rotation | gelöschte Daten nicht reaktivieren; nach Rotationsfrist verschwunden |

Jeder Löschauftrag ist idempotent, berechtigungsgeprüft und erfasst abhängige Vorschaubilder, Suchindizes, Exporte und technische Caches. Legal Holds sind Ausnahmefälle, benötigen dokumentierten Grund, Umfang, Freigabe und Enddatum.
