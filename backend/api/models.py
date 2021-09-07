#  api/models.py
from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import CustomUser


class BaseRecipeClass(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Ingredient(BaseRecipeClass):
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(BaseRecipeClass):
    color = ColorField('Цвет тэга', default='#3399FF', null=True)
    slug = models.CharField('Слаг', max_length=200, unique=True, null=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(BaseRecipeClass):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        to='Ingredient',
        through='RecipeIngredients',
        related_name='recipes'
    )
    tags = models.ManyToManyField(to='Tag', related_name='recipes')
    image = models.ImageField(upload_to='media/', verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(to='Ingredient', on_delete=models.CASCADE)
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[MinValueValidator(1)]
    )


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
        default_related_name = 'favorites'


class ShoppingCart(UserRecipeRelations):

    class Meta:
        default_related_name = 'shopping_cart'
