from django_filters.rest_framework import filters, FilterSet

from recipes.models import Favorite, Ingredient, Recipe, ShopList


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = (
            'name',
        )


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='get_is_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')
    tags = filters.CharFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
            'author'
        )

    def get_is_favorite(self, *args, **kwargs):
        if self.data.get('is_favorited'):
            recipes = Favorite.objects.filter(
                user=self.request.user).values_list('recipe')
            return Recipe.objects.filter(pk__in=recipes)
        return self.queryset

    def get_is_in_shopping_cart(self, *args, **kwargs):
        if self.data.get('is_in_shopping_cart'):
            recipes = ShopList.objects.filter(
                user=self.request.user).values_list('recipe')
            return Recipe.objects.filter(pk__in=recipes)
        return self.queryset
