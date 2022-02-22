from api.models import Favorite, Ingredient, Recipe, ShopingCart, Tag
from django.contrib import admin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    search_fields = ("name", "slug")
    list_filter = ("id", "name", "slug")
    empty_value_display = "-NONE-"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("id", "name")
    empty_value_display = "-NONE-"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "author")
    search_fields = ("id", "name", "author", "tags")
    list_filter = ("id", "name")
    empty_value_display = "-NONE-"

    def count_favorite(self, obj):
        user = self.context["request"].user
        return Favorite.objects.filter(user=user, recipe=obj).count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("id", "user")
    list_filter = ("id", "user")
    empty_value_display = "-NONE-"


@admin.register(ShopingCart)
class ShopingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("id", "user")
    list_filter = ("id", "user")
    empty_value_display = "-NONE-"
