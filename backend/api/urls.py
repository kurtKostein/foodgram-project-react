from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = []

urlpatterns += router.urls
