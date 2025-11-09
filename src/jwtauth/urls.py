from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import logout_user, register_user

urlpatterns = [
    path("auth/register/", register_user, name="register_user"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),
    path("auth/logout/", logout_user, name="logout"),
]
