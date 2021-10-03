from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag,
                     Subscription, )
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer,
                          FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeIngredientsSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['update', 'create']:
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    class Meta:
        ordering = ['-pub_date']


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        queryset = Ingredient.objects.all()

        if name:
            queryset = queryset.filter(
                name__istartswith=name
            ).distinct('name')

        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeIngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeIngredientsSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    search_fields = ('name',)

    def get_queryset(self):
        pk = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=pk)
        return recipe.ingredients.all()


class GetAsCreateAndDeleteAPIView(APIView):
    """
    Base View for Favorite and ShoppingCart
    """
    permission_classes = (permissions.IsAuthenticated,)
    Model = None
    serializer_map = {
        FavoriteRecipe: FavoriteRecipeSerializer,
        ShoppingCart: ShoppingCartSerializer
    }

    def get(self, request, pk):
        data = dict(user=self.request.user.id, recipe=pk)

        if self.Model.objects.filter(**data).exists():
            return response.Response(
                "Ошибка: Рецепт уже добавлен", status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_map.get(self.Model)(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = self.request.user
        obj = get_object_or_404(self.Model, user=user, recipe=pk)
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteAPIView(GetAsCreateAndDeleteAPIView):
    Model = FavoriteRecipe


class ShoppingCartAPIView(GetAsCreateAndDeleteAPIView):
    Model = ShoppingCart


class SubscribeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        subscriber = self.request.user
        subscribe_data = {'subscriber': subscriber.id, 'author': pk}

        if Subscription.objects.filter(**subscribe_data).exists():
            return response.Response(
                'Ошибка: Вы уже подписаны на этого пользователя',
                status.HTTP_400_BAD_REQUEST
            )

        serializer = SubscriptionSerializer(
            data=subscribe_data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, pk):
        subscriber = self.request.user
        subscription = get_object_or_404(
            Subscription, subscriber=subscriber, author=pk
        )
        subscription.delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(mixins.ListModelMixin, GenericAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        subscriber = self.request.user
        queryset = Subscription.objects.filter(subscriber=subscriber)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
