from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=255)
    bidang_pembedahan = forms.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'bidang_pembedahan', 'password1', 'password2']
