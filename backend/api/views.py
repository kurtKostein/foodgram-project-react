#  api/views.py
from django.db.models import Sum
from django.shortcuts import HttpResponse
from django.utils import timezone
from rest_framework import mixins, permissions, response, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.views import APIView

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredients, ShoppingCart,
    Subscription, Tag,
)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CreateUpdateRecipeSerializer, FavoriteRecipeSerializer,
    IngredientSerializer, RecipeIngredientsSerializer, RecipeSerializer,
    ShoppingCartSerializer, SubscriptionSerializer, TagSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        user = self.request.user
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping = self.request.query_params.get('is_in_shopping')
        author = self.request.query_params.get('author')

        if is_favorited is not None:
            queryset = queryset.filter(favorites__user=user)

        if is_in_shopping is not None:
            queryset = queryset.filter(shopping_cart__user=user)

        if author is not None:
            queryset = queryset.filter(author=author)

        return queryset.order_by('-id')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

    @action(detail=False, permission_classes=(IsAuthorOrAdminOrReadOnly,))
    def download_shopping_cart(self, request):
        user = request.user
        cart = RecipeIngredients.objects.filter(
            recipe__shopping_cart__user=user
        ).annotate(_amount=Sum('amount')).values_list(
            'ingredient__name', '_amount', 'ingredient__measurement_unit',
        )
        data = [f'Список покупок на {timezone.now().date()}\n\n']
        for item in cart:
            data.append(f'{item[0]}: {item[1]}{item[2]}\n')
        return HttpResponse(data, {
            'content_type': 'text/plain',
            'Content-Disposition': 'attachment; filename="shopping_list.txt"'
        })


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        queryset = Ingredient.objects.all()

        if name:
            queryset = queryset.filter(name__istartswith=name).distinct('name')

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
    serializer_map = {
        FavoriteRecipe: FavoriteRecipeSerializer,
        ShoppingCart: ShoppingCartSerializer
    }

    def get(self, request, pk):
        data = dict(user=self.request.user.id, recipe=pk)

        if self.Meta.model.objects.filter(**data).exists():
            return response.Response(
                "Ошибка: Рецепт уже добавлен", status.HTTP_400_BAD_REQUEST
            )

        serializer = self.Meta.serializer_class(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = self.request.user
        obj = get_object_or_404(self.Meta.model, user=user, recipe=pk)
        obj.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    class Meta:
        model = None
        serializer_class = None
        abstract = True


class FavoriteAPIView(GetAsCreateAndDeleteAPIView):

    class Meta:
        model = FavoriteRecipe
        serializer_class = FavoriteRecipeSerializer


class ShoppingCartAPIView(GetAsCreateAndDeleteAPIView):

    class Meta:
        serializer_class = ShoppingCartSerializer
        model = ShoppingCart


class SubscribeAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        subscriber = self.request.user
        data = dict(subscriber=subscriber.id, author=pk)

        if Subscription.objects.filter(**data).exists():
            return response.Response(
                'Ошибка: Вы уже подписаны на этого пользователя',
                status.HTTP_400_BAD_REQUEST
            )

        serializer = SubscriptionSerializer(
            data=data, context={'request': request}
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
