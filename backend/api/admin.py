from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Subscription, Tag)


@admin.register(ShoppingCart, Subscription)
class UserToUserRelationsAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    search_fields = ('^name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


class RecipeIngredientsAdmin(admin.TabularInline):
    model = RecipeIngredients
    fields = ('ingredient', 'amount')


class TagInlines(admin.TabularInline):
    verbose_name = Tag._meta.verbose_name
    verbose_name_plural = Tag._meta.verbose_name_plural
    model = Recipe.tags.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',  'author', 'favorited')
    list_filter = ('name', 'author')

    inlines = (RecipeIngredientsAdmin,)

    # noinspection PyMethodMayBeStatic
    def favorited(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'


# class IngredientAdmin(admin.ModelAdmin):
#     model = Ingredient
#     list_display = ('name', 'measurement_unit')
#     list_filter = ('name',)
#     search_fields = ('^name',)

#
# class RecipeIngredientsInline(admin.TabularInline):
#     model = RecipeIngredients

#
# class RecipeAdmin(admin.ModelAdmin):
#     model = Recipe
#     list_display = ('name', 'author', 'favorited')
#     list_filter = ('name', 'author', 'tags')
#     exclude = ('ingredients',)
#
#     inlines = (RecipeIngredientsInline,)
#
#     def favorited(self, obj):
#         favorited_count = FavoriteRecipe.objects.filter(recipe=obj).count()
#         return favorited_count
#
#     favorited.short_description = 'В избранном'
#

# class TagAdmin(admin.ModelAdmin):
#     model = Tag
#     list_display = ('name', 'color', 'slug')

#
# class ShoppingCartAdmin(admin.ModelAdmin):
#     model = ShoppingCart
#     list_display = ('user', 'recipe')
#

# class FavoriteRecipeAdmin(admin.ModelAdmin):
#     model = FavoriteRecipe
#     list_display = ('user', 'recipe')
#

# class SubscriptionAdmin(admin.ModelAdmin):
#     model = Subscription
#     list_display = ('author', 'subscriber')
#

# admin.site.register(Ingredient, IngredientAdmin)
# admin.site.register(Recipe, RecipeAdmin)
# admin.site.register(Tag, TagAdmin)
# admin.site.register(ShoppingCart, ShoppingCartAdmin)
# admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
# admin.site.register(Subscription, SubscriptionAdmin)
