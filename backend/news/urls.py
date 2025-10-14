from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NewsArticleViewSet,
    NewsSourceViewSet,
    NewsCategoryViewSet,
    UserReadArticleViewSet,
)

router = DefaultRouter()
router.register(r"articles", NewsArticleViewSet, basename="articles")
router.register(r"sources", NewsSourceViewSet, basename="sources")
router.register(r"categories", NewsCategoryViewSet, basename="categories")
router.register(r"read-articles", UserReadArticleViewSet, basename="read-articles")

urlpatterns = [
    path("news/", include(router.urls)),
]
