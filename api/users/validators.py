from rest_framework import serializers
from django.contrib.auth.models import User


def validate_email(value):
    """
    Validate if there are no more users with this email
    """
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("A user with that email already exists.")
    return value
