from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, StudentProfile, AlumniProfile, WhitelistEmail

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check if a whitelist entry exists to help populate initial profile data if needed
        whitelist_entry = WhitelistEmail.objects.filter(email=instance.email).first()
        
        if instance.role == 'student':
            StudentProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'bio': f"Name: {whitelist_entry.full_name} | Dept: {whitelist_entry.department}" if whitelist_entry else "",
                    'current_year': whitelist_entry.batch if whitelist_entry else ""
                }
            )
        elif instance.role == 'alumni':
            AlumniProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'graduation_year': whitelist_entry.batch if whitelist_entry else ""
                }
            )

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'alumni' and hasattr(instance, 'alumni_profile'):
        instance.alumni_profile.save()
