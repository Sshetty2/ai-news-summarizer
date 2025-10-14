from rest_framework import serializers
from .models import SentimentAnalysis, AnalysisComparison, UserPreferences
from news.serializers import NewsArticleListSerializer


class SentimentAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for SentimentAnalysis model"""

    article = NewsArticleListSerializer(read_only=True)
    article_id = serializers.IntegerField(write_only=True)
    bias_score_normalized = serializers.ReadOnlyField()
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = SentimentAnalysis
        fields = [
            "id",
            "article",
            "article_id",
            "user_username",
            "political_bias",
            "bias_confidence_score",
            "bias_reasoning",
            "positive_sentiment",
            "negative_sentiment",
            "neutral_sentiment",
            "overall_sentiment_score",
            "primary_topics",
            "topic_distribution",
            "key_themes",
            "emotional_tone",
            "controversy_level",
            "bias_score_normalized",
            "analysis_version",
            "processing_time_seconds",
            "created_at",
            "raw_ai_response",
        ]
        read_only_fields = [
            "id",
            "user_username",
            "bias_score_normalized",
            "analysis_version",
            "processing_time_seconds",
            "created_at",
            "raw_ai_response",
        ]

    def create(self, validated_data):
        # Add the current user to the validated data
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def validate_article_id(self, value):
        """Validate that the article exists"""
        from news.models import NewsArticle

        try:
            NewsArticle.objects.get(id=value)
        except NewsArticle.DoesNotExist:
            raise serializers.ValidationError("Article not found")
        return value

    def validate(self, data):
        """Custom validation for sentiment percentages"""
        if all(
            key in data
            for key in ["positive_sentiment", "negative_sentiment", "neutral_sentiment"]
        ):
            total = (
                data["positive_sentiment"]
                + data["negative_sentiment"]
                + data["neutral_sentiment"]
            )
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                raise serializers.ValidationError(
                    "Sentiment percentages must sum to 1.0"
                )
        return data


class SentimentAnalysisListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for analysis lists"""

    article_title = serializers.CharField(source="article.title", read_only=True)
    article_category = serializers.CharField(
        source="article.category.name", read_only=True
    )
    bias_score_normalized = serializers.ReadOnlyField()

    class Meta:
        model = SentimentAnalysis
        fields = [
            "id",
            "article_title",
            "article_category",
            "political_bias",
            "bias_confidence_score",
            "overall_sentiment_score",
            "controversy_level",
            "bias_score_normalized",
            "created_at",
        ]


class AnalysisComparisonSerializer(serializers.ModelSerializer):
    """Serializer for AnalysisComparison model"""

    analyses = SentimentAnalysisListSerializer(many=True, read_only=True)
    analysis_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    user_username = serializers.CharField(source="user.username", read_only=True)
    analysis_count = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisComparison
        fields = [
            "id",
            "name",
            "analyses",
            "analysis_ids",
            "comparison_notes",
            "user_username",
            "analysis_count",
            "created_at",
        ]
        read_only_fields = ["id", "user_username", "created_at"]

    def get_analysis_count(self, obj):
        return obj.analyses.count()

    def create(self, validated_data):
        analysis_ids = validated_data.pop("analysis_ids", [])
        validated_data["user"] = self.context["request"].user

        comparison = super().create(validated_data)

        # Add analyses to the comparison
        if analysis_ids:
            analyses = SentimentAnalysis.objects.filter(
                id__in=analysis_ids, user=self.context["request"].user
            )
            comparison.analyses.set(analyses)

        return comparison

    def validate_analysis_ids(self, value):
        """Validate that all analysis IDs belong to the current user"""
        if not value:
            raise serializers.ValidationError("At least one analysis is required")

        user = self.context["request"].user
        valid_analyses = SentimentAnalysis.objects.filter(
            id__in=value, user=user
        ).count()

        if valid_analyses != len(value):
            raise serializers.ValidationError(
                "Some analyses don't exist or don't belong to you"
            )

        return value


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for UserPreferences model"""

    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserPreferences
        fields = [
            "id",
            "user_username",
            "preferred_categories",
            "notification_settings",
            "default_analysis_depth",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_username", "created_at", "updated_at"]

    def validate_preferred_categories(self, value):
        """Validate preferred categories"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Preferred categories must be a list")

        valid_categories = [
            "general",
            "business",
            "technology",
            "politics",
            "health",
            "science",
            "sports",
            "entertainment",
        ]

        for category in value:
            if category not in valid_categories:
                raise serializers.ValidationError(
                    f"'{category}' is not a valid category"
                )

        return value


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for requesting new analysis"""

    article_id = serializers.IntegerField()
    analysis_depth = serializers.ChoiceField(
        choices=[
            ("basic", "Basic"),
            ("detailed", "Detailed"),
            ("comprehensive", "Comprehensive"),
        ],
        default="detailed",
    )

    def validate_article_id(self, value):
        """Validate that the article exists"""
        from news.models import NewsArticle

        try:
            NewsArticle.objects.get(id=value)
        except NewsArticle.DoesNotExist:
            raise serializers.ValidationError("Article not found")
        return value


class AnalysisStatsSerializer(serializers.Serializer):
    """Serializer for analysis statistics"""

    total_analyses = serializers.IntegerField()
    average_bias_score = serializers.FloatField()
    average_sentiment = serializers.FloatField()
    average_controversy = serializers.FloatField()
    bias_distribution = serializers.DictField()
    top_topics = serializers.ListField()
    sentiment_range = serializers.DictField()
    analyses_by_month = serializers.ListField(required=False)


class TrendingTopicsSerializer(serializers.Serializer):
    """Serializer for trending topics"""

    topic = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()
