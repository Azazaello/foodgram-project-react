from django.contrib import admin

from .models import (Basket, Favorite, Ingredient, IngredientInRecipe, Recipe,
                     Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):

    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name", "slug")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id',"name", "author", "tags", "favorite")
    list_filter = ("name", "author", "tags")
    search_fields = ("name", "author")
    readonly_fields = ("favorite",)

    def tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    tags.short_description = "Теги"

    def favorite(self, obj):
        return obj.favorite.count()

    favorite.short_description = "B избранном"


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    search_fields = ("recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient",)

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    search_fields = ("user", "recipe")
    list_filter = ("user", "recipe",)


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    search_fields = ("user", "recipe")
