from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('tags', TagsViewSet, 'tags')

urlpatterns = [
    path('', include(router.urls))
]
