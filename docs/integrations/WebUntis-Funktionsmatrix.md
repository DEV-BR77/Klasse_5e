# WebUntis-Funktionsmatrix (anonymisiert)

| Bereich | Technischer Aufruf | Sichtbarkeit | Status im Pilot |
|---|---|---|---|
| Kinder | REST `/api/rest/view/v1/app/data` | eigenes Elternkonto | noch nicht geprüft |
| Stundenplan | RPC `getTimetable` | persönliches Kind | verfügbar, Berechtigung prüfen |
| Erweiterter Stundenplan | REST `/api/public/timetable/weekly/data` | persönliches Kind | noch nicht geprüft |
| Vertretungen | RPC `getSubstitutions` | klassenweit, minimiert | verfügbar, Berechtigung prüfen |
| Hausaufgaben | REST `/api/homeworks/lessons` | persönliches Kind | noch nicht geprüft |
| Prüfungen | REST `/api/exams` | freigegebener Klassen-/Kindbezug | noch nicht geprüft |
| Fehlzeiten | REST `/api/classreg/absences/students` | nur Sorgeberechtigte/Kind | standardmäßig aus |
| Nachrichten | REST `/api/rest/view/v1/messages` | nur eigenes Konto | standardmäßig aus |
| Ferien | RPC `getHolidays` | klassenweit | verfügbar, Berechtigung prüfen |
| Stundenraster | RPC `getTimegridUnits` | klassenweit | verfügbar, Berechtigung prüfen |
| Schuljahr | RPC `getCurrentSchoolyear` | klassenweit | verfügbar, Berechtigung prüfen |

Nicht freigegeben: beliebige RPC-Aufrufe, Rohdaten, Noten, Klassenbuchinhalte und MCP-/LLM-Ausgaben.
