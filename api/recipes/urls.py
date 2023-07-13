from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'tags', views.TagViewSet)

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
        '',
        views.RecipeViewSet.as_view(genericview_list_methods),
        name='recipe-list',
    ),
    path(
        '<slug:slug>-<uuid:id>/',
        views.RecipeViewSet.as_view(genericview_detail_methods),
        name='recipe-detail',
    ),
    # IMAGE
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/images/',
        views.ImageViewSet.as_view(genericview_list_methods),
        name='image-list',
    ),
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/images/<uuid:pk>/',
        views.ImageViewSet.as_view(genericview_detail_methods),
        name='image-detail',
    ),
    # INGREDIENT
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/ingredients/',
        views.IngredientViewSet.as_view(genericview_list_methods),
        name='ingredient-list',
    ),
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/ingredients/<uuid:pk>/',
        views.IngredientViewSet.as_view(genericview_detail_methods),
        name='ingredient-detail',
    ),
    # STEPS
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/steps/',
        views.StepViewSet.as_view(genericview_list_methods),
        name='step-list',
    ),
    path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/steps/<uuid:pk>/',
        views.StepViewSet.as_view(genericview_detail_methods),
        name='step-detail',
    ),
        path(
        f'<slug:recipe__slug>-<uuid:recipe__id>/steps/<uuid:pk>/change-order/',
        views.StepViewSet.as_view({'post':'change_order'}),
    ),
]

urlpatterns += router.urls
