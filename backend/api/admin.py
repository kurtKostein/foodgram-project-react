from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Subscription, Tag)


class TagInlines(admin.TabularInline):
    model = Recipe.tags.through
    verbose_name = 'Тэг рецепта'
    verbose_name_plural = 'Тэги рецепта'
    extra = 1


class RecipeIngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    fields = ('ingredient', 'amount')
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    fields = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('^name',)


@admin.register(ShoppingCart, Subscription)
class UserToUserRelationsAdmin(admin.ModelAdmin):
    pass


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorited')
    list_filter = ('name', 'author')
    exclude = ('tags',)

    inlines = (TagInlines, RecipeIngredientsInline)

    # noinspection PyMethodMayBeStatic
    def favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'
