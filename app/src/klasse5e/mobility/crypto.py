from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _fernet():
    key = settings.MOBILITY_DATA_ENCRYPTION_KEY
    if not key:
        raise ImproperlyConfigured("MOBILITY_DATA_ENCRYPTION_KEY is required")
    return Fernet(key.encode())


def encrypt_address(value):
    return _fernet().encrypt(value.encode("utf-8")).decode("ascii")


def decrypt_address(value):
    if not value:
        return ""
    try:
        return _fernet().decrypt(value.encode("ascii")).decode("utf-8")
    except InvalidToken:
        return ""
