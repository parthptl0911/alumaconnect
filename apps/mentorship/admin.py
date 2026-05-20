from django.contrib import admin
from .models import MentorshipRequest, Mentorship

@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'mentor', 'goal', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('student__email', 'mentor__email', 'goal')

@admin.register(Mentorship)
class MentorshipAdmin(admin.ModelAdmin):
    list_display = ('request', 'meeting_date', 'platform', 'created_at')
    list_filter = ('platform', 'meeting_date')
    search_fields = ('request__student__email', 'request__mentor__email', 'meeting_link')
