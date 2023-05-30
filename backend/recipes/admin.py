from django.contrib.admin import ModelAdmin, TabularInline, register

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-empty-'


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    search_fields = ('name',)
    list_display = ('pk', 'name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (RecipeIngredientInline,)
    empty_value_display = '-empty-'


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    search_fields = ('owner', 'recipe')
    list_display = ('pk', 'owner', 'recipe')
    list_filter = ('owner', 'recipe')
    empty_value_display = '-empty-'


@register(ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    search_fields = ('owner', 'recipe')
    list_display = ('pk', 'owner', 'recipe')
    list_filter = ('owner', 'recipe')
    empty_value_display = '-empty-'


@register(Tag)
class TagAdmin(ModelAdmin):
    search_fields = ('name', 'color')
    list_display = ('name', 'color')
    list_filter = ('name', 'color')
    empty_value_display = '-empty-'
