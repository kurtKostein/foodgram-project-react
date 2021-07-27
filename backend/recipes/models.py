from django.db import models


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Ингридиент', max_length=255)
    measurement_unit = models.CharField(
        verbose_name='Ед. измерения',
        max_length=15
    )


class Tag(models.Model):
    ...


class Recipe(models.Model):
    ...
