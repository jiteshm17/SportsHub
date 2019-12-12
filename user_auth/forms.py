from django import forms
from django.contrib.auth.models import User
from .models import DeliveryLocation, Services
from user_auth.models import Profile


class DeliveryLocationForm(forms.ModelForm):
    class Meta:
        model = DeliveryLocation
        fields = ['pin_code']
        labels = {
            'pin_code': 'Pin Code'
        }


class ServicesForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = ['service_type']
        labels = {
            'service_type': 'Choose your service'
        }


class ServiceRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email']


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Username',
            'email': 'E-mail',
            'first_name': 'First Name',
            'last_name': 'Last Name'
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if qs.exists():
            raise forms.ValidationError("Username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("Email is already registered")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('confirm_password')
        if password != password1:
            raise forms.ValidationError("Passwords do not match!")
        return password1


class UserProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location']


class Contact_Form(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'phone_number']


class UpdateProfile(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Username',
            'email': 'E-mail'
        }
