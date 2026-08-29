STEP_GUIDANCE = {
    1: {
        "kicker": "In Ruhe einrichten",
        "lead": "Wir zeigen zuerst, was das Portal kann. Danach entscheidest du verständlich und einzeln über freiwillige Funktionen.",
        "bullets": (
            "Dein Fortschritt wird nach jedem Schritt gespeichert.",
            "Ein Nein schränkt Kalender, Beiträge und andere Kernfunktionen nicht ein.",
            "Alle Entscheidungen lassen sich später unter Mehr → Einwilligungen ändern.",
        ),
        "illustration": "welcome",
    },
    2: {
        "kicker": "Persönliches Konto",
        "lead": "Jede erwachsene Person nutzt ein eigenes Konto. So bleibt nachvollziehbar, wer eine Einstellung geändert hat.",
        "bullets": (
            "Das Konto wird nicht mit einem Kind geteilt.",
            "Kinderprofile können ohne eigenes Login zugeordnet sein.",
            "Deine Anmeldung und deine Einwilligungen bleiben persönlich.",
        ),
        "illustration": "identity",
    },
    3: {
        "kicker": "Sicher zugeordnet",
        "lead": "Nur eine bestätigte, aktuell gültige Sorgebeziehung erlaubt Entscheidungen für ein Kind.",
        "bullets": (
            "Eine gemeinsame Adresse allein reicht nicht aus.",
            "Mehrere Sorgeberechtigte entscheiden jeweils mit ihrem eigenen Konto.",
            "Fehlt die Zuordnung, bleiben Kinddaten und Kind-Einstellungen gesperrt.",
        ),
        "illustration": "family",
    },
    4: {
        "kicker": "Datenschutz auf einen Blick",
        "lead": "Für Login und Klassenberechtigung sind wenige Pflichtdaten nötig. Alles Weitere wird als freiwilliger Zweck einzeln erklärt.",
        "bullets": (
            "Optionales ist zunächst ausgeschaltet.",
            "Du siehst vor jeder Wahl, welche Wirkung Ja und Nein haben.",
            "Ein Widerruf wirkt für die Zukunft und ist genauso erreichbar wie die Zustimmung.",
        ),
        "illustration": "privacy",
    },
    5: {
        "kicker": "Sichtbarkeit im Klassenraum",
        "lead": "Lege fest, ob andere bestätigte Klassenmitglieder Kontaktdaten im Profil sehen dürfen.",
        "illustration": "contact",
    },
    6: {
        "kicker": "Galerie ist nicht Gesichtssuche",
        "lead": "Die Freigabe für Klassenfotos erlaubt nur die geschützte Galerie. Biometrische Suche wird später separat entschieden.",
        "illustration": "gallery",
    },
    7: {
        "kicker": "Nur die Hinweise, die du möchtest",
        "lead": "Push-Mitteilungen werden pro Kategorie geschaltet. Auf dem Sperrbildschirm erscheinen keine sensiblen Inhalte.",
        "illustration": "notifications",
    },
    8: {
        "kicker": "WebUntis – Verbindung und Datenfreigabe",
        "lead": "WebUntis gehört immer zu einem bestätigten Kind. Erst die Verbindung, dann die Freigabe einzelner Kategorien, dann ein manueller Abruf.",
        "bullets": (
            "Eine Zustimmung allein richtet keine Verbindung ein.",
            "Phase 9A prüft derzeit nur den technischen Zugriff; Stunden und Hausaufgaben werden noch nicht in den Kalender importiert.",
            "Abwesenheiten, Noten, Nachrichten und Klassenbucheinträge werden nicht abgerufen.",
        ),
        "illustration": "webuntis",
    },
    9: {
        "kicker": "Vorschläge statt automatischer Zuordnung",
        "lead": "Wenn die Funktion später freigegeben ist, vergleicht ein lokaler Dienst neue Galeriefotos und schlägt mögliche Treffer vor. Ein Mensch muss jeden Treffer bestätigen.",
        "bullets": (
            "Keine automatische endgültige Personenzuordnung.",
            "Keine Cloud-Gesichtserkennung; der Vision-Dienst läuft lokal.",
            "Die Funktion ist momentan technisch gesperrt und bleibt aus.",
        ),
        "illustration": "biometric",
    },
    10: {
        "kicker": "Bereit für den Klassenraum",
        "lead": "Prüfe die wichtigsten Punkte. Nach dem Abschluss folgt eine kurze bebilderte Tour durch die Anwendung.",
        "illustration": "summary",
    },
}


