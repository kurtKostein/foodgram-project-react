from django.contrib import admin

from .models import (FavoriteRecipe, Subscription, Ingredient,
                     RecipeIngredients, ShoppingCart, Recipe, Tag)


class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('^name',)


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredients


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_display = ('name', 'author', 'favorited')
    list_filter = ('name', 'author', 'tags')
    exclude = ('ingredients',)

    inlines = (RecipeIngredientsInline,)

    def favorited(self, obj):
        favorited_count = FavoriteRecipe.objects.filter(recipe=obj).count()
        return favorited_count

    favorited.short_description = 'В избранном'


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'color', 'slug')


class ShoppingCartAdmin(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('user', 'recipe')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    model = FavoriteRecipe
    list_display = ('user', 'recipe')


class SubscriptionAdmin(admin.ModelAdmin):
    model = Subscription
    list_display = ('author', 'subscriber')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
