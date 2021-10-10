#  api/serializers.py
from django.db import transaction
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Subscription, Tag)
from users.models import CustomUser


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            subscriber=request.user, author=obj).exists()

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
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    # noinspection PyMethodMayBeStatic
    def get_ingredients(self, obj):
        queryset = RecipeIngredients.objects.filter(recipe=obj)
        return RecipeIngredientsSerializer(instance=queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=request.user.id, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author', 'ingredients', 'tags', 'image', 'text',
            'cooking_time', 'is_favorited', 'is_in_shopping_cart',
        )


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CreateRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all().values_list(
            'id', flat=True)
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = CreateRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    # noinspection PyMethodMayBeStatic
    def _set_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient = ingredient.get('ingredient')

            if RecipeIngredients.objects.filter(
                    recipe=recipe, ingredient=ingredient
            ).exists():
                amount += F('amount')

            if amount < 1:
                raise serializers.ValidationError(
                    'Значение не может быть меньше 1'
                )

            RecipeIngredients.objects.update_or_create(
                recipe=recipe, ingredient_id=ingredient,
                defaults={'amount': amount}
            )

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        self._set_ingredients(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            RecipeIngredients.objects.filter(recipe=instance).delete()
            self._set_ingredients(ingredients, instance)

        return instance

    def to_representation(self, instance):
        recipes = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return recipes.data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Class for minified Recipe representation.
    """
    image = serializers.SerializerMethodField(method_name='get_image')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)


class UserRecipeRelationsSerializer(serializers.ModelSerializer):
    """
    Base serializer for Favorite and ShoppingCart serializers.
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
