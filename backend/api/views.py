from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import views, status

from api.permissions import AdminOwnerReadOnly
from api.serializers import (FavoriteSerializer, IngredientSerializer,
                               RecipeSerializer, RecipeCreateSerializer,
                               ShoppingCartSerializer, TagSerializer)
from api.limit import PaginationLimit
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (ShoppingCart, Favorite, Ingredient, Recipe,
                              RecipeIngredient, Tag)


User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminOwnerReadOnly,)
    pagination_class = PaginationLimit
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_queryset(self):
        queryset = Recipe.objects
        user = self.request.user
        queryset = queryset.add_user_annotation(user.pk)
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(is_in_shopping_cart=True)

        return queryset


class FavoriteView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        user = request.user
        data = {
            'user': user.id,
            'recipe': pk,
        }
        context = {'request': request}
        serializer = FavoriteSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartView(views.APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        owner = request.user
        data = {
            'owner': owner.id,
            'recipe': pk,
        }
        context = {'request': request}
        serializer = ShoppingCartSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        owner = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingCart.objects.filter(owner=owner, recipe=recipe).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartDownloadView(views.APIView):
    def get(self, request):
        items = RecipeIngredient.objects.select_related(
            'recipe', 'ingredient'
        )
        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session['purchases']
            )

        items = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename{filename}'

        return response


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOwnerReadOnly,)
