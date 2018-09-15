from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100, widget=forms.PasswordInput())
    password2 = forms.CharField(label='repeat password', max_length=100, widget=forms.PasswordInput())
    def pwd_validate(self,p1,p2):
        return p1==p2

class ChangePswForm(forms.Form):
    oldpassword = forms.CharField(label='old password', max_length=100, widget=forms.PasswordInput())
    newpassword = forms.CharField(label='new password', max_length=100, widget=forms.PasswordInput())

class RegionForm(forms.Form):
    name= forms.CharField(label='name', max_length=100)
    cover=forms.FloatField(label='cover', max_value=1,min_value=0)
    delay=forms.FloatField(label='delay/s', min_value=0)
    x= forms.IntegerField(label='topleft x', max_value=100,min_value=0)
    y= forms.IntegerField(label='topleft y', max_value=100,min_value=0)
    w= forms.IntegerField(label='width', max_value=100,min_value=0)
    h= forms.IntegerField(label='height', max_value=100,min_value=0)

class CamForm(forms.Form):
    name= forms.CharField(label='name', max_length=100)
    addr= forms.CharField(label='address', max_length=100)
