from rest_framework import serializers

from .models import Ingredient, ShoppingCart, Tag, Recipe, RecipeIngredients, \
    FavoriteRecipe, CustomUser
from djoser.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user
        recipe = obj
        return (
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user
        recipe = obj
        return (
            ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )

    class Meta:
        model = Recipe
        fields = '__all__'


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')


class RecipeForFavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = '__all__'
