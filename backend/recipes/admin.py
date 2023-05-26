from django.contrib.admin import ModelAdmin, TabularInline, display, register
from django.core.handlers.wsgi import WSGIRequest
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from recipes.forms import TagForm
from recipes.models import (AmountIngredient, Carts, Favorites, Ingredient,
                            Recipe, Tag)


class IngredientInline(TabularInline):
    model = AmountIngredient
    extra = 2


@register(AmountIngredient)
class LinksAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )

    save_on_top = True
    empty_value_display = '-empty-'


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name', 'author', 'get_image', 'count_favorites',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    raw_id_fields = ('author', )
    search_fields = (
        'name', 'author__username', 'tags__name',
    )
    list_filter = (
        'name', 'author__username', 'tags__name'
    )

    inlines = (IngredientInline,)
    save_on_top = True
    empty_value_display = '-empty-'

    def get_image(self, obj: Recipe) -> SafeString:
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    get_image.short_description = 'Image'

    def count_favorites(self, obj: Recipe) -> int:
        return obj.in_favorites.count()

    count_favorites.short_description = 'Favorites'


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = (
        'name', 'slug', 'color_code',
    )
    search_fields = (
        'name', 'color'
    )

    save_on_top = True
    empty_value_display = '-empty-'

    @display(description='Colored')
    def color_code(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>',
            obj.color[1:], obj.color
        )

    color_code.short_description = 'Color code of tag'


@register(Favorites)
class FavoriteAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe', 'date_added'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )

    def has_change_permission(
        self,
        request: WSGIRequest,
        obj: Favorites | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: WSGIRequest,
        obj: Favorites | None = None
    ) -> bool:
        return False


@register(Carts)
class CardAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe', 'date_added'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )

    def has_change_permission(
        self,
        request: WSGIRequest,
        obj: Carts | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: WSGIRequest,
        obj: Carts | None = None
    ) -> bool:
        return False
