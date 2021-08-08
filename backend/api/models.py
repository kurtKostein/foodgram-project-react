#  api/models.py
from django.db import models

from colorfield.fields import ColorField


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
    ...
