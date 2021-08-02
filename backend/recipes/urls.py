from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, 'ingredient')
router.register('tags', TagsViewSet, 'tag')
router.register('recipe', RecipeViewSet, 'recipe')

urlpatterns = [
    path('', include(router.urls))
]
