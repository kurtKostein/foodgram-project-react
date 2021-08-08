from rest_framework import viewsets

from .models import Ingredient, Tag
from .serializers import IngredientSerializer, TagSerializer
from .permissions import IsAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = IsAdminOrReadOnly
