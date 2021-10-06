#  api/models.py
from django.core.validators import MinValueValidator
from django.db import models, transaction

from colorfield.fields import ColorField

from foodgram import settings
from users.models import CustomUser


class BaseRecipeClass(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Ingredient(BaseRecipeClass):
    measurement_unit = models.CharField('Ед. измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(BaseRecipeClass):
    color = ColorField('Цвет тэга', default='#3399FF', null=True, unique=True)
    slug = models.CharField('Слаг', max_length=200, null=True, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class RecipeManager(models.Manager):

    @staticmethod
    def _set_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient = ingredient.get('ingredient')
            RecipeIngredients.objects.update_or_create(
                recipe=recipe, ingredient_id=ingredient,
                defaults={'amount': amount}
            )

    @transaction.atomic
    def create(self, author, ingredients, tags, **validated_data):
        recipe = Recipe(author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags)
        self._set_ingredients(ingredients, recipe)

        return recipe

    # @transaction.atomic
    # def update(self, instance, validated_data):
        # instance.name = validated_data.get('name', instance.name)
        # instance.text = validated_data.get('text', instance.text)
        # instance.cooking_time = validated_data.get(
        #     'cooking_time', instance.cooking_time
        # )
        # instance.image = validated_data.get('image', instance.image)
        # instance.save()
        #
        # if 'tags' in self.initial.data:
        #     tags = validated_data.pop('tags')
        #     instance.tags.set(tags)
        #
        # if 'ingredients' in self.initial.data:
        #     ingredients = validated_data.pop('ingredients')
        #     instance.ingredients.clear()
        #     self._set_ingredients(ingredients, instance)
        #
        # return instance


class Recipe(BaseRecipeClass):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты рецепта',
        to='Ingredient',
        through='RecipeIngredients',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        verbose_name='Тэги рецепта',
        to='Tag',
        related_name='recipes'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='media'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        default=1,
        validators=[MinValueValidator(1)]
    )

    objects = RecipeManager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(
        verbose_name='Ингредиенты',
        to='Ingredient',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        verbose_name='Рецепт',
        to='Recipe',
        on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'


class UserRecipeRelations(models.Model):
    """
    Base class for Favorite and ShoppingCart models
    """
    user = models.ForeignKey(
        to='users.CustomUser',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_is_unique'
            )
        ]
        abstract = True


class FavoriteRecipe(UserRecipeRelations):
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(UserRecipeRelations):
    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        default_related_name = 'shopping_cart'


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers'  # TODO check naming!
    )
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    class Meta:
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'author'],
                                    name='unique_subscriptions')
        ]
