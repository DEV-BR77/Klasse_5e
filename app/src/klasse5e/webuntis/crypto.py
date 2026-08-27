from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


class CredentialKeyMissing(RuntimeError):
    pass


def _fernet():
    key = getattr(settings, "WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY", "")
    if not key:
        raise CredentialKeyMissing("WebUntis-Verschlüsselungsschlüssel ist nicht konfiguriert.")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(value):
    return _fernet().encrypt(value.encode("utf-8"))


def decrypt(value):
    try:
        return _fernet().decrypt(bytes(value)).decode("utf-8")
    except InvalidToken as exc:
        raise CredentialKeyMissing("WebUntis-Zugang kann nicht entschlüsselt werden.") from exc

