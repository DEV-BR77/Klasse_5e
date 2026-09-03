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
        "kicker": "Daten, Kalender und Hausaufgaben synchronisieren",
        "lead": "Die Schuldaten-Synchronisierung gehört immer zu einem bestätigten Kind. Erst die Verbindung, dann die Auswahl einzelner Inhalte; Aktualisierungen laufen anschließend automatisch.",
        "bullets": (
            "Eine Zustimmung allein richtet keine Verbindung ein.",
            "Stundenplan, Änderungen und Hausaufgaben erscheinen nach einem erfolgreichen Abruf im Portal. Noch kein Kalenderimport bedeutet: Die Verbindung hat noch keine Daten geliefert.",
            "Abwesenheiten, Noten, Nachrichten und Klassenbucheinträge werden nicht abgerufen.",
        ),
        "illustration": "sync",
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
    "webuntis_timetable_extended": ("Stundendetails", "Zusätzliche verfügbare Informationen zu Unterrichtsstunden anfragen."),
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
    "webuntis_absences": ("Abwesenheiten", "Diese besonders persönliche Kategorie kann freigegeben werden; der aktuelle Adapter kann sie technisch noch nicht lesen oder melden."),
}

for key, (label, summary) in WEBUNTIS_GUIDANCE.items():
    CONSENT_GUIDANCE[key] = {
        "display_label": label,
        "summary": summary,
        "yes": "Die Kategorie darf beim manuellen Klick auf „Aktuell prüfen“ für das ausgewählte Kind angefragt werden.",
        "no": "Diese Kategorie wird nicht bei der verbundenen Schulquelle angefragt.",
        "data": "Es werden nur die für die gewählte Funktion erforderlichen Daten und ein technischer Laufstatus gespeichert.",
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
        "title": "Daten, Kalender und Hausaufgaben synchronisieren",
        "body": "Für ein bestätigtes Kind können Stundenplan und Hausaufgaben automatisch aktualisiert werden. Die Verbindung und jede Datenart bleiben persönlich einstellbar. Bei einer neuen Verbindung gibt es zunächst noch keine Fachdaten.",
        "bullets": ("Kind eindeutig auswählen", "automatisch nach dem Login aktualisieren", "Kalender herunterladen oder abonnieren"),
        "illustration": "sync",
        "action_href": "/mehr/webuntis/",
        "action_label": "Synchronisierung öffnen",
    },
    {
        "title": "Veranstaltungen und Mitbringen",
        "body": "Termine, Zusagen und Mitbringlisten stehen zusammen. Mengen können aufgeteilt und eigene Beiträge ergänzt werden.",
        "bullets": ("offene Wünsche sehen", "Teilmenge übernehmen", "Mitgebrachtes abhaken"),
        "illustration": "event",
        "action_href": "/mehr/veranstaltungen/",
        "action_label": "Veranstaltungen öffnen",
    },
    {
        "title": "Wir fahren zusammen",
        "body": "Familien können Fahrradgruppen und Fahrgemeinschaften finden. Öffentliche Karten zeigen nur einen ungefähren Bereich; genaue Treffpunkte werden erst nach Annahme geteilt.",
        "bullets": ("Fahrrad oder Auto", "Hin- und Rückfahrt", "Treffpunkte gemeinsam abstimmen"),
        "illustration": "mobility",
        "action_href": "/mehr/mobilitaet/",
        "action_label": "Mobilität öffnen",
    },
    {
        "title": "Chat und Absprachen",
        "body": "Im Klassen- und Eventchat sind Text, Emojis, Dateien, Sprachnachrichten und persönliche @Erwähnungen möglich. Direkte Beleidigungen werden verdeckt; Bilder bleiben bis zur Inhaltsprüfung gesperrt. Noch kein Import oder noch keine Fachdaten sind kein Chat-Fehler, sondern betreffen nur die optionale Schuldaten-Synchronisierung.",
        "bullets": ("@Name benachrichtigt gezielt", "Aufbewahrung je Chatart", "Melden bleibt immer möglich"),
        "illustration": "chat",
        "action_href": "/chat/",
        "action_label": "Chat ansehen",
    },
    {
        "title": "Fotos und Galerien",
        "body": "Galerien ordnen Klassenfahrt, Feiern und andere Momente. Fotos werden geschützt hochgeladen und das eigene Kind kann direkt zugewiesen oder wieder entfernt werden.",
        "bullets": ("geschützter Upload", "Kategorien und Filter", "Erkennung nur mit ausdrücklicher Freigabe"),
        "illustration": "gallery",
        "action_href": "/mehr/fotos/",
        "action_label": "Galerien öffnen",
    },
    {
        "title": "Familie und persönliche Einstellungen",
        "body": "Familienbeziehungen werden geprüft und nicht nur über gleiche Namen erraten. Profil, Sichtbarkeit, Benachrichtigungen und Design gelten für den jeweiligen Login.",
        "bullets": ("bestätigte Kindbeziehung", "Datenschutz einzeln wählen", "eigenes Theme auswählen"),
        "illustration": "family",
        "action_href": "/mehr/familie/",
        "action_label": "Familie ansehen",
    },
    {
        "title": "Menü, Tutorial und Feedback",
        "body": "Das Menü bündelt alle selteneren Funktionen in verständlichen Gruppen. Diese Tour kann jederzeit neu gestartet werden; über Feedback lassen sich Ideen und Fehler direkt von der aktuellen Seite senden.",
        "bullets": ("Einführung jederzeit öffnen", "Feedback mit optionalem Screenshot", "Menügruppen übersichtlich aufklappen"),
        "illustration": "help",
        "action_href": "/mehr/",
        "action_label": "Menü öffnen",
    },
)
