from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, FavoriteViewSet)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet)
router.register('tags', TagViewSet)
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view({'get': 'create', 'delete': 'destroy'}),
        name='favorite')
]

urlpatterns += router.urls
