from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, UserSession
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserSessionSerializer,
    UserStatsSerializer,
    PasswordChangeSerializer,
    UserSerializer,
)
import logging

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Log the user in
        login(request, user)

        # Create session record
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.create(
                user=user,
                session_key=session_key,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

        return Response(
            {"message": "Registration successful", "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # Log the user in
        login(request, user)

        # Create or update session record
        session_key = request.session.session_key
        if session_key:
            session, created = UserSession.objects.get_or_create(
                user=user,
                session_key=session_key,
                defaults={
                    "ip_address": get_client_ip(request),
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "is_active": True,
                },
            )

            if not created:
                session.last_activity = timezone.now()
                session.is_active = True
                session.save()

        return Response(
            {"message": "Login successful", "user": UserSerializer(user).data}
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    # Deactivate user sessions
    UserSession.objects.filter(
        user=request.user, session_key=request.session.session_key
    ).update(is_active=False)

    # Logout user
    logout(request)

    return Response({"message": "Logout successful"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_info_view(request):
    """Get current user information"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user profile"""
        try:
            return self.get_queryset().get()
        except UserProfile.DoesNotExist:
            # This should not happen due to signals, but just in case
            return UserProfile.objects.create(user=self.request.user)

    def list(self, request):
        """Return current user's profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request):
        """Override create to prevent duplicate profiles"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get user statistics"""
        user = request.user
        profile = self.get_object()

        # Get analysis statistics
        from analysis.models import SentimentAnalysis

        analyses = SentimentAnalysis.objects.filter(user=user)

        total_analyses = analyses.count()

        # Analyses this month
        month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        analyses_this_month = analyses.filter(created_at__gte=month_start).count()

        # Favorite categories (most analyzed)
        category_counts = {}
        for analysis in analyses.select_related("article__category"):
            if analysis.article.category:
                cat_name = analysis.article.category.name
                category_counts[cat_name] = category_counts.get(cat_name, 0) + 1

        favorite_categories = sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Average sentiment bias
        if total_analyses > 0:
            avg_bias = (
                sum(analysis.bias_score_normalized for analysis in analyses)
                / total_analyses
            )
        else:
            avg_bias = 0

        # Most controversial topics
        all_topics = []
        controversial_analyses = analyses.filter(controversy_level__gte=0.7)
        for analysis in controversial_analyses:
            all_topics.extend(analysis.primary_topics)

        topic_counts = {}
        for topic in all_topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        controversial_topics = sorted(
            topic_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Analysis activity (last 30 days)
        activity_data = []
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            count = analyses.filter(created_at__date=date).count()
            activity_data.append({"date": date.isoformat(), "count": count})

        stats_data = {
            "total_analyses": total_analyses,
            "analyses_this_month": analyses_this_month,
            "favorite_categories": [
                {"name": name, "count": count} for name, count in favorite_categories
            ],
            "average_sentiment_bias": avg_bias,
            "most_controversial_topics": [
                {"topic": topic, "count": count}
                for topic, count in controversial_topics
            ],
            "analysis_activity": list(reversed(activity_data)),
        }

        serializer = UserStatsSerializer(stats_data)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user sessions"""

    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user).order_by(
            "-last_activity"
        )

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get active user sessions"""
        active_sessions = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def terminate(self, request, pk=None):
        """Terminate a specific session"""
        session = self.get_object()
        session.is_active = False
        session.save()

        return Response({"message": "Session terminated"})

    @action(detail=False, methods=["post"])
    def terminate_all(self, request):
        """Terminate all user sessions except current"""
        current_session_key = request.session.session_key

        terminated_count = (
            self.get_queryset()
            .exclude(session_key=current_session_key)
            .update(is_active=False)
        )

        return Response({"message": f"Terminated {terminated_count} sessions"})


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_data(request):
    """Get dashboard data for authenticated user"""
    user = request.user

    # Get recent analyses
    from analysis.models import SentimentAnalysis

    recent_analyses = (
        SentimentAnalysis.objects.filter(user=user)
        .select_related("article")
        .order_by("-created_at")[:5]
    )

    # Get analysis count by category
    from django.db.models import Count

    category_stats = (
        SentimentAnalysis.objects.filter(user=user)
        .values("article__category__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # Get recent read articles
    from news.models import UserReadArticle

    recent_reads = (
        UserReadArticle.objects.filter(user=user)
        .select_related("article")
        .order_by("-read_at")[:5]
    )

    return Response(
        {
            "recent_analyses": [
                {
                    "id": analysis.id,
                    "article_title": analysis.article.title,
                    "political_bias": analysis.political_bias,
                    "controversy_level": analysis.controversy_level,
                    "created_at": analysis.created_at,
                }
                for analysis in recent_analyses
            ],
            "category_stats": [
                {
                    "category": stat["article__category__name"] or "Uncategorized",
                    "count": stat["count"],
                }
                for stat in category_stats
            ],
            "recent_reads": [
                {
                    "id": read.article.id,
                    "title": read.article.title,
                    "read_at": read.read_at,
                }
                for read in recent_reads
            ],
        }
    )
