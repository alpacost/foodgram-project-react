from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient
from users.serializers import UserRecipeSerializer


def add_ingredient(recipe, ingredients):
    ingredient_list = []
    for ingredient in ingredients:
        ingredient_list.append(RecipeIngredient(
            recipe_name=Recipe.objects.get(pk=recipe.pk),
            ingredient=Ingredient.objects.get(
             pk=list(ingredient.values())[0]['id']),
            amount=list(ingredient.values())[1]
        ))
    RecipeIngredient.objects.bulk_create(ingredient_list)


def favorite_shopping_cart(request, instance, target_recipe):
    if request.method == 'POST':
        instance.objects.get_or_create(user=request.user,
                                       recipe=target_recipe)
        serializer = UserRecipeSerializer(target_recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    get_object_or_404(
        instance, user=request.user, recipe=target_recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
