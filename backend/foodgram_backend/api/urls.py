from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    SubscriptionViewSet, get_shoppinglist)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(r'users/subscriptions', SubscriptionViewSet.as_view({
        'get': 'list'}), name='subscriptions'),
    path(r'users/<int:pk>/subscribe', SubscriptionViewSet.as_view({
        'post': 'create', 'delete': 'destroy'}), name='subscriptions-change'),
    path('recipes/download_shopping_cart', get_shoppinglist),
]
