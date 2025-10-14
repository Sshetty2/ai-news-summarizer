from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with additional information"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Profile information
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    newsletter_subscription = models.BooleanField(default=False)

    # Usage tracking
    total_analyses_created = models.IntegerField(default=0)
    last_analysis_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def get_full_name(self):
        """Get user's full name or username as fallback"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username


class UserSession(models.Model):
    """Track user sessions for analytics"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-last_activity"]

    def __str__(self):
        return f"Session for {self.user.username} - {self.created_at}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, "profile"):
        instance.profile.save()
