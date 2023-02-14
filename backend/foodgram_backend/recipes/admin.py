from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe,
                     RecipeCharacteristic, ShopList, Subscribe, Tag)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeCharacteristic
    extra = 1
    fields = ('ingredients', 'ingredients_quantity',)
    verbose_name = 'Ингредиент'


class RecipeTagsInline(admin.StackedInline):
    model = RecipeCharacteristic
    extra = 1
    extra = 1
    fields = ('tags',)
    verbose_name = 'Тэг'


class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'text',
                    'cooking_time', 'image', )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'
    inlines = [RecipeIngredientInline, RecipeTagsInline]


class ShopListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipes',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class SubscribesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagsAdmin)
admin.site.register(Ingredient, IngredientsAdmin)
admin.site.register(Recipe, RecipesAdmin)
admin.site.register(ShopList, ShopListAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscribe, SubscribesAdmin)

