from django_filters import rest_framework
from django.contrib.auth import get_user_model
from django.db.models import Exists, Subquery, OuterRef, \
    Prefetch
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import Carts, Favorites, Ingredient, Recipe, Tag
from api.permissions import (AdminOrReadOnly, AuthorStaffOrReadOnly,
                             DjangoModelPermissions, IsAuthenticated)
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             ShortRecipeSerializer, TagSerializer,
                             UserSubscribeSerializer)
from users.models import Follow

from backend.api.limit import PaginationLimit
from backend.api.serializers import RecipeCreateSerializer
from backend.recipes.filters import IngredientFilter, RecipeFilter
from backend.recipes.models import Favorite, ShoppingCart


User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PaginationLimit
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'recipe_id'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        user_queryset = User.objects.all()
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Subquery(
                    Favorite.objects.filter(owner=user, recipe=OuterRef('pk'))
                ))
            ).annotate(
                is_in_shopping_cart=Exists(Subquery(
                    ShoppingCart.objects.filter(owner=user, recipe=OuterRef('pk'))
                ))
            )
            user_queryset = user_queryset.annotate(
                is_subscribed=Exists(Subquery(
                    Follow.objects.filter(user=user, following=OuterRef('pk'))
                ))
            )
        if self.action == 'list':
            return queryset.prefetch_related(
                Prefetch('author', user_queryset)
            ).prefetch_related(
                'tags'
            ).prefetch_related(
                'recipe_ingredient'
            ).prefetch_related(
                'recipe_ingredient__ingredient'
            )
        return queryset

    def get_permissions(self):
        if self.action in ('favorite', 'shopping_cart',
                           'download_shopping_cart',):
            return (IsAuthenticated(),)
        return (IsAuthenticatedOrReadOnly(),)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=('post', 'delete',), detail=True)
    def favorite(self, request, *args, **kwargs):
        favorite = FavoriteCartCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            Favorite,
            'Нельзя дважды добавить рецепт в избранное!',
            'Рецепт не в избранном!',
        )
        if request.method == 'POST':
            return favorite.create()
        return favorite.delete()

    @action(methods=('post', 'delete',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        cart_item = FavoriteCartCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            ShoppingCart,
            'Нельзя дважды добавить рецепт в корзине товаров!',
            'Рецепт не в корзине товаров!',
        )
        if request.method == 'POST':
            return cart_item.create()
        return cart_item.delete()

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        pdf_generator = ShoppingCartPdfGenerator()
        return pdf_generator.generate_pdf(request)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
