from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, UserSession


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, data):
        """Validate passwords match"""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")
        return data

    def validate_username(self, value):
        """Validate username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Validate email is unique"""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """Create new user"""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate user credentials"""
        username = data["username"]
        password = data["password"]

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data["user"] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "bio",
            "avatar",
            "location",
            "website",
            "email_notifications",
            "newsletter_subscription",
            "total_analyses_created",
            "last_analysis_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
            "full_name",
            "total_analyses_created",
            "last_analysis_date",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        """Update user and profile data"""
        # Update User fields
        user_data = {}
        if "user" in validated_data:
            user_data = validated_data.pop("user")

        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update UserProfile fields
        return super().update(instance, validated_data)


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for UserSession model"""

    user_username = serializers.CharField(source="user.username", read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            "id",
            "user_username",
            "session_key",
            "ip_address",
            "user_agent",
            "created_at",
            "last_activity",
            "is_active",
            "duration_minutes",
        ]
        read_only_fields = ["id", "user_username", "duration_minutes"]

    def get_duration_minutes(self, obj):
        """Calculate session duration in minutes"""
        if obj.last_activity and obj.created_at:
            duration = obj.last_activity - obj.created_at
            return int(duration.total_seconds() / 60)
        return 0


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""

    total_analyses = serializers.IntegerField()
    analyses_this_month = serializers.IntegerField()
    favorite_categories = serializers.ListField()
    average_sentiment_bias = serializers.FloatField()
    most_controversial_topics = serializers.ListField()
    analysis_activity = serializers.ListField()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate passwords"""
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("New passwords don't match")

        # Check old password
        user = self.context["request"].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError("Old password is incorrect")

        return data

    def save(self):
        """Change user password"""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for public information"""

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "date_joined", "profile"]
        read_only_fields = ["id", "username", "date_joined"]
