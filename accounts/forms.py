# accounts/forms.py
from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm

class PasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
