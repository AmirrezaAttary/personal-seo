from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = 'api-v1-accounts'


urlpatterns = [
    # register user
    path(
        "registration/",
        views.RegistrationAPIView.as_view(),
        name="registration",
    ),
    # login jwt
    path(
        "jwt/create/",
        views.CustomTokenObtainPairView.as_view(),
        name="jwt-create",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    # change password
    path(
        "change-password/",
        views.ChangePasswordApiView.as_view(),
        name="change-password",
    ),
    # profile
    path("profile/", views.ProfileApiView.as_view(), name="profile"),
    # router urls
]
