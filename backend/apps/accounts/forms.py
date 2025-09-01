from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Account


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)



class SellerForm(UserCreationForm):
    class Meta:
        model = Account
        fields = [
            "username",
            "email",
            "password1",   # <- vem do UserCreationForm
            "password2",   # <- confirmação automática
            "user_type",
            "first_name",
            "last_name",
            "document",
            "phone",
  
     
        ]

        