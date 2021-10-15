#  api/urls.py
from django.urls import path
from rest_framework import routers

from .views import (FavoriteAPIView, IngredientViewSet, RecipeViewSet,
                    ShoppingCartAPIView, SubscribeAPIView, SubscriptionsView,
                    TagViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

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

urlpatterns += router_v1.urls
