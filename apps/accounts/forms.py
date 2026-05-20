from django import forms
from django.contrib.auth import authenticate
from .models import WhitelistEmail, CustomUser


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input', 
            'placeholder': 'e.g. j.doe@college.edu',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input', 
            'placeholder': '••••••••',
            'required': True
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Invalid email or password.",
                    code='invalid_login'
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'readonly': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'required': True
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'required': True
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if not WhitelistEmail.objects.filter(email=email).exists():
            raise forms.ValidationError("Email not authorized. You must be on the college whitelist to register.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Account already exists with this email. Please login.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        from .models import StudentProfile
        model = StudentProfile
        fields = ['bio', 'current_year', 'skills', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'current_year': forms.TextInput(attrs={'class': 'form-input'}),
            'skills': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Python, React, UI/UX'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input'})
        }

class AlumniProfileForm(forms.ModelForm):
    class Meta:
        from .models import AlumniProfile
        model = AlumniProfile
        fields = ['company', 'designation', 'location', 'graduation_year', 'linkedin', 'skills', 'profile_image', 'is_mentor_available']
        labels = {
            'is_mentor_available': 'Available for Mentorship'
        }
        help_texts = {
            'is_mentor_available': 'Check this box to appear as a mentor and allow students to send you requests.'
        }
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-input'}),
            'designation': forms.TextInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'graduation_year': forms.TextInput(attrs={'class': 'form-input'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/in/...'}),
            'skills': forms.TextInput(attrs={'class': 'form-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input'}),
            'is_mentor_available': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }
