from rest_framework import serializers
from recipes.models import Ingredient, Tag


def ingredients_validator(ingredients):
    if not ingredients:
        raise serializers.ValidationError('Нужен как минимум один ингредиент')
    for ingredient in ingredients:
        if not Ingredient.objects.filter(pk=ingredient['id']).exists():
            raise serializers.ValidationError(
                f"Ингредиента с id {ingredient['id']} не существует")
    return ingredients


def tags_validator(tags):
    if not tags:
        raise serializers.ValidationError('Нужен как минимум один тэг')
    for tag in tags:
        if not Tag.objects.filter(pk=tag).exists():
            raise serializers.ValidationError(f"Тэга с id {tag} не существует")
    return tags
