from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from .models import Ingredient, Tag, Recipe
from .serializers import (IngredientSerializer,
                          TagSerializer,
                          RecipeSerializer,
                          RecipeIngredientSerializer)
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
