from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, status
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Tag, ShoppingCart)
from users.serializers import UserSerializer


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.pk')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        write_only=True,
        min_value=settings.MIN_VALUE,
        max_value=settings.MAX_VALUE,
    )

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')
    cooking_time = serializers.IntegerField(
        min_value=settings.MIN_VALUE,
        max_value=settings.MAX_VALUE
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        if hasattr(obj, 'is_favorited'):
            return obj.is_favorited
        user = self.context.get('request').user
        return (user.is_authenticated and
                obj.favorites.filter(owner=user).exists())

    def get_is_in_shopping_cart(self, obj):
        if hasattr(obj, 'is_in_shopping_cart'):
            return obj.is_in_shopping_cart
        user = self.context.get('request').user
        return (user.is_authenticated and
                obj.shopping_cart.filter(owner=user).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    author = UserSerializer(required=False)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'You forgot about ingredients'},
                status.HTTP_400_BAD_REQUEST,
            )
        valid_set = set()
        for ingredient in ingredients:
            if ingredient in valid_set:
                raise serializers.ValidationError(
                    {'ingredients': 'Ingredients must be unique'},
                    status.HTTP_400_BAD_REQUEST,
                )
            valid_set.add(ingredient)
            if (int(ingredient['amount']) < settings.MIN_VALUE or
                    int(ingredient['amount']) > settings.MAX_VALUE):
                raise serializers.ValidationError(
                    {
                        'ingredients':
                            'Amount of ingredients must be between 1 and 32000'
                    },
                    status.HTTP_400_BAD_REQUEST,
                )
        return data

    @staticmethod
    def _create_data(ingredients, obj):
        create_ingredients = [
            RecipeIngredient(
                recipe=obj,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]

        RecipeIngredient.objects.bulk_create(
            create_ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_data(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
        self._create_data(ingredients, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class ShortRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredient_amount',
        many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context.get('recipes_limit')
        if isinstance(recipes_limit, int) and recipes_limit > settings.ZERO:
            recipes_limit = min(
                recipes_limit,
                settings.RECIPE_LIMIT_SUBSCRIPTIONS
            )
            queryset = queryset[:recipes_limit]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        if hasattr(obj, 'is_subscribed'):
            return obj.is_subscribed
        user = self.context.get('request').user
        return (user.is_authenticated and
                obj.subscribed_by.filter(user=user).exists())


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'owner'),
                message='Recipe is already added to favorite',
            )
        ]


class ShoppingCartSerializer(FavoriteSerializer):
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'owner'),
                message='Recipe is already added to shopping cart',
            )
        ]
