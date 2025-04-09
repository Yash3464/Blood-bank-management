from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

from .models import BloodBank, Donor, BloodRequest, Donation


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class DonorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'email', 'phone_number', 'age', 'blood_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '18', 'max': '65'}),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18 or age > 65:
            raise ValidationError("Age must be between 18 and 65 years.")
        return age


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'email', 'age', 'blood_type']


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'requester_name', 'blood_group', 'units_required',
            'hospital_name', 'hospital_address', 'contact_number', 'email'
        ]

    def clean_units_required(self):
        units = self.cleaned_data['units_required']
        if units <= 0:
            raise ValidationError("Units required must be greater than 0.")
        if units > 10:
            raise ValidationError("Cannot request more than 10 units at once.")
        return units


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['blood_bank', 'units_donated']
        widgets = {
            'blood_bank': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.donor = kwargs.pop('donor', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.donor and not self.donor.can_donate():
            raise ValidationError("You must wait at least 90 days between donations.")
        return cleaned_data


class BloodBankForm(forms.ModelForm):
    class Meta:
        model = BloodBank
        fields = ['name', 'address', 'contact_number', 'email']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_contact_number(self):
        phone = self.cleaned_data['contact_number']
        if not phone.startswith('+'):
            raise ValidationError("Phone number must start with country code (e.g., +1).")
        return phone
