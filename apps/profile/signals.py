from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from apps.user_settings.models import UserSettings

@receiver(post_save, sender=User)
def create_user_profile_and_settings(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile and UserSettings record in Supabase
    whenever a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensures profile updates are saved when the user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()