from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    register_view,
    login_view,
    logout_view,
    user_info_view,
    UserProfileViewSet,
    UserSessionViewSet,
    dashboard_data,
)

router = DefaultRouter()
router.register(r"profile", UserProfileViewSet, basename="profile")
router.register(r"sessions", UserSessionViewSet, basename="sessions")

urlpatterns = [
    path("auth/register/", register_view, name="register"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/user/", user_info_view, name="user-info"),
    path("auth/dashboard/", dashboard_data, name="dashboard"),
    path("auth/", include(router.urls)),
]
