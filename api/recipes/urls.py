from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'recipes/tags', views.TagViewSet)

genericview_list_methods = {'get': 'list', 'post': 'create'}
genericview_detail_methods = {
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
}

urlpatterns = [
    # RECIPE
    path(
        'recipes/',
        views.RecipeViewSet.as_view(genericview_list_methods),
        name='recipe-list',
    ),
    path(
        'users/<author__username>/recipe/<slug>/',
        views.RecipeViewSet.as_view(genericview_detail_methods),
        name='recipe-detail',
    ),
    # IMAGE
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/images/',
        views.ImageViewSet.as_view(genericview_list_methods),
        name='image-list',
    ),
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/images/<pk>/',
        views.ImageViewSet.as_view(genericview_detail_methods),
        name='image-detail',
    ),
    # INGREDIENT
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/ingredients/',
        views.IngredientViewSet.as_view(genericview_list_methods),
        name='ingredient-list',
    ),
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/ingredients/<pk>/',
        views.IngredientViewSet.as_view(genericview_detail_methods),
        name='ingredient-detail',
    ),
    # STEPS
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/steps/',
        views.StepViewSet.as_view(genericview_list_methods),
        name='step-list',
    ),
    path(
        f'users/<recipe__author__username>/recipe/<recipe__slug>/steps/<pk>/',
        views.StepViewSet.as_view(genericview_detail_methods),
        name='step-detail',
    ),
]

urlpatterns += router.urls