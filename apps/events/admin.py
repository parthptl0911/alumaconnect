from django.contrib import admin
from .models import Event, RSVP

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'capacity', 'attendee_count', 'is_active')
    list_filter = ('date', 'event_type', 'is_active')
    search_fields = ('title', 'location')

@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'status', 'rsvp_date')
    list_filter = ('status', 'rsvp_date')
    search_fields = ('user__email', 'event__title')
