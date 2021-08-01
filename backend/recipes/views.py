from rest_framework import viewsets, permissions

from .models import Ingredient, Tag
from .serializers import IngredientSerializer, TagSerializer
from .permissions import IsAdminOrReadOnly


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    search_fields = ('name',)
