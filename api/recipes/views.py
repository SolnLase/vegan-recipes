from django.db.models import F

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser

from django_filters.rest_framework import DjangoFilterBackend

from . import serializers
from recipes import models
from api import permissions as custom_permissions
from api.mixins import MultipleFieldLookupMixin, MultipleFieldQuerysetMixin


class RecipeViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.all()
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
        custom_permissions.IsEmailConfirmed,
    )
    multiple_lookup_fields = ('author__username', 'slug')
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ('tags',)
    search_fields = ('=author__username', 'title', 'ingredients__name', 'tags__name')
    ordering_fields = ('created', 'views')

    def retrieve(self, request, *args, **kwargs):
        # Increment the view count if the recipe belongs to a different author
        recipe = self.get_object()
        if recipe.author != request.user:
            # Use atomic update with F() expression to ensure thread safety
            models.Recipe.objects.filter(**kwargs).update(views=F('views') + 1)

        return super().retrieve(self, request)


class ImageViewSet(MultipleFieldQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.ImageSerializer
    queryset = models.Image.objects.all()
    queryset_fields = ('recipe__author__username', 'recipe__slug')


class IngredientViewSet(MultipleFieldQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()
    queryset_fields = ('recipe__author__username', 'recipe__slug')


class StepViewSet(MultipleFieldQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.StepSerializer
    queryset = models.Step.objects.all()
    queryset_fields = ('recipe__author__username', 'recipe__slug')


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    lookup_field = 'slug'
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)
