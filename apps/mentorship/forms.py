from django import forms
from .models import MentorshipRequest, Mentorship

class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['goal', 'message']
        widgets = {
            'goal': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': 'e.g. Career Guidance in AI'
            }),
            'message': forms.Textarea(attrs={
                'class': 'glass-input',
                'placeholder': 'Tell the mentor a bit about yourself and what you hope to achieve...',
                'rows': 5
            }),
        }

from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

class MentorshipAcceptForm(forms.ModelForm):
    class Meta:
        model = Mentorship
        fields = ['meeting_date', 'platform', 'meeting_link']
        widgets = {
            'meeting_date': forms.DateTimeInput(attrs={
                'class': 'glass-input',
                'type': 'datetime-local',
                'id': 'meeting_date'
            }),
            'platform': forms.Select(attrs={
                'class': 'glass-input'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'glass-input',
                'placeholder': 'https://meet.google.com/xxx-xxxx-xxx'
            }),
        }

    def clean_meeting_date(self):
        meeting_date = self.cleaned_data.get('meeting_date')
        if meeting_date:
            # Check if meeting_date is at least 10 minutes in the future
            if meeting_date < timezone.now() + timedelta(minutes=10):
                raise ValidationError("Please select a future date and time (at least 10 minutes ahead).")
        return meeting_date

class MentorshipRejectForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'glass-input',
            'placeholder': 'Briefly explain why you are declining the request...',
            'rows': 4
        }),
        required=True
    )