CONSENT_GUIDANCE = {
    "profile_contact_visibility": {
        "summary": "Andere bestätigte Klassenmitglieder dürfen freigegebene Kontaktfelder im Klassenprofil sehen.",
        "yes": "Freigegebene E-Mail- oder Telefonnummern können im geschützten Mitgliederbereich angezeigt werden.",
        "no": "Kontaktdaten bleiben verborgen. Persönliche Nachrichten und Kernfunktionen funktionieren weiter.",
        "data": "Nur die Kontaktfelder, die im Profil zusätzlich auf „Mitglieder“ gestellt wurden.",
    },
    "photo_gallery": {
        "summary": "Fotos der ausgewählten Person dürfen in geschützten Klassengalerien verarbeitet und berechtigten Mitgliedern gezeigt werden.",
        "yes": "Freigegebene Klassenfotos können sichtbar sein. Uploads werden neu codiert und Metadaten entfernt.",
        "no": "Fotos dieser Person dürfen nicht regulär in der Galerie angezeigt werden.",
        "data": "Neu codierte Bildableitungen und eine manuell geprüfte Personenangabe; keine Gesichtsdaten.",
    },
    "push_general": {
        "summary": "Neutrale Hinweise zu wichtigen Neuigkeiten dürfen an dieses Gerät gesendet werden.",
        "yes": "Das Gerät kann einen Hinweis wie „Es gibt etwas Neues“ erhalten.",
        "no": "Neuigkeiten sind weiterhin nach dem Öffnen des Portals sichtbar.",
        "data": "Technischer Push-Endpunkt und eine neutrale Hinweiskategorie, keine vertraulichen Inhalte.",
    },
    "push_chat": {
        "summary": "Das Gerät darf neutral auf neue Aktivitäten im Klassenchat hinweisen.",
        "yes": "Du erfährst zeitnah, dass im Chat etwas Neues vorliegt.",
        "no": "Chats bleiben nutzbar; es erscheint lediglich kein Gerätehinweis.",
        "data": "Technischer Push-Endpunkt und Kategorie; kein Nachrichtentext auf dem Sperrbildschirm.",
    },
    "push_events": {
        "summary": "Das Gerät darf neutral an anstehende Termine und Mitbringlisten erinnern.",
        "yes": "Du kannst Erinnerungen erhalten und öffnest Details erst nach dem Login.",
        "no": "Alle Termine bleiben im Kalender sichtbar, aber ohne Gerätehinweis.",
        "data": "Technischer Push-Endpunkt und Terminkategorie; keine Namen oder Termindetails im Push.",
    },
    "biometric_face_search": {
        "summary": "Ein lokaler Dienst dürfte Gesichter auf freigegebenen Galeriefotos vergleichen und mögliche Treffer zur menschlichen Prüfung vorschlagen.",
        "yes": "Erst nach zusätzlicher technischer Freigabe könnten Vorschläge entstehen; niemand wird automatisch endgültig zugeordnet.",
        "no": "Es werden keine biometrischen Profile oder Gesichtsvorschläge für die Person erzeugt.",
        "data": "Lokale Gesichtsmerkmale und technisch getrennte Kennungen; keine Namen im Vision-Dienst.",
    },
}


WEBUNTIS_GUIDANCE = {
    "webuntis_timetable": ("Stundenplan", "Unterrichtszeiten und Fach des bestätigten Kindes manuell anfragen."),
    "webuntis_timetable_extended": ("Stundendetails", "Zusätzliche, von WebUntis freigegebene Informationen zu Unterrichtsstunden anfragen."),
    "webuntis_substitutions": ("Vertretungen und Änderungen", "Entfall, Vertretung, Raum- oder Zeitänderungen anfragen."),
    "webuntis_homework": ("Hausaufgaben", "Fach, Aufgabe- und Fälligkeitsdatum sowie freigegebenen Aufgabentext anfragen."),
    "webuntis_exams": ("Prüfungen", "Freigegebene Prüfungstermine und zugehörige Stundeninformationen anfragen."),
    "webuntis_holidays": ("Ferien", "Unterrichtsfreie Zeiträume der Schule anfragen."),
    "webuntis_timegrid": ("Stundenraster", "Beginn und Ende der schulischen Unterrichtsblöcke anfragen."),
    "webuntis_subjects": ("Fächer", "Die für den Stundenplan benötigten Fachbezeichnungen anfragen."),
    "webuntis_rooms": ("Räume", "Die für Stunden und Änderungen benötigten Raumangaben anfragen."),
    "webuntis_teachers": ("Lehrkräfte", "Freigegebene Lehrkraftbezeichnungen für Stunden und Änderungen anfragen."),
    "webuntis_schoolyears": ("Schuljahr", "Das aktuelle Schuljahr zur zeitlichen Zuordnung anfragen."),
    "webuntis_statusdata": ("Statushinweise", "Technische Änderungs- und Stundenstatus für eine verständliche Anzeige anfragen."),
    "webuntis_absences": ("Abwesenheiten", "Diese besonders persönliche Kategorie wird vom Adapter nicht abgerufen und bleibt aus."),
}

