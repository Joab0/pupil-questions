from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from turnstile.fields import TurnstileField

from .models import User


class RegisterForm(UserCreationForm):
    turnstile = TurnstileField(theme="dark")

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]


class LoginForm(AuthenticationForm):
    turnstile = TurnstileField(theme="dark")

    username = forms.EmailField()
    password = forms.CharField()


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(min_length=2, max_length=30, required=False, strip=True)
    last_name = forms.CharField(min_length=2, max_length=30, required=False, strip=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
