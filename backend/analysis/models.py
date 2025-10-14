from django.db import models
from django.contrib.auth.models import User
from news.models import NewsArticle
import json


class SentimentAnalysis(models.Model):
    """Model to store AI-powered sentiment analysis results"""

    POLITICAL_BIAS_CHOICES = [
        ("far_left", "Far Left"),
        ("left", "Left"),
        ("center_left", "Center Left"),
        ("center", "Center"),
        ("center_right", "Center Right"),
        ("right", "Right"),
        ("far_right", "Far Right"),
        ("neutral", "Neutral"),
    ]

    # Core relationships
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sentiment_analyses"
    )
    article = models.ForeignKey(
        NewsArticle, on_delete=models.CASCADE, related_name="sentiment_analyses"
    )

    # Political Analysis
    political_bias = models.CharField(max_length=20, choices=POLITICAL_BIAS_CHOICES)
    bias_confidence_score = models.FloatField(help_text="Confidence score from 0-1")
    bias_reasoning = models.TextField(help_text="AI reasoning for bias classification")

    # Sentiment Metrics
    positive_sentiment = models.FloatField(
        help_text="Percentage of positive sentiment (0-1)"
    )
    negative_sentiment = models.FloatField(
        help_text="Percentage of negative sentiment (0-1)"
    )
    neutral_sentiment = models.FloatField(
        help_text="Percentage of neutral sentiment (0-1)"
    )
    overall_sentiment_score = models.FloatField(
        help_text="Overall sentiment score (-1 to 1)"
    )

    # Topic Analysis
    primary_topics = models.JSONField(
        default=list, help_text="List of primary political topics"
    )
    topic_distribution = models.JSONField(
        default=dict, help_text="Topic distribution percentages"
    )

    # Key insights
    key_themes = models.JSONField(default=list, help_text="Main themes identified")
    emotional_tone = models.CharField(max_length=50, blank=True)
    controversy_level = models.FloatField(
        default=0.0, help_text="Controversy level from 0-1"
    )

    # Metadata
    analysis_version = models.CharField(max_length=10, default="1.0")
    processing_time_seconds = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    raw_ai_response = models.JSONField(help_text="Raw response from OpenAI")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["article", "-created_at"]),
            models.Index(fields=["political_bias"]),
        ]
        verbose_name_plural = "Sentiment Analyses"

    def __str__(self):
        return f"Analysis of '{self.article.title[:50]}' by {self.user.username}"

    @property
    def bias_score_normalized(self):
        """Convert bias to numeric score for visualization (-1 = far left, 1 = far right)"""
        bias_mapping = {
            "far_left": -1.0,
            "left": -0.66,
            "center_left": -0.33,
            "center": 0.0,
            "neutral": 0.0,
            "center_right": 0.33,
            "right": 0.66,
            "far_right": 1.0,
        }
        return bias_mapping.get(self.political_bias, 0.0)


class AnalysisComparison(models.Model):
    """Model to store comparisons between multiple analyses"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="analysis_comparisons"
    )
    name = models.CharField(max_length=200)
    analyses = models.ManyToManyField(SentimentAnalysis, related_name="comparisons")
    comparison_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} by {self.user.username}"


class UserPreferences(models.Model):
    """Store user preferences for analysis"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="analysis_preferences"
    )
    preferred_categories = models.JSONField(
        default=list, help_text="User's preferred news categories"
    )
    notification_settings = models.JSONField(
        default=dict, help_text="User notification preferences"
    )
    default_analysis_depth = models.CharField(
        max_length=20,
        choices=[
            ("basic", "Basic"),
            ("detailed", "Detailed"),
            ("comprehensive", "Comprehensive"),
        ],
        default="detailed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
