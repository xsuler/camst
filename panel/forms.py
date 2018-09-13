from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(label='repeat password', max_length=100, widget=forms.PasswordInput())

class ChangePswForm(forms.Form):
    oldpassword = forms.CharField(label='old password', max_length=100, widget=forms.PasswordInput())
    newpassword = forms.CharField(label='new password', max_length=100, widget=forms.PasswordInput())


