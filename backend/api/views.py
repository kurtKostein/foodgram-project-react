from rest_framework import viewsets, mixins, permissions, status, response
from rest_framework.generics import get_object_or_404


from .models import Ingredient, Tag, Recipe
from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeIngredientSerializer,
    CreateUpdateRecipeSerializer,
    FavoriteRecipeSerializer,
)
from .permissions import IsAuthorOrAdminOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['update', 'retrieve']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    search_fields = ('name',)

    def get_queryset(self):
        pk = self.kwargs.get('review_id',)
        recipe = get_object_or_404(Recipe, pk=pk)
        return recipe.ingredients.all()

    def perform_create(self, serializer):
        serializer.save(
            recipe=get_object_or_404(
                Recipe, pk=self.kwargs.get('recipe_id')
            )
        )


class CreateDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass


class FavoriteViewSet(CreateDestroyViewSet):
    pagination_class = None
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        user = self.request.user
        return user.favorites.all()

    def create(self, request, *args, **kwargs):
        recipe = self.kwargs.get('recipe_id')
        user = self.request.user.id
        data = {'user': user, 'recipe': recipe}
        serializer = FavoriteRecipeSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        ...
