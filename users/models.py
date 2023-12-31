from django.db import models
from django.contrib.auth.models import User
from recipes.models import Recipe


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_confirmed = models.BooleanField(default=False)

    def image_path(instance, filename):
        return f"users/{instance.user.username}"

    avatar = models.ImageField(upload_to=image_path, null=True, blank=True)  # default
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        if self.user:
            return self.user.username
        else:
            return self.id


class FavouriteRecipes(models.Model):
    owner = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='favourite_recipes'
    )
    recipes = models.ManyToManyField(Recipe, blank=True)

    class Meta:
        verbose_name_plural = "Favourite Recipes"

    def __str__(self):
        return self.owner.username
