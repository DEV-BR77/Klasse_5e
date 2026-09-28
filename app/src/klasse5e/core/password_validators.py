from django.core.exceptions import ValidationError


class PasswordCompositionValidator:
    """Require a usable password without invalidating existing credentials."""

    def validate(self, password, user=None):
        if not any(character.isalpha() for character in password):
            raise ValidationError("Das Passwort muss mindestens einen Buchstaben enthalten.")
        if not any(character.isdecimal() for character in password):
            raise ValidationError("Das Passwort muss mindestens eine Ziffer enthalten.")
        if not any(not character.isalnum() for character in password):
            raise ValidationError("Das Passwort muss mindestens ein Sonderzeichen enthalten.")

    def get_help_text(self):
        return "Das Passwort benötigt mindestens einen Buchstaben, eine Ziffer und ein Sonderzeichen."
