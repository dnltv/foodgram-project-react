from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.functions import Length
from PIL import Image

from core.limitations import Limits, Tuples
from core.validators import OneOfTwoValidator, hex_color_validator


CharField.register_lookup(Length)

User = get_user_model()


class Ingredient(models.Model):
    """A model representing an ingredient."""
    name = models.CharField(
        'Name of ingredient',
        max_length=200,
        help_text='Enter the name of the ingredient',
    )
    measurement_unit = models.CharField(
        'Measurement unit',
        max_length=200,
        help_text='Enter measurement unit',
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    """A model representing tags for recipes."""
    name = models.CharField(
        'Name of tag',
        max_length=200,
        help_text='Enter the tag name',
        unique=True,
    )
    color = models.CharField(
        'Color of the tag',
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
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


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
