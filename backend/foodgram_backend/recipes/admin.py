from django.contrib import admin

from users.models import Subscribe
from .models import (Favorite, Ingredient, Recipe,
                     RecipeIngredient, ShopList, Tag)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    fk_name = 'recipe_name'
    extra = 1
    fields = ('ingredient', 'amount',)
    verbose_name = 'Ингредиент'


class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('name', 'author', 'tags')
    filter_horizonta = ('tags',)
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientInline, ]

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class SubscribesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(RecipeIngredient)
admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(ShopList, ShopListAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribesAdmin)
