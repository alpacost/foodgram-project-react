import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe,
                            RecipeIngredient, ShopList, Tag)
from users.models import Subscribe, User
from users.serializers import (SubscribeCustomUserSerializer,
                               UserRecipeSerializer)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsOwnerOrReadOnly, permissions
from .serializers import (IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class CreateListDeleteViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ('author',)

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[permissions.IsAuthenticated],
            url_path='favorite', url_name='favorite')
    def favorite(self, request, *args, **kwargs):
        target_recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user,
                                           recipe=target_recipe)
            serializer = UserRecipeSerializer(target_recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Favorite, user=request.user, recipe=target_recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        target_recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        if request.method == 'POST':
            ShopList.objects.get_or_create(user=request.user,
                                           recipe=target_recipe)
            serializer = UserRecipeSerializer(target_recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(ShopList,
                          user=request.user, recipe=target_recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(CreateListDeleteViewSet):
    serializer_class = SubscribeCustomUserSerializer

    def get_queryset(self):
        return User.objects.filter(
            pk__in=Subscribe.objects.filter(user=self.request.user))

    def get_object(self):
        return get_object_or_404(Subscribe,
                                 user=self.request.user,
                                 author=self.kwargs['pk'])


@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated])
def get_shoppinglist(request):
    shop_list = ShopList.objects.filter(user=request.user)
    shop_list = RecipeIngredient.objects.filter(
        recipe_name__in=shop_list.values_list('recipe', flat=True))
    unique_ingredient = shop_list.values_list('ingredient',
                                              flat=True).distinct()
    result = {}
    for ingredient in unique_ingredient:
        result[Ingredient.objects.get(pk=ingredient)] = sum(
            shop_list.filter(
                ingredient=ingredient).values_list('amount', flat=True))
    if os.path.exists(f'media/shopping_cart/{request.user.username}.txt'):
        os.remove(f'media/shopping_cart/{request.user.username}.txt')
    with open(f'media/shopping_cart/{request.user.username}.txt',
              'w', encoding='utf-8') as f:
        for ingredient in result:
            f.write(f'{ingredient.name} ({ingredient.measurement_unit}) '
                    f'- {result[ingredient]}')
            f.write('\n')
        f.close()
    with open(f'media/shopping_cart/{request.user.username}.txt',
              'r', encoding='utf-8') as f:
        file_data = f.read()
        return HttpResponse(file_data, content_type='text/plain')
