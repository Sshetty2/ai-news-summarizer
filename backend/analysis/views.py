from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import SentimentAnalysis, AnalysisComparison, UserPreferences
from .serializers import (
    SentimentAnalysisSerializer,
    SentimentAnalysisListSerializer,
    AnalysisComparisonSerializer,
    UserPreferencesSerializer,
    AnalysisRequestSerializer,
    AnalysisStatsSerializer,
    TrendingTopicsSerializer,
)
from .services import OpenAIAnalysisService, get_trending_topics
from news.models import NewsArticle
import logging

logger = logging.getLogger(__name__)


class AnalysisPagination(PageNumberPagination):
    """Pagination for analysis results"""

    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50


class SentimentAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for sentiment analysis"""

    serializer_class = SentimentAnalysisSerializer
    pagination_class = AnalysisPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter analyses for current user"""
        queryset = (
            SentimentAnalysis.objects.filter(user=self.request.user)
            .select_related("article__source", "article__category")
            .order_by("-created_at")
        )

        # Filter by political bias
        bias = self.request.query_params.get("bias")
        if bias:
            queryset = queryset.filter(political_bias=bias)

        # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(article__category__slug=category)

        # Filter by date range
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)

        # Filter by controversy level
        min_controversy = self.request.query_params.get("min_controversy")
        if min_controversy:
            try:
                min_controversy = float(min_controversy)
                queryset = queryset.filter(controversy_level__gte=min_controversy)
            except ValueError:
                pass

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return SentimentAnalysisListSerializer
        return SentimentAnalysisSerializer

    @action(detail=False, methods=["post"])
    def analyze_article(self, request):
        """Analyze a specific article using AI"""
        serializer = AnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data["article_id"]

        try:
            article = NewsArticle.objects.get(id=article_id)

            # Check if user already analyzed this article
            existing_analysis = SentimentAnalysis.objects.filter(
                user=request.user, article=article
            ).first()

            if existing_analysis:
                return Response(
                    {
                        "message": "Article already analyzed",
                        "analysis": SentimentAnalysisSerializer(existing_analysis).data,
                    }
                )

            # Create analysis using OpenAI service
            ai_service = OpenAIAnalysisService()
            analysis = ai_service.analyze_article(article, request.user)

            serializer = SentimentAnalysisSerializer(analysis)
            return Response(
                {
                    "message": "Analysis completed successfully",
                    "analysis": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except NewsArticle.DoesNotExist:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error analyzing article {article_id}: {e}")
            return Response(
                {"error": "Analysis failed. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get user's analysis statistics"""
        user_analyses = self.get_queryset()

        if not user_analyses.exists():
            return Response({"total_analyses": 0, "message": "No analyses found"})

        # Calculate statistics
        total_analyses = user_analyses.count()

        # Bias distribution
        bias_distribution = {}
        for analysis in user_analyses:
            bias = analysis.political_bias
            bias_distribution[bias] = bias_distribution.get(bias, 0) + 1

        # Average scores
        avg_sentiment = (
            user_analyses.aggregate(avg_sentiment=Avg("overall_sentiment_score"))[
                "avg_sentiment"
            ]
            or 0
        )

        avg_controversy = (
            user_analyses.aggregate(avg_controversy=Avg("controversy_level"))[
                "avg_controversy"
            ]
            or 0
        )

        avg_bias = (
            sum(analysis.bias_score_normalized for analysis in user_analyses)
            / total_analyses
        )

        # Top topics
        all_topics = []
        for analysis in user_analyses:
            all_topics.extend(analysis.primary_topics)

        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Sentiment range
        sentiment_scores = [a.overall_sentiment_score for a in user_analyses]
        sentiment_range = {
            "min": min(sentiment_scores) if sentiment_scores else 0,
            "max": max(sentiment_scores) if sentiment_scores else 0,
        }

        # Analyses by month (last 12 months)
        analyses_by_month = []
        now = timezone.now()
        for i in range(12):
            month_start = now.replace(day=1) - timedelta(days=30 * i)
            month_end = month_start.replace(day=28) + timedelta(
                days=4
            )  # Approximate month end

            count = user_analyses.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).count()

            analyses_by_month.append(
                {"month": month_start.strftime("%Y-%m"), "count": count}
            )

        stats_data = {
            "total_analyses": total_analyses,
            "average_bias_score": avg_bias,
            "average_sentiment": avg_sentiment,
            "average_controversy": avg_controversy,
            "bias_distribution": bias_distribution,
            "top_topics": top_topics,
            "sentiment_range": sentiment_range,
            "analyses_by_month": list(reversed(analyses_by_month)),
        }

        serializer = AnalysisStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def trending_topics(self, request):
        """Get trending topics from user's analyses"""
        days = int(request.query_params.get("days", 7))
        topics = get_trending_topics(user=request.user, days=days)

        total_count = sum(count for _, count in topics)
        trending_data = [
            {
                "topic": topic,
                "count": count,
                "percentage": (count / total_count * 100) if total_count > 0 else 0,
            }
            for topic, count in topics[:10]
        ]

        serializer = TrendingTopicsSerializer(trending_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recent analyses"""
        recent_analyses = self.get_queryset()[:10]
        serializer = SentimentAnalysisListSerializer(recent_analyses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def controversial(self, request):
        """Get most controversial analyses"""
        controversial = (
            self.get_queryset()
            .filter(controversy_level__gte=0.6)
            .order_by("-controversy_level")[:10]
        )

        serializer = SentimentAnalysisListSerializer(controversial, many=True)
        return Response(serializer.data)


class AnalysisComparisonViewSet(viewsets.ModelViewSet):
    """ViewSet for analysis comparisons"""

    serializer_class = AnalysisComparisonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AnalysisComparison.objects.filter(
            user=self.request.user
        ).prefetch_related("analyses")

    @action(detail=True, methods=["get"])
    def comparative_stats(self, request, pk=None):
        """Get comparative statistics for a comparison"""
        comparison = self.get_object()
        analyses = comparison.analyses.all()

        if not analyses:
            return Response({"error": "No analyses in comparison"})

        # Use the service to get comparative analysis
        from .services import OpenAIAnalysisService

        service = OpenAIAnalysisService()
        stats = service.get_comparative_analysis(analyses)

        return Response(stats)


class UserPreferencesViewSet(viewsets.ModelViewSet):
    """ViewSet for user preferences"""

    serializer_class = UserPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserPreferences.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user preferences"""
        try:
            return self.get_queryset().get()
        except UserPreferences.DoesNotExist:
            return UserPreferences.objects.create(user=self.request.user)

    def create(self, request):
        """Override create to handle get_or_create logic"""
        preferences, created = UserPreferences.objects.get_or_create(
            user=request.user, defaults=request.data
        )

        if not created:
            # Update existing preferences
            serializer = self.get_serializer(
                preferences, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            preferences = serializer.instance

        serializer = self.get_serializer(preferences)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
