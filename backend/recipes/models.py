from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef
from django.utils.text import slugify

User = get_user_model()


class Ingredient(models.Model):
    """A model representing an ingredient."""
    name = models.CharField(
        verbose_name='Name of ingredient',
        max_length=200,
        help_text='Enter the name of the ingredient',
    )
    measurement_unit = models.CharField(
        verbose_name='Measurement unit',
        max_length=200,
        help_text='Enter measurement unit',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    """A model representing tags for recipes."""
    name = models.CharField(
        verbose_name='Name of tag',
        max_length=200,
        help_text='Enter the tag name',
        unique=True,
    )
    color = models.CharField(
        verbose_name='Color of the tag',
        max_length=7,
        help_text='Enter color HEX-code of the tag',
        unique=True,
    )
    slug = models.CharField(
        'Tag slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self) -> str:
        return f'{self.name}'


# class RecipeQuerySet(models.QuerySet):
#     def add_user_annotation(self, user_id: Optional[int]):
#         return self.annotate(
#             is_favorited=Exists(
#                 Favorite.objects.filter(
#                     user_id=user_id, recipe__pk=OuterRef('pk')
#                 )
#             ),
#             is_in_shopping_cart=Exists(
#                 ShoppingCart.objects.filter(
#                     user_id=user_id, recipe__pk=OuterRef('pk')
#                 )
#             ),
#         )


class Recipe(models.Model):
    """A model representing recipes."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author of the recipe',
    )
    name = models.CharField(
        verbose_name='Name of the recipe',
        max_length=200,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ingredients of the recipe',
        related_name='ingredients',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time in minutes',
        validators=(MinValueValidator(settings.MIN_VALUE),),
        help_text='Enter the cooking time in minutes'
    )
    pub_date = models.DateTimeField(
        verbose_name='Date and time of recipe creation',
        auto_now_add=True,
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Recipe description',
        blank=False,
        null=False,
        help_text='Enter the description of the recipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tag',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Image of the recipe',
        upload_to='recipes/images/',
        help_text='Attach a photo of the recipe',
        null=True,
        default=None,
    )
    # objects = RecipeQuerySet.as_manager()

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self) -> str:
        return f'{self.name}'


class RecipeIngredient(models.Model):
    """A model representing ingredients for a specific recipe."""
    amount = models.PositiveIntegerField(
        verbose_name='Amount',
        validators=(MinValueValidator(settings.MIN_VALUE), ),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='recipe_ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='recipe_ingredient',
    )

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Ingredient in recipe'
        verbose_name_plural = 'Ingredients in recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.recipe}: {self.ingredient} in amount: {self.amount}'


class ShoppingCart(models.Model):
    """A model representing recipes in shopping cart."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe in the shopping cart',
        related_name='shopping_cart',
        help_text='Select the recipe to add to shopping cart',
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Cart owner',
        related_name='shopping_cart',
    )
    pub_date = models.DateTimeField(
        verbose_name='Date added',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Shopping cart'
        verbose_name_plural = 'Shopping carts'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'owner'),
                name='unique_shopping_cart',
            ),
        )

    def __str__(self) -> str:
        return f'{self.owner} -> {self.recipe}'


class Favorite(models.Model):
    """A model representing favorite recipes."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        related_name='favorites',
        on_delete=models.CASCADE,
        help_text='Select the recipe to add to favorites'
    )
    owner = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Date added',
        auto_now_add=True,
        db_index=True,
        editable=False,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'owner'),
                name='unique_favorite_recipe_owner'
            ),
        )

    def __str__(self) -> str:
        return f'{self.owner} -> {self.recipe}'
