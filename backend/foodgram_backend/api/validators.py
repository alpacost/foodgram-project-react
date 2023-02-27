from rest_framework import serializers

from recipes.models import Ingredient


def ingredients_validator(ingredients):
    if not ingredients:
        raise serializers.ValidationError('Нужен как минимум один ингредиент')
    for ingredient in ingredients:
        if not Ingredient.objects.filter(pk=ingredient).exists():
            raise serializers.ValidationError(
                f"Ингредиента с id {ingredient} не существует")
    return ingredients
