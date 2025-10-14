from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import NewsArticle, NewsSource, NewsCategory, UserReadArticle
from .serializers import (
    NewsArticleListSerializer,
    NewsArticleDetailSerializer,
    NewsSourceSerializer,
    NewsCategorySerializer,
    UserReadArticleSerializer,
    NewsSearchSerializer,
)
from .services import NewsAPIService, populate_sample_categories
import logging

logger = logging.getLogger(__name__)


class StandardResultsPagination(PageNumberPagination):
    """Standard pagination for news articles"""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news articles"""

    queryset = (
        NewsArticle.objects.filter(is_active=True)
        .select_related("source", "category")
        .prefetch_related("sentiment_analyses")
    )
    pagination_class = StandardResultsPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

    def get_queryset(self):
        """Filter articles based on query parameters"""
        queryset = self.queryset

        # Filter by category
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(
                Q(category__slug=category) | Q(category__name__icontains=category)
            )

        # Filter by source
        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source__name__icontains=source)

        # Search in title and description
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        # Filter by date range
        from_date = self.request.query_params.get("from_date")
        to_date = self.request.query_params.get("to_date")

        if from_date:
            queryset = queryset.filter(published_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(published_at__lte=to_date)

        # Sort by parameter
        sort_by = self.request.query_params.get("sort_by", "-published_at")
        valid_sorts = ["published_at", "-published_at", "title", "-created_at"]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

        return queryset

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def mark_as_read(self, request, pk=None):
        """Mark article as read by the user"""
        article = self.get_object()
        user_read, created = UserReadArticle.objects.get_or_create(
            user=request.user, article=article
        )

        if created:
            return Response({"status": "marked as read"})
        else:
            return Response({"status": "already read"})

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def fetch_latest(self, request):
        """Fetch latest articles from News API"""
        category = request.data.get("category")
        max_articles = min(int(request.data.get("max_articles", 50)), 100)

        try:
            service = NewsAPIService()
            created_count = service.fetch_and_store_articles(
                category=category, max_articles=max_articles
            )

            return Response(
                {
                    "status": "success",
                    "created_count": created_count,
                    "message": f"Fetched {created_count} new articles",
                }
            )

        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["get"])
    def trending(self, request):
        """Get trending articles (most analyzed in last 24 hours)"""
        since = timezone.now() - timedelta(hours=24)

        trending_articles = (
            self.get_queryset()
            .annotate(
                analysis_count=Count(
                    "sentiment_analyses",
                    filter=Q(sentiment_analyses__created_at__gte=since),
                )
            )
            .filter(analysis_count__gt=0)
            .order_by("-analysis_count", "-published_at")[:20]
        )

        serializer = self.get_serializer(trending_articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def categories_with_counts(self, request):
        """Get categories with article counts"""
        categories = NewsCategory.objects.annotate(
            article_count=Count("articles", filter=Q(articles__is_active=True))
        ).filter(article_count__gt=0)

        serializer = NewsCategorySerializer(categories, many=True)
        return Response(serializer.data)


class NewsSourceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news sources"""

    queryset = NewsSource.objects.annotate(
        article_count=Count("articles", filter=Q(articles__is_active=True))
    ).filter(article_count__gt=0)
    serializer_class = NewsSourceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["get"])
    def articles(self, request, pk=None):
        """Get articles from a specific source"""
        source = self.get_object()
        articles = NewsArticle.objects.filter(source=source, is_active=True).order_by(
            "-published_at"
        )

        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = NewsArticleListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = NewsArticleListSerializer(
            articles, many=True, context={"request": request}
        )
        return Response(serializer.data)


class NewsCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for news categories"""

    queryset = NewsCategory.objects.annotate(
        article_count=Count("articles", filter=Q(articles__is_active=True))
    )
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def articles(self, request, slug=None):
        """Get articles from a specific category"""
        category = self.get_object()
        articles = (
            NewsArticle.objects.filter(category=category, is_active=True)
            .select_related("source")
            .order_by("-published_at")
        )

        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = NewsArticleListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = NewsArticleListSerializer(
            articles, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=["post"], permission_classes=[permissions.IsAdminUser]
    )
    def populate_defaults(self, request):
        """Create default news categories"""
        created_count = populate_sample_categories()
        return Response(
            {
                "status": "success",
                "created_count": created_count,
                "message": f"Created {created_count} categories",
            }
        )


class UserReadArticleViewSet(viewsets.ModelViewSet):
    """ViewSet for user read articles"""

    serializer_class = UserReadArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserReadArticle.objects.filter(user=self.request.user).select_related(
            "article"
        )

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Get recently read articles"""
        recent_reads = self.get_queryset().order_by("-read_at")[:20]
        serializer = self.get_serializer(recent_reads, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear_history(self, request):
        """Clear user's read history"""
        deleted_count = self.get_queryset().count()
        self.get_queryset().delete()

        return Response(
            {
                "status": "success",
                "deleted_count": deleted_count,
                "message": f"Cleared {deleted_count} read articles",
            }
        )
