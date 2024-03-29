from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers

from foodgram_backend.pagination import CustomPageNumberPagination
from recipes.models import Recipe
from .models import Subscribe, User


class CustomUserSerializer(UserSerializer, CustomPageNumberPagination):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, target_user):
        if self.context['request'].user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=self.context['request'].user,
                                        author=target_user).exists()


class UserRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )


class SubscribeCustomUserSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='count_recipes')

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count',
                  )
        read_only_fields = ('email',
                            'id',
                            'username',
                            'first_name',
                            'last_name',
                            'is_subscribed'
                            )

    def validate(self, attrs):
        if self.context['request'].user == get_object_or_404(
                User, pk=self.context['view'].kwargs['pk']):
            raise serializers.ValidationError('Нельзя подписаться на себя')
        return attrs

    def create(self, validated_data):
        target_user = get_object_or_404(User,
                                        pk=self.context['view'].kwargs['pk'])
        Subscribe.objects.get_or_create(
            user=self.context['request'].user,
            author=target_user
        )
        return target_user

    def get_recipes(self, target_user):
        if self.context['request'].GET.get('recipes_limit'):
            limit = int(self.context['request'].GET.get('recipes_limit'))
        else:
            limit = None
        result = UserRecipeSerializer(Recipe.objects.filter(
            author=target_user), many=True).data
        return result[:limit]

    def count_recipes(self, target_user):
        return Recipe.objects.filter(author=target_user).count()
