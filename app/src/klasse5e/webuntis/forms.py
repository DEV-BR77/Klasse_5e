from django import forms


class WebUntisCredentialForm(forms.Form):
    username = forms.CharField(
        label="Benutzername für den Schuldaten-Zugang",
        max_length=160,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Passwort für den Schuldaten-Zugang",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
