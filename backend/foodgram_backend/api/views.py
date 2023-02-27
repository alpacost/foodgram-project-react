import io

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response

from recipes.models import Favorite
from recipes.models import Ingredient
from recipes.models import Recipe
from recipes.models import RecipeIngredient
from recipes.models import ShopList
from recipes.models import Tag
from users.models import Subscribe
from users.models import User
from users.serializers import SubscribeCustomUserSerializer
from .filters import IngredientFilter
from .filters import RecipeFilter
from .mixins import CreateListDeleteViewSet
from .permissions import IsOwnerOrReadOnly
from .permissions import permissions
from .serializers import CreateRecipeSerializer
from .serializers import IngredientSerializer
from .serializers import RecipeSerializer
from .serializers import TagSerializer
from .utils import favorite_shopping_cart


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
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ('author',)

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(instance,
                                               context={'request': request})
        return Response(instance_serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        value = self.perform_update(serializer)
        instance_serializer = RecipeSerializer(
            value, context={'request': request})
        return Response(instance_serializer.data,
                        status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        return serializer.update(
            serializer.instance, serializer.validated_data)

    def perform_create(self, serializer):
        return serializer.save()

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[permissions.IsAuthenticated],
            url_path='favorite', url_name='favorite')
    def favorite(self, request, *args, **kwargs):
        target_recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return favorite_shopping_cart(request, Favorite, target_recipe)

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart', url_name='shopping_cart')
    def shopping_cart(self, request, *args, **kwargs):
        target_recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return favorite_shopping_cart(request, ShopList, target_recipe)


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
    result = (Ingredient.objects.filter(
        pk__in=shop_list.values_list('ingredient', flat=True))).annotate(
        amount_sum=Sum('ingredient_recipe__amount')).distinct()
    f = io.StringIO()
    for ingredient in result:
        f.write(f'{ingredient.name} ({ingredient.measurement_unit}) '
                f'- {ingredient.amount_sum}')
        f.write('\n')
    file_data = f.getvalue()
    f.close()
    return HttpResponse(file_data, content_type='text/plain')
