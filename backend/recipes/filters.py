from django_filters import rest_framework

from .models import Ingredient, Recipe


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = rest_framework.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
