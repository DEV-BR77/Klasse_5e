from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet():
    key = getattr(settings, "WEBUNTIS_CREDENTIAL_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("Credential encryption key is not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(value):
    return _fernet().encrypt(value.encode("utf-8"))


def decrypt(value):
    try:
        return _fernet().decrypt(bytes(value)).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Schulmanager-Zugang kann nicht entschlüsselt werden.") from exc
