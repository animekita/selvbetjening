from django import forms

class AuthenticateInputForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField()
