from django.db import models
from django.conf import settings
from django.utils import timezone

class Story(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review')
    thumbnail = models.ImageField(upload_to='stories/thumbnails/', null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags (e.g. Engineering, Startup, Scholarship)")
    submitted_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stories"
        ordering = ['-published_at', '-submitted_at']

    def __str__(self):
        return f"{self.title} by {self.author.email}"
