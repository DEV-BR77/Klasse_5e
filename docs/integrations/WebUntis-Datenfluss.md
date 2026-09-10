# WebUntis-Datenfluss

Stand: 10.09.2026. Die Schule verwaltet am Adapter genau eine HTTPS-Portaladresse. Beim Speichern eines persönlichen Zugangs leitet KlassID daraus den Host und – falls nicht ausdrücklich gepflegt – die Schulkennung aus der Subdomain ab. Die Werte werden nur akzeptiert, wenn der Host in `WEBUNTIS_ALLOWED_HOSTS` steht.

```text
Schuladapter (URL, aktivierte Module)
  → bestätigte Beziehung + Kind + persönlicher Modultoggle
  → verschlüsselte Verbindung dieses Elternkontos zu diesem Kind
  → begrenzter, lesender WebUntis-Adapter
  → personenbezogene Importdaten dieses Verbindungsdatensatzes
```

Weder ein Klassenadministrator noch ein zweites Elternkonto kann die verschlüsselten Zugangsdaten lesen oder für ein anderes Kind verwenden. Pro Abruf gelten Host-Allowlist, HTTPS, begrenzte Methoden, Zeitüberschreitung, Rate-Limit und Sitzungsende. Audit enthält keine Zugangsdaten, Antworttexte oder URLs mit Geheimnissen.
