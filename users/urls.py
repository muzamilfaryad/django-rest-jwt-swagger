from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", views.CustomTokenRefreshView.as_view(), name="refresh"),
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("profile/", views.ProfileAPIView.as_view(), name="profile"),
]
