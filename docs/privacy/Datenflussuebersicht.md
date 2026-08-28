# Datenflussübersicht

## Systemgrenzen

```text
Browser/PWA
   │ HTTPS, Sitzung, Formulare
   ▼
Django/Wagtail-Monolith ─────► PostgreSQL
   │         │                   Konten, Beziehungen,
   │         ├────► Medien       Einwilligungen, Inhalte
   │         │      Bilder/Dokumente
   │         ├────► lokaler Vision-Dienst (nur mit separater Biometrie-Einwilligung)
   │         ├────► Push-Anbieter (nur bei aktivierter Kategorie)
   │         └────► thgwob.webuntis.com (nur manueller, erlaubter Abruf)
   ▼
minimierte Audit- und Betriebsprotokolle ─────► verschlüsselte Backups
```

## Vertrauensgrenzen und Kontrollen

| Übergang | Risiko | Kontrolle |
|---|---|---|
| Browser → Anwendung | manipulierte Parameter, fremde Objekt-IDs | CSRF, Sitzungsschutz, serverseitige Objekt- und Rollenprüfung |
| Anwendung → Datenbank/Medien | zu breite interne Zugriffe | modulare Dienste, Least Privilege, keine öffentlichen Medienpfade |
| Anwendung → Vision | besonders schützenswerte biometrische Daten | global aus, separate aktuelle Einwilligung aller Berechtigten, Löschkaskade |
| Anwendung → Push | Gerätekennung und Inhaltsabfluss | Opt-in je Kategorie, minimierter Nachrichtentext, sofortige Abmeldung |
| Anwendung → WebUntis | Drittzugang und Schülerdaten | feste Host-Allowlist, verschlüsselter Zugang, manueller Abruf, keine Session-Speicherung |
| Anwendung → Backup | verzögerte Löschung | Verschlüsselung, Rotation, Zugriffsbeschränkung, dokumentierte Ablaufzeit |

Produktive Konten, Antworten und technische Kennungen werden weder in Test-Fixtures noch in Git übernommen.
