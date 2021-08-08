from django.contrib import admin
from .models import Ingredient, Tag, Recipe, RecipeIngredients

admin.site.register(Ingredient)
admin.site.register(Tag)


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredients
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    inlines = (IngredientsInline,)


admin.site.register(Recipe, RecipeAdmin)