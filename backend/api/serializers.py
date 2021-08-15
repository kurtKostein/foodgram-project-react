from rest_framework import serializers

from .models import Ingredient, Tag, Recipe, RecipeIngredients, FavoriteRecipe
from djoser.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        recipe = obj
        return (
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists()
        )

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeForFavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.RelatedField(read_only=True)
    recipe = RecipeForFavoritesSerializer(many=True)

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
