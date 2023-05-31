from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if hasattr(obj, 'is_subscribed'):
            return obj.is_subscribed
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.following.filter(user=user).exists())


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_new_password(self, password):
        try:
            validate_password(password, User)
        except django_exceptions.ValidationError as exception:
            raise serializers.ValidationError(list(exception.messages))
        return password

    def validate_current_password(self, password):
        is_password_valid = self.context['request'].user.check_password(
            password
        )
        if not is_password_valid:
            raise serializers.ValidationError('Invalid password')
        return password
