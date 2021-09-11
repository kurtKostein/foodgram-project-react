from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet,
                    ShoppingCartAPIView, TagViewSet, FavoriteViewSet,
                    FavoriteAPIView)

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # path(
    #     'recipes/<int:recipe_id>/favorite/',
    #     FavoriteViewSet.as_view({'get': 'create', 'delete': 'destroy'}),
    #     name='favorite')
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteAPIView.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartAPIView.as_view(),
        name='shopping_cart'
    )
]

urlpatterns += router.urls
