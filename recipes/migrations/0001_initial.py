# Generated by Django 4.2.2 on 2023-08-14 10:35

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import recipes.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField(editable=False)),
                ('body', models.TextField()),
                ('views', models.PositiveIntegerField(blank=True, default=0, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
                'unique_together': {('author', 'slug'), ('author', 'title')},
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=75, unique=True)),
                ('slug', models.SlugField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('recipes', models.ManyToManyField(blank=True, related_name='tags', to='recipes.recipe')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('unit', models.CharField(blank=True, choices=[('g', 'grams'), ('kg', 'kilograms'), ('mg', 'milligrams'), ('oz', 'ounces'), ('lb', 'pounds'), ('cup', 'cups'), ('tsp', 'teaspoons'), ('tbsp', 'tablespoons'), ('ml', 'milliliters'), ('l', 'liters'), ('piece', 'pieces')], max_length=20, null=True)),
                ('additional_informations', models.CharField(blank=True, max_length=100, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Step',
            fields=[
                ('order', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20), django.core.validators.StepValueValidator(1)])),
                ('instruction', models.TextField(max_length=1000)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='recipes.recipe')),
            ],
            options={
                'ordering': ('order',),
                'unique_together': {('recipe', 'instruction')},
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('order', models.PositiveIntegerField(editable=False, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20), django.core.validators.StepValueValidator(1)])),
                ('unique_identifier', models.CharField(editable=False, max_length=100)),
                ('url', models.ImageField(unique=True, upload_to=recipes.models.Image.image_path)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='recipes.recipe')),
            ],
            options={
                'unique_together': {('recipe', 'unique_identifier')},
            },
        ),
    ]