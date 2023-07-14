from django.db.models import F
from django.core.exceptions import ValidationError

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
 
from . import serializers
from recipes import models
from api import permissions as custom_permissions
from api.mixins import MultipleFieldLookupMixin, MultipleFieldQuerysetMixin


class RecipeViewSet(MultipleFieldLookupMixin, viewsets.ModelViewSet):
    serializer_class = serializers.RecipeSerializer
    queryset = models.Recipe.objects.all()
    multiple_lookup_fields = ('slug', 'id')
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        custom_permissions.IsOwnerOrReadOnly,
        custom_permissions.HasEmailConfirmed,
    )
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    filterset_fields = ('tags', 'author__username', 'ingredients__name')
    search_fields = ('=author__username', 'title', 'ingredients__name', 'tags__name')
    ordering_fields = ('created', 'modified', 'views')

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
    queryset_fields = ('recipe__slug', 'recipe__id', 'pk')
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        custom_permissions.IsRecipeOwnerOrReadOnly,
        custom_permissions.HasEmailConfirmed,
    )


class IngredientViewSet(MultipleFieldQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = models.Ingredient.objects.all()
    queryset_fields = ('recipe__slug', 'recipe__id', 'pk')
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        custom_permissions.IsRecipeOwnerOrReadOnly,
        custom_permissions.HasEmailConfirmed,
    )


class StepViewSet(MultipleFieldQuerysetMixin, viewsets.ModelViewSet):
    queryset = models.Step.objects.all()
    queryset_fields = ('recipe__slug', 'recipe__id', 'pk')
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        custom_permissions.IsRecipeOwnerOrReadOnly,
        custom_permissions.HasEmailConfirmed,
    )

    def get_serializer_class(self):
        if self.action == 'change_order':
            return serializers.StepOrderSerializer
        else:
            return serializers.StepSerializer

    @action(detail=True, methods=['post'])
    def change_order(
        self,
        request,
        pk=None,
        *args,
        **kwargs,
    ):
        step = self.get_object()
        new_order = request.data['order']

        serializer = serializers.StepOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            step.change_order(new_order)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TagSerializer
    queryset = models.Tag.objects.all()
    lookup_field = 'slug'
    permission_classes = (IsAdminUser,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)
    ordering_fields = ('name',)
