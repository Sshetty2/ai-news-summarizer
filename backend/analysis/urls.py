from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SentimentAnalysisViewSet,
    AnalysisComparisonViewSet,
    UserPreferencesViewSet,
)

router = DefaultRouter()
router.register(r"analyses", SentimentAnalysisViewSet, basename="analyses")
router.register(r"comparisons", AnalysisComparisonViewSet, basename="comparisons")
router.register(r"preferences", UserPreferencesViewSet, basename="preferences")

urlpatterns = [
    path("analysis/", include(router.urls)),
]
