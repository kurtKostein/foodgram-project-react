from django.db import models

from users.models import CustomUser
from recipes.models import Recipe


class Favorite(models.Model):
    ...


class ShoppingCart(models.Model):
    ...


class Follow(models.Model):
    ...
