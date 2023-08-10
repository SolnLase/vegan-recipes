import uuid
from utils import generate_unique_identifier
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    StepValueValidator,
)
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="recipes",
        null=True,
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
        ordering = ("-created",)
        # Titles for recipes created by one author must be unique
        unique_together = (("author", "title"), ("author", "slug"))

    def save(self, *args, **kwargs):
        # Create slug
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Order(models.Model):
    """
    Abstract model containing order field and methods returning new object's order
    and for changing its order respectively
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_model = type(self)

    order = models.PositiveIntegerField(
        editable=False,
        validators=[MinValueValidator(1), MaxValueValidator(20), StepValueValidator(1)],
        null=True,
    )

    class Meta:
        abstract = True

    def evaluate_next_object_order(self):
        """
        Returns the order for the next object in the recipe related object
        """
        pass

    def change_order(self, new_order):
        """
        Changes the order of the object and adjusts the order of other steps accordingly
        """

        new_order = int(new_order)
        queryset = self.object_model.objects.filter(recipe=self.recipe)

        if new_order > queryset.count():
            raise ValidationError(
                "New order can't be greater than the sum of all steps related to the same recipe"
            )
        if new_order < 0:
            raise ValidationError("New order must be a positive integer")

        old_order = self.order
        self.order = new_order
        self.save()

        if old_order < new_order:
            # Moving the step down, so adjust the order of steps in between
            queryset.filter(order__gt=old_order, order__lte=new_order).exclude(
                pk=self.pk
            ).update(order=models.F("order") - 1)
        elif old_order > new_order:
            # Moving the step up, so adjust the order of steps in between
            queryset.filter(order__gte=new_order, order__lt=old_order).exclude(
                pk=self.pk
            ).update(order=models.F("order") + 1)


class Image(Order):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="images")
    unique_identifier = models.CharField(max_length=100, editable=False)

    def image_path(instance, filename):
        return f"recipes/{instance.recipe.author.username}/{slugify(instance.recipe.title)}/{filename}"

    url = models.ImageField(upload_to=image_path, unique=True)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    class Meta:
        unique_together = (("recipe", "unique_identifier"),)

    def evaluate_next_image_order(self):
        return self.recipe.images.count() + 1

    def save(self, *args, **kwargs):
        is_created = not bool(Image.objects.filter(pk=self.pk))
        if is_created:
            self.order = self.evaluate_next_image_order()
        self.unique_identifier = generate_unique_identifier(self.url)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.url.name


class Ingredient(models.Model):
    UNIT_CHOICES = (
        ("g", "grams"),
        ("kg", "kilograms"),
        ("mg", "milligrams"),
        ("oz", "ounces"),
        ("lb", "pounds"),
        ("cup", "cups"),
        ("tsp", "teaspoons"),
        ("tbsp", "tablespoons"),
        ("ml", "milliliters"),
        ("l", "liters"),
        ("piece", "pieces"),
    )

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients"
    )
    name = models.CharField(max_length=50)
    quantity = models.FloatField(null=True, blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, null=True, blank=True)
    additional_informations = models.CharField(max_length=100, null=True, blank=True)
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    def __str__(self):
        return self.name


class Step(Order):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")
    instruction = models.TextField(max_length=1000)

    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )

    class Meta:
        ordering = ("order",)
        unique_together = (("recipe", "instruction"),)

    def evaluate_next_step_order(self):
        return self.recipe.steps.count() + 1

    def save(self, *args, **kwargs):
        # Automatically assign step's order by one
        is_created = not bool(Step.objects.filter(pk=self.pk))
        if is_created:
            self.order = self.evaluate_next_step_order()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order}. {self.instruction[:50]} ({self.recipe})"


class Tag(models.Model):
    recipes = models.ManyToManyField(Recipe, related_name="tags", blank=True)
    name = models.CharField(max_length=75, unique=True)
    slug = models.SlugField(editable=False, unique=True, primary_key=True)

    class Meta:
        ordering = ("name",)

    def save(self, *args, **kwargs):
        # Create slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
