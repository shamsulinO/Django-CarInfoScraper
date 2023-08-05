from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *

class ChangeUrl(forms.ModelForm):
    search_link = forms.CharField(widget=forms.URLInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Ссылка'}))
    status = forms.BooleanField(widget=forms.CheckboxInput(attrs={'style': 'width:19px; height:19px;'}), required=False)

    class Meta:
        model = Cars
        fields = ('search_link', 'status',)


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Логин'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Пароль'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Логин'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Почта'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Пароль'}))
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput(attrs={'style': 'width: 100%; background-color: #fff; border-radius: 5px; border: 2px solid #4827EC; margin-bottom: 10px; padding-left: 5px;', 'placeholder': 'Повтор пароля'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')