# recipes/models.py
from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class BaseRecipeClass(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Ingredient(BaseRecipeClass):
    measurement_unit = models.CharField(
        verbose_name='Ед. измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(BaseRecipeClass):
    color = models.CharField(verbose_name='Цвет', max_length=200, null=True)
    slug = models.SlugField(verbose_name='Слаг', max_length=200, null=True)

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


Ingredient._meta.get_field('name').verbose_name = 'Название ингридиента'
Tag._meta.get_field('name').verbose_name = 'Название Тэга'
Recipe._meta.get_field('name').verbose_name = 'Название рецепта'


class Favorite(models.Model):
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)


class ShoppingCart(models.Model):
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)


class Follow(models.Model):
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        null=False,
        blank=True
    )
    following = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        null=False,
        blank=False
    )
