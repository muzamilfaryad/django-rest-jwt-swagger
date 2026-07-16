import logging
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User
from swaggerwithdjango.response import api_response
from swaggerwithdjango.bugsnag import notify_bugsnag, leave_breadcrumb
from .serializers import UserSerializer, RegisterSerializer

logger = logging.getLogger(__name__)


class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        leave_breadcrumb(
            "Profile fetch requested",
            metadata={"user_id": request.user.id},
        )

        try:
            serializer = UserSerializer(request.user)
            return api_response(
                message="Profile loaded successfully.",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            notify_bugsnag(
                e,
                severity="error",
                context="profile_fetch",
                user={
                    "id": request.user.id,
                    "email": request.user.email,
                    "username": request.user.username,
                },
                metadata={
                    "profile": {
                        "user_id": request.user.id,
                        "has_profile": hasattr(request.user, "profile"),
                    }
                },
            )
            logger.exception("Unexpected error fetching profile for user %s", request.user.id)
            return api_response(
                message="Something went wrong.",
                data=None,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        leave_breadcrumb(
            "Registration attempt",
            metadata={"username": request.data.get("username")},
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
            leave_breadcrumb(
                "User registered successfully",
                metadata={"username": serializer.data.get("username")},
            )
            return api_response(
                message="Account created successfully.",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            notify_bugsnag(
                e,
                severity="error",
                context="user_registration",
                metadata={
                    "registration": {
                        "username": request.data.get("username"),
                        "email": request.data.get("email"),
                    }
                },
            )
            logger.exception("Failed to create user account")
            return api_response(
                message="Account creation failed. Please try again.",
                data=None,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        leave_breadcrumb(
            "Login attempt",
            metadata={"username": request.data.get("username")},
        )

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            leave_breadcrumb(
                "Login successful",
                metadata={"username": request.data.get("username")},
            )
            return api_response(
                message="Login successful.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )

        except (TokenError, InvalidToken):
            logger.warning(
                "Failed login attempt for username: %s from IP: %s",
                request.data.get("username"),
                request.META.get("REMOTE_ADDR"),
            )
            return api_response(
                message="Invalid credentials.",
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            notify_bugsnag(
                e,
                severity="error",
                context="user_login",
                metadata={
                    "auth": {
                        "username": request.data.get("username"),
                        "ip": request.META.get("REMOTE_ADDR"),
                        "user_agent": request.META.get("HTTP_USER_AGENT"),
                    }
                },
            )
            logger.exception("Unexpected error during login")
            return api_response(
                message="Login failed. Please try again.",
                data=None,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return api_response(
                message="Token refreshed successfully.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )

        except (TokenError, InvalidToken):
            notify_bugsnag(
                Exception("Invalid or expired refresh token"),
                severity="info",
                context="token_refresh",
                metadata={
                    "token": {
                        "ip": request.META.get("REMOTE_ADDR"),
                    }
                },
            )
            return api_response(
                message="Invalid or expired refresh token.",
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as e:
            notify_bugsnag(
                e,
                severity="error",
                context="token_refresh",
                metadata={
                    "token": {"ip": request.META.get("REMOTE_ADDR")}
                },
            )
            logger.exception("Unexpected error during token refresh")
            return api_response(
                message="Token refresh failed. Please login again.",
                data=None,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
