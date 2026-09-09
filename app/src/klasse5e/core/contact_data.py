"""Shared normalization for contact data entered through the portal."""

import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def normalize_login_email(value):
    email = (value or "").strip().casefold()
    local_part, separator, domain = email.partition("@")
    if separator and domain == "googlemail.com":
        domain = "gmail.com"
    return f"{local_part}@{domain}" if separator else email


def normalize_email_address(value, *, required=True):
    """Return the canonical address after Django's server-side validation."""

    email = normalize_login_email(value)
    if not email and not required:
        return ""
    if not email:
        raise ValidationError("Bitte gib eine E-Mail-Adresse an.")
    validate_email(email)
    return email


def normalize_phone_number(value, *, default_region="DE", required=False):
    """Validate a phone number and return its globally unique E.164 form."""

    raw_value = (value or "").strip()
    if not raw_value and not required:
        return ""
    if not raw_value:
        raise ValidationError("Bitte gib eine Telefonnummer an.")
    try:
        number = phonenumbers.parse(raw_value, default_region)
    except phonenumbers.NumberParseException as error:
        raise ValidationError("Bitte gib eine gültige Telefonnummer an.") from error
    if number.extension or not phonenumbers.is_valid_number(number):
        raise ValidationError("Bitte gib eine gültige Telefonnummer an.")
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


def format_phone_number(value):
    """Format a stored E.164 number for a readable international display."""

    raw_value = (value or "").strip()
    if not raw_value:
        return ""
    try:
        number = phonenumbers.parse(raw_value, None if raw_value.startswith("+") else "DE")
    except phonenumbers.NumberParseException:
        return raw_value
    if not phonenumbers.is_valid_number(number):
        return raw_value
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
