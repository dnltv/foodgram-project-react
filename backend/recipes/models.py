from typing import Optional

from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    """A model representing an Ingredient for a Recipe."""
    name = models.CharField(max_length=200, verbose_name='Name')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Unit of measurement'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """A model representing a recipe."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=200, verbose_name='Name of the recipe')
    text = models.TextField(verbose_name='Text')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ingredients'
    )
    slug = models.SlugField(verbose_name='slug')
    pub_date = models.DateTimeField(
        verbose_name='Date of publication',
        auto_now=True,
        db_index=True
    )
    objects = 'RecipeQuerySet'.as_manager()

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name

