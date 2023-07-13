from rest_framework import permissions
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404

from recipes.models import Recipe


class IsAccountOwner(permissions.BasePermission):
    """
    Object-level permission to only allow to the account access to it's user.
    """

    message = "You must be owner of this account."

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    message = "You can't make changes to not your content"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `author`.
        return obj.author == request.user


class IsRecipeOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow making changes to objects related to the recipe only to its owner
    """

    message = "You can't create, update, or delete children objects of this recipe."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        recipe_id = view.kwargs.get('recipe__id')
        recipe = get_object_or_404(Recipe, id=recipe_id)

        return recipe.author == request.user


class IsNotAuthenticated(permissions.BasePermission):
    """
    Only allow not authenticated users
    """

    message = "You must log out to do this operation"

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class HasEmailConfirmed(permissions.BasePermission):
    """
    Only allow users with confirmed emails
    """

    message = "You must confirm your email first."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.profile.email_confirmed
