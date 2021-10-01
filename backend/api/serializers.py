from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer

from .models import (
    Ingredient, ShoppingCart, Tag, Recipe, RecipeIngredients, FavoriteRecipe,
    CustomUser, Subscription,
)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=request.user, author=obj
        ).exists()

    class Meta:
        model = CustomUser
        fields = (
            'email', 'username', 'id',
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
    ingredients = serializers.SerializerMethodField()
    # ingredients = RecipeIngredientsSerializer()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(instance=queryset, many=True).data

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user.id
        recipe = obj
        return (
            FavoriteRecipe.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, obj) -> bool:
        request = self.context.get('request')
        user = request.user.id
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


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(method_name='get_image')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url)


class UserRecipeRelationsSerializer(serializers.ModelSerializer):
    """
    Base serializer for Favorite and ShoppingCart serializers
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        abstract = True

    def to_representation(self, instance):
        request = self.context.get('request')
        recipes = RecipeMinifiedSerializer(
            instance.recipe,
            context={'request': request}
        )
        return recipes.data


class FavoriteRecipeSerializer(UserRecipeRelationsSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingCartSerializer(UserRecipeRelationsSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Subscription
        fields = ('subscriber', 'author')

    def to_representation(self, instance):
        request = self.context.get('request')
        instance_recipes = instance.author.recipes.all()
        limit = request.query_params.get('recipes_limit')

        if limit is not None:
            instance_recipes = instance_recipes[:int(limit)]

        author = CustomUserSerializer(
            instance.author, context={'request': request}
        )
        recipes = RecipeMinifiedSerializer(
            many=True,
            instance=instance_recipes,
            context={'request': request}
        )
        recipes_count = instance.author.recipes.count()

        return {
            **author.data,
            'recipes': recipes.data,
            'recipes_count': recipes_count
        }
