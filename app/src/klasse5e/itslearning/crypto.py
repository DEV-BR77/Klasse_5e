from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


class PortalKeyMissing(RuntimeError):
    pass


def _fernet():
    key = getattr(settings, "ITSLEARNING_CREDENTIAL_ENCRYPTION_KEY", "")
    if not key:
        raise PortalKeyMissing("itslearning-Verschlüsselungsschlüssel ist nicht konfiguriert.")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(value):
    if not value:
        return b""
    return _fernet().encrypt(value.encode("utf-8"))


def decrypt(value):
    if not value:
        return ""
    try:
        return _fernet().decrypt(bytes(value)).decode("utf-8")
    except InvalidToken as exc:
        raise PortalKeyMissing("itslearning-Daten können nicht entschlüsselt werden.") from exc
