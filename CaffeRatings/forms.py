from django import forms
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from .models import MineUser


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = MineUser
        fields = ['username', 'email']
