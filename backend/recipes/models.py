from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, SET_NULL, CharField, CheckConstraint,
                              DateTimeField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, Q, TextField,
                              UniqueConstraint)
from django.db.models.functions import Length
from PIL import Image

from core.enums import Limits, Tuples
from core.validators import OneOfTwoValidator, hex_color_validator

CharField.register_lookup(Length)

User = get_user_model()


class Ingredient(Model):
    """A model representing ingredients for recipes.
    """
    name = CharField(
        verbose_name='Ingredient',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    measurement_unit = CharField(
        verbose_name='Measurement unit',
        max_length=24,
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingredient'
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def clean(self) -> None:
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        super().clean()

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Tag(Model):
    """A model representing tags for recipes."""
    name = CharField(
        verbose_name='Tag',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        validators=(OneOfTwoValidator(field='tag name'),),
        unique=True,
    )
    color = CharField(
        verbose_name='Color',
        max_length=7,
        unique=True,
        db_index=False,
    )
    slug = CharField(
        verbose_name='tag slug',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (color: {self.color})'

    def clean(self) -> None:
        self.name = self.name.strip().lower()
        self.slug = self.slug.strip().lower()
        self.color = hex_color_validator(self.color)
        return super().clean()


class Recipe(Model):
    """A model representing recipes."""
    name = CharField(
        verbose_name='Name of the recipe',
        max_length=Limits.MAX_LEN_RECIPES_CHARFIELD.value,
    )
    author = ForeignKey(
        verbose_name='Author of the recipe',
        related_name='recipes',
        to=User,
        on_delete=SET_NULL,
        null=True,
    )
    tags = ManyToManyField(
        verbose_name='Tag',
        related_name='recipes',
        to='Tag',
    )
    ingredients = ManyToManyField(
        verbose_name='Ingredients of the recipe',
        related_name='recipes',
        to=Ingredient,
        through='recipes.AmountIngredient',
    )
    pub_date = DateTimeField(
        verbose_name='',
        auto_now_add=True,
        editable=False,
    )
    image = ImageField(
        verbose_name='Image of the dish',
        upload_to='recipe_images/',
    )
    text = TextField(
        verbose_name='Description of the dish',
        max_length=Limits.MAX_LEN_RECIPES_TEXTFIELD.value,
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Cooking time',
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_COOKING_TIME.value,
                'Cooking time is too short',
            ),
            MaxValueValidator(
                Limits.MAX_COOKING_TIME.value,
                'Cooking time is too long',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
        )

    def clean(self) -> None:
        self.name = self.name.capitalize()
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        image = Image.open(self.image.path)
        image = image.resize(Tuples.RECIPE_IMAGE_SIZE)
        image.save(self.image.path)

    def __str__(self) -> str:
        return f'{self.name}. Author: {self.author.username}'


class AmountIngredient(Model):
    """A model representing amount of ingredients in recipe."""
    recipe = ForeignKey(
        verbose_name='In which recipes',
        related_name='ingredient',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        verbose_name='Related Ingredients',
        related_name='recipe',
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Amount',
        default=0,
        validators=(
            MinValueValidator(
                Limits.MIN_AMOUNT_INGREDIENTS,
                'Specify a larger amount of ingredients',
            ),
            MaxValueValidator(
                Limits.MAX_AMOUNT_INGREDIENTS,
                'Specify fewer ingredients',
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Amount of ingredients'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Carts(Model):
    """A model representing recipes in shopping cart."""
    recipe = ForeignKey(
        verbose_name='Recipe in the shopping cart',
        related_name='in_carts',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Cart owner',
        related_name='carts',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Date added',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Recipe in the shopping cart'
        verbose_name_plural = 'Recipes in the shopping cart'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Favorites(Model):
    """A model representing Favorite recipes."""
    recipe = ForeignKey(
        verbose_name='Favorite recipe',
        related_name='in_favorites',
        to=Recipe,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='User',
        related_name='favorites',
        to=User,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Date added',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorites recipes'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user', ),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
