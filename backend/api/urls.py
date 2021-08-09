# from django.urls import include, path
from rest_framework import routers

from .views import IngredientViewSet, TagViewSet, RecipeViewSet, FavoriteRecipe


router = routers.DefaultRouter()
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'recipes/(?<recip_id>\d+)/favorites', FavoriteRecipe)

urlpatterns = router.urls
