from rest_framework import serializers

from recipes.models import Favorite
from recipes.models import Ingredient
from recipes.models import Recipe
from recipes.models import RecipeIngredient
from recipes.models import ShopList
from recipes.models import Tag
from users.serializers import CustomUserSerializer
from .fields import Base64ImageField
from .validators import ingredients_validator
from .utils import add_ingredient


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )
        extra_kwargs = {'namer': {'required': True},
                        'color': {'required': True},
                        'slug': {'required': True}}


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


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='ingredient_set')
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

    def validate(self, attrs):
        ingredient_list = []
        for item in attrs['ingredient_set']:
            if list(item.values())[0]['id'] in ingredient_list:
                raise serializers.ValidationError(
                    'Все ингредиенты должны быть уникальны')
            ingredient_list.append(list(item.values())[0]['id'])
        ingredients_validator(ingredient_list)
        return attrs

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        add_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredient_set' in validated_data.keys():
            ingredients = validated_data.pop('ingredient_set')
            RecipeIngredient.objects.filter(recipe_name=instance.pk).delete()
            add_ingredient(instance, ingredients)
        if 'tags' in validated_data.keys():
            tags_list = self.context['request'].data['tags']
            instance.tags.set(Tag.objects.filter(pk__in=tags_list))
        instance.save()
        return super().update(instance, validated_data)


class RecipeSerializer(CreateRecipeSerializer):
    tags = TagSerializer(many=True)

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
