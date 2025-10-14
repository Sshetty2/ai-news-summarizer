from django.contrib import admin
from .models import SentimentAnalysis, AnalysisComparison, UserPreferences


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "article_title_short",
        "political_bias",
        "overall_sentiment_score",
        "controversy_level",
        "created_at",
    ]
    list_filter = ["political_bias", "emotional_tone", "created_at"]
    search_fields = ["article__title", "user__username", "bias_reasoning"]
    readonly_fields = [
        "created_at",
        "processing_time_seconds",
        "bias_score_normalized",
        "raw_ai_response",
    ]
    date_hierarchy = "created_at"
    list_per_page = 20

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("user", "article", "created_at", "processing_time_seconds")},
        ),
        (
            "Political Analysis",
            {
                "fields": (
                    "political_bias",
                    "bias_confidence_score",
                    "bias_score_normalized",
                    "bias_reasoning",
                )
            },
        ),
        (
            "Sentiment Metrics",
            {
                "fields": (
                    "positive_sentiment",
                    "negative_sentiment",
                    "neutral_sentiment",
                    "overall_sentiment_score",
                    "emotional_tone",
                )
            },
        ),
        (
            "Topic Analysis",
            {"fields": ("primary_topics", "topic_distribution", "key_themes")},
        ),
        (
            "Additional Insights",
            {
                "fields": (
                    "controversy_level",
                    "analysis_version",
                    "raw_ai_response",
                )
            },
        ),
    )

    def article_title_short(self, obj):
        return (
            obj.article.title[:50] + "..."
            if len(obj.article.title) > 50
            else obj.article.title
        )

    article_title_short.short_description = "Article"


@admin.register(AnalysisComparison)
class AnalysisComparisonAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "analyses_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "user__username", "comparison_notes"]
    readonly_fields = ["created_at"]
    filter_horizontal = ["analyses"]

    def analyses_count(self, obj):
        return obj.analyses.count()

    analyses_count.short_description = "# Analyses"


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "default_analysis_depth", "created_at", "updated_at"]
    list_filter = ["default_analysis_depth", "created_at"]
    search_fields = ["user__username"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Preferences",
            {
                "fields": (
                    "preferred_categories",
                    "notification_settings",
                    "default_analysis_depth",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )
