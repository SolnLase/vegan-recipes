import requests
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import ValidationError
from recipes import models
from api.relations import CustomMultiLookupHyperlink
from utils import generate_unique_identifier


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(
        view_name='user-detail', lookup_field='username', read_only=True
    )
    url = CustomMultiLookupHyperlink(
        view_name='recipe-detail',
        lookup_kwarg_fields=('author__username', 'slug'),
        source='*',
        read_only=True,
    )
    ingredient_listing = CustomMultiLookupHyperlink(
        view_name='ingredient-list',
        lookup_kwarg_fields={
            'recipe__author__username': 'author__username',
            'recipe__slug': 'slug',
        },
        source='*',
        read_only=True,
    )
    image_listing = CustomMultiLookupHyperlink(
        view_name='image-list',
        lookup_kwarg_fields={
            'recipe__author__username': 'author__username',
            'recipe__slug': 'slug',
        },
        source='*',
        read_only=True,
    )
    step_listing = CustomMultiLookupHyperlink(
        view_name='step-list',
        lookup_kwarg_fields={
            'recipe__author__username': 'author__username',
            'recipe__slug': 'slug',
        },
        source='*',
        read_only=True,
    )

    class Meta:
        model = models.Recipe
        fields = (
            'url',
            'author',
            'slug',
            'title',
            'body',
            'views',
            'image_listing',
            'ingredient_listing',
            'step_listing',
            'tags',
            'created',
            'modified',
        )

    def validate(self, data):
        """
        Validate if there's no more recipes of this author with this title
        """
        title = data['title']
        user = self.context['request'].user
        if models.Recipe.objects.filter(author=user, title=title).exists():
            raise ValidationError(
                detail="Recipe with this title for this author already exists.",
                code='recipe_already_exists',
            )
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)


class RecipeChildSerializer(serializers.ModelSerializer):
    """
    Serializer for related models to recipe with ManyToOne relationship
    """

    recipe = CustomMultiLookupHyperlink(
        view_name='recipe-detail',
        lookup_kwarg_fields=('author__username', 'slug'),
        read_only=True,
    )

    def get_recipe(self):
        """
        Get the current recipe
        """
        request = self.context.get('request')
        if request:
            kwargs = request.parser_context['kwargs']
            recipe_author_username = kwargs.get('recipe__author__username')
            recipe_slug = kwargs.get('recipe__slug')
            return get_object_or_404(
                models.Recipe, author__username=recipe_author_username, slug=recipe_slug
            )

    def create(self, validated_data):
        # Assign recipe based on url
        recipe = self.get_recipe()
        validated_data['recipe'] = recipe

        return super().create(validated_data)


class ImageSerializer(RecipeChildSerializer):
    url = CustomMultiLookupHyperlink(
        view_name='image-detail',
        lookup_kwarg_fields=('recipe__author__username', 'recipe__slug', 'pk'),
        source='*',
        read_only=True,
    )
    image_url = serializers.ImageField(source='url')

    class Meta:
        model = models.Image
        fields = (
            'url',
            'recipe',
            'image_url',
        )

    def validate(self, data):
        """
        Validate if there's no image duplicates
        """
        recipe = self.get_recipe()
        image_url = data['url']
        unique_identifier = generate_unique_identifier(image_url)

        if models.Image.objects.filter(
            recipe=recipe, unique_identifier=unique_identifier
        ).exists():
            raise serializers.ValidationError(
                detail="This image for this recipe was already uploaded.",
                code='image_already_exists',
            )

        return data


class IngredientSerializer(RecipeChildSerializer):
    url = CustomMultiLookupHyperlink(
        view_name='ingredient-detail',
        lookup_kwarg_fields=('recipe__author__username', 'recipe__slug', 'pk'),
        source='*',
        read_only=True,
    )

    recipe = CustomMultiLookupHyperlink(
        view_name='recipe-detail',
        lookup_kwarg_fields=('author__username', 'slug'),
        read_only=True,
    )

    class Meta:
        model = models.Ingredient
        fields = ('url', 'recipe', 'name', 'quantity', 'unit')

    def validate_name(self, value):
        """
        Validate if the ingredient is vegan using is-vegan API
        """
        ingredient_arg = value.replace(' ', '').lower()
        response = requests.get(
            f'https://is-vegan.netlify.app/.netlify/functions/api?ingredients={ingredient_arg}'
        )
        if not response.json()['isVeganSafe']:
            raise ValidationError(
                detail="This ingredient is not vegan!", code='not_vegan_ingredient'
            )

        return value


class StepSerializer(RecipeChildSerializer):
    url = CustomMultiLookupHyperlink(
        view_name='step-detail',
        lookup_kwarg_fields=('recipe__author__username', 'recipe__slug', 'pk'),
        source='*',
        read_only=True,
    )

    class Meta:
        model = models.Step
        fields = ('url', 'recipe', 'instruction', 'order')


class TagSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='tag-detail', lookup_field='slug'
    )

    class Meta:
        model = models.Tag
        fields = ('url', 'name', 'slug')
