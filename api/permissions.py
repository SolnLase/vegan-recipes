from rest_framework import permissions


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

    message = "You can't make changes to not your content."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `author`.
        return obj.author == request.user


class IsNotAuthenticated(permissions.BasePermission):
    """
    Only allow not authenticated users
    """
    message = "You must log out to do this operation"

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsEmailConfirmed(permissions.BasePermission):
    """
    Only allow users with confirmed emails
    """

    message = "You must confirm your email first."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.profile.email_confirmed
