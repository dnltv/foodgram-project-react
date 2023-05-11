from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name', 'measurement_unit',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text', 'slug', 'pub_date')
    search_fields = ('author', 'name', 'text', 'ingredients', 'slug', 'pub_date')
    list_filter = ('author', 'name', 'text', 'ingredients', 'slug', 'pub_date')
    empty_value_display = '-empty-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('amount', 'ingredient', 'recipe')
    search_fields = ('amount', 'ingredient', 'recipe')
    list_filter = ('amount', 'ingredient', 'recipe')
    empty_value_display = '-empty-'
