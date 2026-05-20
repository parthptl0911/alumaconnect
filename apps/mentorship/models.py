from django.db import models
from django.conf import settings

class MentorshipRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_mentorship_requests'
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_mentorship_requests'
    )
    goal = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A student can have only one request with a specific status for a specific mentor at a time.
        unique_together = ('student', 'mentor', 'status')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student} -> {self.mentor} ({self.status})"

class Mentorship(models.Model):
    PLATFORM_CHOICES = [
        ('google_meet', 'Google Meet'),
        ('zoom', 'Zoom'),
        ('teams', 'Microsoft Teams'),
    ]
    request = models.OneToOneField(MentorshipRequest, on_delete=models.CASCADE, related_name='active_session')
    meeting_date = models.DateTimeField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    meeting_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Active Mentorship: {self.request.student} with {self.request.mentor}"
