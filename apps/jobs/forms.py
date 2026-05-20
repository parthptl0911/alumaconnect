from django import forms
from .models import Job, JobApplication

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'requirements', 
            'salary_range', 'location', 'job_type', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'Job Title'}),
            'company': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'glass-input', 'placeholder': 'Job Description', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'glass-input', 'placeholder': 'Job Requirements', 'rows': 4}),
            'salary_range': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'e.g., $100k - $120k'}),
            'location': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'Location (City, Country or Remote)'}),
            'job_type': forms.Select(attrs={'class': 'glass-input'}),
            'deadline': forms.DateInput(attrs={'class': 'glass-input', 'type': 'date'}),
        }

from django.core.validators import FileExtensionValidator

class JobApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'glass-input', 'accept': '.pdf,.doc,.docx'}),
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )

    class Meta:
        model = JobApplication
        fields = ['full_name', 'email', 'resume', 'cover_letter']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'glass-input', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'glass-input', 'placeholder': 'Email Address'}),
            'cover_letter': forms.Textarea(attrs={'class': 'glass-input', 'placeholder': 'Why should we hire you?', 'rows': 5}),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB.")
        return resume
