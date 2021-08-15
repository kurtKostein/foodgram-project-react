from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404


from .models import Ingredient, Tag, Recipe, FavoriteRecipe
from users.models import CustomUser
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    FavoriteRecipeSerializer,
    RecipeForFavoritesSerializer,
)
from .permissions import IsAuthorOrAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=(IsAuthorOrAdminOrReadOnly,)  # TODO need IsOwner
    )
    def favorite(self, request, **kwargs):
        recipe = self.get_object()
        user = self.request.user
        if request.method == 'GET':
            favor = FavoriteRecipe.objects.create(recipe=recipe, user=user)
            favor.save()
            serializer = RecipeForFavoritesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favor = get_object_or_404(FavoriteRecipe, recipe=recipe, user=user)
            favor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    search_fields = ('name',)

    def get_queryset(self):
        recipe_id = self.kwargs.get('review_id',)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        return recipe.ingredients.all()

    def perform_create(self, serializer):
        serializer.save(
            recipe=get_object_or_404(
                Recipe, pk=self.kwargs.get('recipe_id')
            )
        )


class RetrieveDestroyViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
