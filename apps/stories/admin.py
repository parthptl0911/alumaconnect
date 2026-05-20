from django.contrib import admin
from .models import Story
from django.utils import timezone

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'submitted_at', 'published_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'content', 'author__email')
    actions = ['approve_stories', 'reject_stories']

    def approve_stories(self, request, queryset):
        queryset.update(status='approved', published_at=timezone.now())
        self.message_user(request, "Selected stories have been approved and published.")
    approve_stories.short_description = "Approve and Publish selected stories"

    def reject_stories(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Selected stories have been rejected.")
    reject_stories.short_description = "Reject selected stories"
