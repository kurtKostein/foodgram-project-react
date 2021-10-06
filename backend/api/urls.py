from django.urls import path
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet,
                    ShoppingCartAPIView,
                    SubscriptionsView, TagViewSet,
                    FavoriteAPIView, SubscribeAPIView, )

router = routers.DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/<int:pk>/favorite/',
        FavoriteAPIView.as_view(),
        name='favorite'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingCartAPIView.as_view(),
        name='shopping_cart'
    ),
    path(
        'users/<int:pk>/subscribe/',
        SubscribeAPIView.as_view(),
        name='subscription'
    ),
    path('users/subscriptions/', SubscriptionsView.as_view(),)
]

urlpatterns += router.urls
