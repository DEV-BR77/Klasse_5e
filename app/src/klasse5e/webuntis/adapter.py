from dataclasses import dataclass
from .client import ALLOWED_REST, ALLOWED_RPC, WebUntisClient

@dataclass(frozen=True)
class Capability:
    key: str
    method: str
    purpose: str
    scope: str
    personal: bool

CAPABILITIES = (
    Capability("students", "students", "Kinder des Elternkontos ermitteln", "personal", True),
    Capability("timetable", "getTimetable", "Stundenplan lesen", "personal", True),
    Capability("timetable_weekly", "timetable_weekly", "Angereicherter Wochenstundenplan lesen", "personal", True),
    Capability("substitutions", "getSubstitutions", "Vertretungen und Aenderungen lesen", "class", False),
    Capability("homework", "homework", "Hausaufgaben lesen", "personal", True),
    Capability("exams", "exams", "Pruefungen lesen", "personal", True),
    Capability("absences", "absences", "Fehlzeiten lesen", "personal", True),
    Capability("messages", "messages", "Persoenliche Nachrichten lesen", "personal", True),
    Capability("holidays", "getHolidays", "Ferien lesen", "class", False),
    Capability("timegrid", "getTimegridUnits", "Stundenraster lesen", "class", False),
    Capability("schoolyear", "getCurrentSchoolyear", "Aktuelles Schuljahr lesen", "class", False),
)

def public_methods(_client_cls=WebUntisClient):
    return sorted(set(ALLOWED_RPC) | set(ALLOWED_REST))

def classify_error(exc):
    return getattr(exc, "code", "unknown_external_error")

class WebUntisAdapter:
    def __init__(self, *, server, school, username, password, useragent="Klasse-5e-WebUntis-Pilot/9A"):
        self.client = WebUntisClient(username, password, server=server, school=school, user_agent=useragent)

    def test_connection(self):
        with self.client:
            return {"status": "ok", "methods": public_methods()}

    def call_readonly(self, method, *args, **kwargs):
        if method in ALLOWED_RPC:
            return self.client.rpc(method, kwargs or (args[0] if args else {}))
        if method in ALLOWED_REST:
            return self.client.rest(method, params=kwargs)
        raise ValueError("Nicht freigegebener WebUntis-Endpunkt")
