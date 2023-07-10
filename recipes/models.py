import uuid
from utils import generate_unique_identifier
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    StepValueValidator,
)
from django.utils.text import slugify


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='recipes', null=True
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(editable=False)
    body = models.TextField()
    views = models.PositiveIntegerField(default=0, blank=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    class Meta:
        # Ordering by the creation from the latest to the oldest
        ordering = ('-created',)
        # Titles for recipes created by one author must be unique
        unique_together = (('author', 'title'), ('author', 'slug'))

    def save(self, *args, **kwargs):
        # Create slug
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Image(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    unique_identifier = models.CharField(max_length=100, editable=False)

    def image_path(instance, filename):
        return f"recipes/{instance.recipe.author.username}/{slugify(instance.recipe.title)}/{filename}"

    url = models.ImageField(upload_to=image_path, unique=True)

    class Meta:
        unique_together = (('recipe', 'unique_identifier'),)

    def save(self, *args, **kwargs):
        self.unique_identifier = generate_unique_identifier(self.url)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.url.name


class Ingredient(models.Model):
    UNIT_CHOICES = (
        ('g', 'grams'),
        ('kg', 'kilograms'),
        ('mg', 'milligrams'),
        ('oz', 'ounces'),
        ('lb', 'pounds'),
        ('cup', 'cups'),
        ('tsp', 'teaspoons'),
        ('tbsp', 'tablespoons'),
        ('ml', 'milliliters'),
        ('l', 'liters'),
        ('piece', 'pieces'),
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients'
    )
    name = models.CharField(max_length=50)
    quantity = models.FloatField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    def __str__(self):
        return self.name


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')
    instruction = models.TextField(max_length=500)
    # Max 20 steps are allowed, and can be only add by one
    order = models.PositiveIntegerField(
        editable=False,
        validators=[MinValueValidator(1), MaxValueValidator(20), StepValueValidator(1)],
    )
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    def evaluate_step_order(self):
        """
        New step's order
        """
        return self.recipe.steps.count() + 1

    def save(self, *args, **kwargs):
        # Automatically assign step's order by one
        self.order = self.evaluate_step_order()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.instruction[:100]


class Tag(models.Model):
    recipes = models.ManyToManyField(Recipe, related_name='tags', blank=True)
    name = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(editable=False, unique=True, primary_key=True)

    class Meta:
        ordering = ('-name',)

    def save(self, *args, **kwargs):
        # Create slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
