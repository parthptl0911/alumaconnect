from django.contrib import admin
from .models import Campaign, Donation

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_amount', 'current_amount', 'is_active', 'end_date')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'campaign', 'amount', 'status', 'donated_at')
    list_filter = ('status', 'donated_at')
    search_fields = ('donor__email', 'campaign__title')
