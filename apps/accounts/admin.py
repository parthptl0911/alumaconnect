from django.contrib import admin
from .models import CustomUser, WhitelistEmail, StudentProfile, AlumniProfile

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'is_active')

@admin.register(WhitelistEmail)
class WhitelistEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'batch', 'department', 'enrollment_number')
    search_fields = ('email', 'first_name', 'last_name', 'enrollment_number')
    list_filter = ('role', 'batch', 'department')

admin.site.register(StudentProfile)

@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'designation', 'graduation_year', 'is_mentor_available')
    list_editable = ('is_mentor_available',)
    list_filter = ('is_mentor_available', 'graduation_year')
    search_fields = ('user__email', 'company', 'designation')
