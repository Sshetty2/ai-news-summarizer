from rest_framework import serializers
from .models import NewsArticle, NewsSource, NewsCategory, UserReadArticle


class NewsSourceSerializer(serializers.ModelSerializer):
    """Serializer for NewsSource model"""

    class Meta:
        model = NewsSource
        fields = ["id", "name", "description", "url", "created_at"]
        read_only_fields = ["id", "created_at"]


class NewsCategorySerializer(serializers.ModelSerializer):
    """Serializer for NewsCategory model"""

    article_count = serializers.SerializerMethodField()

    class Meta:
        model = NewsCategory
        fields = ["id", "name", "slug", "description", "article_count"]
        read_only_fields = ["id"]

    def get_article_count(self, obj):
        return obj.articles.filter(is_active=True).count()


class NewsArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article lists"""

    source_name = serializers.CharField(source="source.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    has_analysis = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "description",
            "url",
            "url_to_image",
            "author",
            "source_name",
            "category_name",
            "category_slug",
            "published_at",
            "has_analysis",
        ]

    def get_has_analysis(self, obj):
        """Check if current user has analyzed this article"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.sentiment_analyses.filter(user=request.user).exists()
        return False


class NewsArticleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single article view"""

    source = NewsSourceSerializer(read_only=True)
    category = NewsCategorySerializer(read_only=True)
    user_analyses = serializers.SerializerMethodField()
    is_read_by_user = serializers.SerializerMethodField()

    class Meta:
        model = NewsArticle
        fields = [
            "id",
            "title",
            "description",
            "content",
            "url",
            "url_to_image",
            "author",
            "source",
            "category",
            "published_at",
            "created_at",
            "language",
            "user_analyses",
            "is_read_by_user",
        ]

    def get_user_analyses(self, obj):
        """Get analyses for current user"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            from analysis.serializers import SentimentAnalysisSerializer

            analyses = obj.sentiment_analyses.filter(user=request.user)
            return SentimentAnalysisSerializer(analyses, many=True).data
        return []

    def get_is_read_by_user(self, obj):
        """Check if user has read this article"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return UserReadArticle.objects.filter(
                user=request.user, article=obj
            ).exists()
        return False


class UserReadArticleSerializer(serializers.ModelSerializer):
    """Serializer for tracking read articles"""

    article_title = serializers.CharField(source="article.title", read_only=True)

    class Meta:
        model = UserReadArticle
        fields = ["id", "article", "article_title", "read_at"]
        read_only_fields = ["id", "read_at"]

    def create(self, validated_data):
        # Add the current user to the validated data
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class NewsSearchSerializer(serializers.Serializer):
    """Serializer for news search parameters"""

    query = serializers.CharField(max_length=200, required=False)
    category = serializers.CharField(max_length=50, required=False)
    source = serializers.CharField(max_length=100, required=False)
    from_date = serializers.DateTimeField(required=False)
    to_date = serializers.DateTimeField(required=False)
    sort_by = serializers.ChoiceField(
        choices=[
            ("published_at", "Published Date"),
            ("-published_at", "Published Date (Desc)"),
            ("title", "Title"),
            ("-created_at", "Created Date (Desc)"),
        ],
        default="-published_at",
    )

    def validate(self, data):
        # Custom validation logic
        if data.get("from_date") and data.get("to_date"):
            if data["from_date"] > data["to_date"]:
                raise serializers.ValidationError("from_date must be before to_date")
        return data
