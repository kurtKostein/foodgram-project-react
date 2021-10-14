#  api/models.py
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from foodgram import settings


class BaseRecipeClass(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Ingredient(BaseRecipeClass):
    MEASUREMENT_UNIT_LIST = [
        (1, 'л'), (2, 'бутылка'), (3, 'зубчик'), (4, 'щепотка'), (5, 'пачка'),
        (6, 'пучок'), (7, 'банка'), (8, 'веточка'), (9, 'стакан'), (10, 'кг'),
        (11, 'стручок'), (12, 'шт.'), (13, 'пласт'), (14, 'звездочка'),
        (15, 'тушка'), (16, 'батон'), (17, 'упаковка'), (18, 'мл'), (19, 'г'),
        (20, 'пакетик'), (21, 'горсть'), (22, 'кусок'), (23, 'по вкусу'),
        (24, 'г.'), (25, 'стебель'), (26, 'ст. л.'), (27, 'капля'),
        (28, 'пакет'), (29, 'долька'), (30, 'ч. л.'), (31, 'лист'),
    ]

    measurement_unit = models.CharField(
        'Ед. измерения', max_length=200,
        choices=MEASUREMENT_UNIT_LIST,
        default=19
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(BaseRecipeClass):
    color = ColorField('Цвет тэга', default='#3399FF', null=True, unique=True)
    slug = models.CharField('Слаг', max_length=50, null=True, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


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
        validators=[
            MinValueValidator(1, message='Значение не может быть меньше 1')
        ]
    )

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
        validators=[
            MinValueValidator(1, message='Значение не может быть меньше 1')
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

        def __str__(self):
            return self.verbose_name


class UserRecipeRelations(models.Model):
    """
    Base class for Favorite and ShoppingCart models
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to='Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_is_unique'
            ),
        )
        abstract = True

    def __str__(self):
        return (f'{self._meta.verbose_name} пользователя {self.user} '
                f'рецепт: {self.recipe.name}')


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
        verbose_name='Подписчик',
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    author = models.ForeignKey(
        verbose_name='Автор рецепта',
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(fields=('subscriber', 'author'),
                                    name='unique_subscriptions'),
        )

    def __str__(self):
        return f'{self._meta.verbose_name} {self.subscriber} на {self.author}'
