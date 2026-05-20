from django import forms
from .models import Story

class StorySubmissionForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['title', 'content', 'thumbnail', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': 'The Story Title (e.g. Scaling a startup to 1M users)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'glass-input',
                'placeholder': 'Share your journey, challenges, and insights...',
                'rows': 8
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'file-input',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'glass-input',
                'placeholder': 'e.g. Engineering, FAANG, Startup (comma separated)'
            }),
        }
