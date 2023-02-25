import base64
from django.core.files.base import ContentFile
from recipes.models import (Recipe, Tag, Ingredient,
                            Favorite, ShopList, RecipeIngredient)
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from .validators import ingredients_validator, tags_validator


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            form, imgstr = data.split(';base64,')
            ext = form.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True,)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            RecipeIngredient.objects.filter(recipe_name=obj), many=True).data

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return Favorite.objects.filter(user=self.context['request'].user,
                                       recipe=obj).exists()

    def get_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return ShopList.objects.filter(user=self.context['request'].user,
                                       recipe=obj).exists()

    def create(self, validated_data):
        ingredient_list = self.context['request'].data['ingredients']
        ingredients_validator(ingredient_list)
        tags = self.context['request'].data['tags']
        tags_validator(tags)
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe_id = recipe.pk
        recipe.tags.set(Tag.objects.filter(pk__in=tags))
        for ingredient in ingredient_list:
            RecipeIngredient.objects.create(
                recipe_name=Recipe.objects.get(pk=recipe_id),
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            )
        recipe.ingredient_sort()
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in self.context['request'].data.keys():
            ingredient_list = self.context['request'].data['ingredients']
            ingredients_validator(ingredient_list)
            RecipeIngredient.objects.filter(recipe_name=instance.pk).delete()
            for ingredient in ingredient_list:
                RecipeIngredient.objects.create(
                    recipe_name=Recipe.objects.get(pk=instance.pk),
                    ingredient=Ingredient.objects.get(pk=ingredient['id']),
                    amount=ingredient['amount']
                )
            instance.ingredient_sort()
        if 'tags' in self.context['request'].data.keys():
            tags_list = self.context['request'].data['tags']
            tags_validator(tags_list)
            instance.tags.set(Tag.objects.filter(pk__in=tags_list))
        instance.save()
        return super().update(instance, validated_data)
