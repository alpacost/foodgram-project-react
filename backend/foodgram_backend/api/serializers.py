from rest_framework import serializers

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShopList, Tag)
from users.serializers import CustomUserSerializer
from .fields import Base64ImageField
from .utils import add_ingredient
from .validators import ingredients_validator


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
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredient')
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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['tags'] = TagSerializer(instance.tags, many=True).data
        return ret

    def validate(self, attrs):
        ingredient_list = []
        for item in attrs['recipe_ingredient']:
            item = [i for i in item.values()]
            if item[0]['id'] in ingredient_list:
                raise serializers.ValidationError(
                    'Все ингредиенты должны быть уникальны')
            ingredient_list.append(item[0]['id'])
        ingredients_validator(ingredient_list)
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        add_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'recipe_ingredient' in validated_data.keys():
            ingredients = validated_data.pop('recipe_ingredient')
            RecipeIngredient.objects.filter(recipe_name=instance.pk).delete()
            add_ingredient(instance, ingredients)
        if 'tags' in validated_data.keys():
            tags_list = validated_data.pop('tags')
            instance.tags.set(tags_list)
        instance.save()
        return super().update(instance, validated_data)
