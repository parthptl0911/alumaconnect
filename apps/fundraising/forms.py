from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'glass-input',
                'placeholder': 'Enter amount to donate (₹)',
                'min': '1',
            }),
        }
