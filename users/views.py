from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from swaggerwithdjango.response import api_response
from .serializers import UserSerializer, RegisterSerializer



class ProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user)
        return api_response(
            message="Profile loaded successfully.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            message="Account created successfully.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return api_response(
                message="Login successful.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return api_response(
                message="Invalid credentials.",
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return api_response(
                message="Token refreshed successfully.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return api_response(
                message="Invalid or expired refresh token.",
                data=None,
                status_code=status.HTTP_401_UNAUTHORIZED
            )