for key, (label, summary) in WEBUNTIS_GUIDANCE.items():
    CONSENT_GUIDANCE[key] = {
        "display_label": label,
        "summary": summary,
        "yes": "Die Kategorie darf beim manuellen Klick auf „Aktuell prüfen“ für das ausgewählte Kind angefragt werden.",
        "no": "Diese Kategorie wird nicht bei WebUntis angefragt.",
        "data": "Phase 9A speichert nur technischen Laufstatus und keine WebUntis-Fachantworten.",
    }


TUTORIAL_STEPS = (
    {
        "title": "Startseite",
        "body": "Die Startseite bündelt das, was heute wichtig ist. Leere Karten sagen ausdrücklich, ob noch keine Inhalte gepflegt oder eine Quelle noch nicht verbunden ist.",
        "bullets": ("heutiger Unterricht", "anstehende Termine", "neue Beiträge und Hinweise"),
        "illustration": "dashboard",
        "action_href": "/",
        "action_label": "Startseite ansehen",
    },
    {
        "title": "Kalender",
        "body": "Wechsle tageweise und sieh nur Unterricht und Termine deiner Klasse. Ein manueller Plan bleibt auch dann sichtbar, wenn eine externe Quelle ausfällt.",
        "bullets": ("Tag vor und zurück", "Unterricht getrennt von Terminen", "Änderungen mit Text statt nur Farbe"),
        "illustration": "calendar",
        "action_href": "/kalender/",
        "action_label": "Kalender öffnen",
    },
    {
        "title": "Beiträge und Chat",
        "body": "Beiträge informieren die Klasse; der Chat ist für kurze Absprachen. Inhalte bleiben auf die aktive Klassenmitgliedschaft begrenzt.",
        "bullets": ("respektvoll schreiben", "problematische Inhalte melden", "keine fremden persönlichen Daten weitergeben"),
        "illustration": "chat",
        "action_href": "/chat/",
        "action_label": "Chat ansehen",
    },
    {
        "title": "Familie und Zuordnung",
        "body": "Hier siehst du, für welche Kinder dein Konto bestätigt ist. Nur diese Zuordnung gibt dir passende Ansichts- und Entscheidungsrechte.",
        "bullets": ("persönliches Elternkonto", "bestätigte Kindbeziehung", "getrennte Rechte je Zweck"),
        "illustration": "family",
        "action_href": "/mehr/familie/",
        "action_label": "Familie ansehen",
    },
    {
        "title": "Freiwillige Funktionen",
        "body": "Kontaktprofil, Fotos, Push, WebUntis und Biometrie sind getrennte Einstellungen. Du kannst jeden Bereich später wieder öffnen und ändern.",
        "bullets": ("standardmäßig aus", "Ja und Nein mit sichtbarer Wirkung", "Widerruf jederzeit möglich"),
        "illustration": "settings",
        "action_href": "/mehr/einwilligungen/",
        "action_label": "Einstellungen öffnen",
    },
    {
        "title": "WebUntis verstehen",
        "body": "Eine WebUntis-Zustimmung ist noch kein Import. Es braucht eine Verbindung für das bestätigte Kind und aktivierte Kategorien. Phase 9A prüft aktuell nur den Zugriff und zeigt noch keine Fachdaten im Kalender.",
        "bullets": ("Kind auswählen", "Verbindung testen", "Kategorien freigeben", "manuell aktuell prüfen"),
        "illustration": "webuntis",
        "action_href": "/mehr/webuntis/",
        "action_label": "WebUntis-Status öffnen",
    },
    {
        "title": "Hilfe und später ändern",
        "body": "Unter Mehr findest du Einwilligungen, Benachrichtigungen, WebUntis und diese Tour. Du musst beim ersten Durchlauf nicht alles aktivieren.",
        "bullets": ("Tour neu starten", "Entscheidungen ändern", "Sitzungen und Sicherheit verwalten"),
        "illustration": "help",
        "action_href": "/mehr/",
        "action_label": "Zum Bereich Mehr",
    },
)
