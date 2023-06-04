from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Prefetch, Subquery
from django_filters import rest_framework
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.limit import PaginationLimit
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, TagSerializer)
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.helpers import FavoriteCreateDelete, ShoppingCartToPDF
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'recipe_id'
    pagination_class = PaginationLimit

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
                    ShoppingCart.objects.filter(
                        owner=user,
                        recipe=OuterRef('pk')
                    )))
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

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ('favorite', 'shopping_cart',
                           'download_shopping_cart',):
            return IsAuthenticated(),
        return IsAuthenticatedOrReadOnly(),

    @action(methods=('post', 'delete',), detail=True)
    def favorite(self, request, *args, **kwargs):
        favorite = FavoriteCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            Favorite,
            "Can't add to favorites twice",
            'The recipe is not in favorites',
        )
        if request.method == 'POST':
            return favorite.create()
        return favorite.delete()

    @action(methods=('post', 'delete',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        shopping_cart = FavoriteCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            ShoppingCart,
            "Can't add a recipe to your shopping cart twice",
            'The recipe is not in shopping cart',
        )
        if request.method == 'POST':
            return shopping_cart.create()
        return shopping_cart.delete()

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        pdf = ShoppingCartToPDF()
        return pdf.generate_pdf(request)


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
