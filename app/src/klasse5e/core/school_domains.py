import re
import unicodedata

from django.core.exceptions import ValidationError

BASE_DOMAIN = "klassid.de"
RESERVED_LABELS = {"www", "admin", "api", "mail", "kontakt", "static", "media"}
LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_code(value):
    value = unicodedata.normalize("NFKD", str(value).strip()).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    if not value or not LABEL_RE.fullmatch(value) or value in RESERVED_LABELS:
        raise ValidationError("Das Kürzel ist nicht DNS-tauglich oder reserviert.")
    return value


def propose_class_hostname(class_code, school_code):
    return f"{normalize_code(class_code)}-{normalize_code(school_code)}.{BASE_DOMAIN}"


def validate_class_hostname(hostname, *, reserved_exception=False):
    hostname = str(hostname).strip().lower()
    if hostname == f"5e.{BASE_DOMAIN}" and reserved_exception:
        return hostname
    suffix = f".{BASE_DOMAIN}"
    if not hostname.endswith(suffix):
        raise ValidationError("Der Klassenhostname muss unter klassid.de liegen.")
    label = hostname.removesuffix(suffix)
    if "." in label or not LABEL_RE.fullmatch(label) or label in RESERVED_LABELS:
        raise ValidationError("Der Klassenhostname ist ungültig oder reserviert.")
    return hostname
