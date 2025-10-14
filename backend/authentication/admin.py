from django.contrib import admin
from .models import UserProfile, UserSession


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "location",
        "total_analyses_created",
        "last_analysis_date",
        "email_notifications",
        "created_at",
    ]
    list_filter = ["email_notifications", "newsletter_subscription", "created_at"]
    search_fields = ["user__username", "user__email", "bio", "location"]
    readonly_fields = [
        "total_analyses_created",
        "last_analysis_date",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Profile Information",
            {"fields": ("bio", "avatar", "location", "website")},
        ),
        (
            "Preferences",
            {"fields": ("email_notifications", "newsletter_subscription")},
        ),
        (
            "Usage Statistics",
            {
                "fields": (
                    "total_analyses_created",
                    "last_analysis_date",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "ip_address",
        "is_active",
        "created_at",
        "last_activity",
        "session_duration",
    ]
    list_filter = ["is_active", "created_at", "last_activity"]
    search_fields = ["user__username", "ip_address", "session_key"]
    readonly_fields = ["created_at", "last_activity"]
    date_hierarchy = "created_at"

    def session_duration(self, obj):
        if obj.last_activity and obj.created_at:
            duration = obj.last_activity - obj.created_at
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        return "N/A"

    session_duration.short_description = "Duration"
