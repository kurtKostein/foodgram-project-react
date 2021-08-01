from rest_framework import viewsets

from .models import Ingredient
from .serializers import IngredientSerializer
from .permissions import IsAdminOrReadOnly


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)

