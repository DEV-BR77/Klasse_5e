from django import forms


class WebUntisCredentialForm(forms.Form):
    username = forms.CharField(label="WebUntis-Benutzername", max_length=160, widget=forms.TextInput(attrs={"autocomplete": "username"}))
    password = forms.CharField(label="WebUntis-Passwort", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
