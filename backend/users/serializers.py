from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from api.serializers import ShortRecipeSerializer


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


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context.get('recipes_limit')
        if isinstance(recipes_limit, int) and recipes_limit > 0:
            recipes_limit = min(recipes_limit,
                                settings.RECIPE_LIMIT_SUBSCRIPTIONS)
            queryset = queryset[:recipes_limit]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
