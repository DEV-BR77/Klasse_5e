# Sicherheit Phase 2

Es gibt keine öffentliche Registrierung. Konten entstehen über einmalige,
gehashte und ablaufende Einladungen an eine konkrete E-Mail-Adresse. Der
Bootstrap-Befehl schreibt das einmalige Token mit Modus `0600` in einen vom
Betreiber bestimmten Secret-Pfad und gibt es nicht im Log aus.

Privilegierte Rollen werden bis zur Einrichtung eines von django-allauth
verwalteten TOTP- oder WebAuthn-Authenticators blockiert. Recovery Codes werden
von allauth verwaltet. Hauptadministratoren ernennen weitere Administratoren;
die fachliche UI dafür bleibt bewusst auf Django/Wagtail-Administration
begrenzt. Loginversuche werden pro IP/E-Mail-Kombination begrenzt.

Cookies sind HttpOnly, SameSite=Lax und außerhalb des Diagnosemodus Secure.
CSRF, Clickjacking-, MIME-Sniffing- und Referrer-Schutz sind aktiv. Auditdaten
enthalten nur Actor, Aktion, Ziel-ID und minimierte Metadaten, keine Passwörter,
Tokens oder vollständigen sensiblen Inhalte.

E-Mail-Verifikation wird im Einladungsfluss durch Bindung des Tokens an die
eingeladene Adresse hergestellt. Ein später angeschlossener E-Mail-Versand darf
nur allauths verifizierten Flow verwenden; Phase 2 versendet nichts extern.
# Galerien (Phase 5)

Fotodateien werden inhaltlich geprüft, vollständig neu codiert und nur über
klassenautorisierte Views ausgeliefert. Metadaten, Benutzerpfade und öffentliche
Medien-URLs werden nicht übernommen. Consent wird bei jedem Abruf erneut
bewertet; Datenschutzmeldungen sperren vorsorglich. Antworten tragen `private,
no-store`; Logs und Audit enthalten keine Bilddaten, EXIF-Inhalte oder Namen
abgebildeter Kinder.
