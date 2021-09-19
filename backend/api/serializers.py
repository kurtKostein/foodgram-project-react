from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer

from .models import (
    Ingredient, ShoppingCart, Tag, Recipe, RecipeIngredients, FavoriteRecipe,
    CustomUser
)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj) -> bool:
        # request = self.context.get('request')
        user = obj
        return False

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

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
        fields = (
            'id', 'name', 'author', 'ingredients', 'tags', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            curr_ing = get_object_or_404(Ingredient, id=ingredient['id'])
            RecipeIngredients.objects.create(
                recipe=recipe, ingredient=curr_ing, amount=ingredient['amount']
            )

        return recipe


class RecipeForFavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    # recipe = RecipeForFavoritesSerializer()

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

    def to_representation(self, instance):
        request = self.context.get('request')
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': request.build_absolute_uri(instance.recipe.image),
            'cooking_time': instance.recipe.cooking_time
        }


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = '__all__'
