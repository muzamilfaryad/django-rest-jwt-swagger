from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Profile
import re

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'phone_number', 'birth_date']

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'profile']

    def get_profile(self, obj):
        try:
            return ProfileSerializer(obj.profile).data
        except Exception:
            return None

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this username already exists.")]
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with this email already exists.")]
    )
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    updated_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'created_at', 'updated_at']

    def validate_password(self, value):
        errors = []
        
        if len(value) > 8:
            errors.append("maximum 8 characters")
        
        if not re.search(r'[a-z]', value):
            errors.append("at least one lowercase letter")
        
        if not re.search(r'[A-Z]', value):
            errors.append("at least one uppercase letter")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        if errors:
            error_message = "Must contain: " + ", ".join(errors) + "."
            raise serializers.ValidationError(error_message)
        
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
