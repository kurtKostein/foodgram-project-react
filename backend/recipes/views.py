from rest_framework import viewsets, permissions, pagination

from .models import Ingredient, Tag, Recipe
from .serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination.PageNumberPagination.page_size = 20
    search_fields = ('name',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    search_fields = ('name',)
