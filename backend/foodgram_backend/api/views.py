import io

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, ShopList, Tag
from users.models import Subscribe, User
from users.serializers import SubscribeCustomUserSerializer
from .filters import IngredientFilter, RecipeFilter
from .mixins import CreateListDeleteViewSet
from .permissions import IsOwnerOrReadOnly, permissions
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
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
