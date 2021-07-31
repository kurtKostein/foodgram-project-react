# recipes/models.py
from django.db import models

from ..users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингридиент', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Ед. измерения',
        max_length=200
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Тэг', max_length=200)
    color = models.CharField(verbose_name='Цвет', max_length=200, null=True)
    slug = models.SlugField(verbose_name='Слаг', max_length=200, null=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        to='CustomUser',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        to='Ingredient',
        through='RecipeIngredients',
    )
    tags = models.ManyToManyField(to='Tag', related_name='recipe_tag')
    image = models.BinaryField()
    name = models.CharField()
    text = models.TextField()
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        default=1
    )

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient = models.ForeignKey(to='Ingredient', on_delete=models.CASCADE)
    recipe = models.ForeignKey(to='Recipe', on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Количество')
