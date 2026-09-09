import pytest
from django.core.exceptions import ValidationError

from klasse5e.core.contact_data import (
    format_phone_number,
    normalize_email_address,
    normalize_phone_number,
)


def test_phone_number_is_stored_as_e164_and_displayed_readably():
    stored = normalize_phone_number("05361 123456")

    assert stored == "+495361123456"
    assert format_phone_number(stored) == "+49 5361 123456"


@pytest.mark.parametrize("value", ["123", "keine Telefonnummer", "+49 5361 123456 ext. 7"])
def test_invalid_or_extended_phone_number_is_rejected(value):
    with pytest.raises(ValidationError):
        normalize_phone_number(value)


def test_email_uses_one_normalization_and_django_validation_path():
    assert normalize_email_address(" Example.User@googlemail.com ") == "example.user@gmail.com"
    assert normalize_email_address("", required=False) == ""
    with pytest.raises(ValidationError):
        normalize_email_address("keine-adresse")
