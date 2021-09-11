from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from django_filters import rest_framework as filters

from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeIngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagFilter(filters.FilterSet):  # Todo temporary here
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = TagFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        author = self.request.query_params.get('author')

        if author:
            queryset = queryset.filter(author__recipes=author)
        if is_in_shopping_cart:
            queryset = queryset.filter(shopping_cart__user=user)
        if is_favorited:
            queryset = queryset.filter(favorites__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action in ['update', 'create']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        queryset = Ingredient.objects.all()

        if name:
            queryset = queryset.filter(
                name__istartswith=name
            ).distinct('name')

        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    search_fields = ('name',)

    def get_queryset(self):
        pk = self.kwargs.get('recipe_id', )
        recipe = get_object_or_404(Recipe, pk=pk)
        return recipe.ingredients.all()

    def perform_create(self, serializer):  # TODO bulk create?
        ...


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class FavoriteViewSet(CreateDestroyViewSet):  # Todo delete if apiview
    pagination_class = None                   # will be stayed
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.favorites.all()

    def create(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe_id')
        user = self.request.user.id
        data = {'user': user, 'recipe': recipe}
        serializer = FavoriteRecipeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data,
            status.HTTP_201_CREATED,
            headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        ...


class FavoriteAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, recipe_id):
        user = self.request.user
        data = {'recipe': recipe_id, 'user': user.id}

        if FavoriteRecipe.objects.filter(user=user, recipe=recipe_id).exists():
            return response.Response(
                "Ошибка: Рецепт уже добавлен", status.HTTP_400_BAD_REQUEST
            )

        serializer = FavoriteRecipeSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        favorite = get_object_or_404(user.favorites, recipe=recipe_id)
        favorite.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartAPIView(APIView):  # TODO thinking about union with favorite
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, recipe_id):
        user = self.request.user
        data = {'recipe': recipe_id, 'user': user.id}

        if ShoppingCart.objects.filter(user=user, recipe=recipe_id).exists():
            return response.Response(
                "Ошибка: Рецепт уже добавлен в список покупок",
                status.HTTP_400_BAD_REQUEST
            )

        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        shopping_cart = get_object_or_404(user.shopping_cart, recipe=recipe_id)
        shopping_cart.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
