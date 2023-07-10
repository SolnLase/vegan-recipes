# Generated by Django 4.2.2 on 2023-07-05 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_tag_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='image_field',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.CharField(choices=[('g', 'grams'), ('kg', 'kilograms'), ('mg', 'milligrams'), ('oz', 'ounces'), ('lb', 'pounds'), ('cup', 'cups'), ('tsp', 'teaspoons'), ('tbsp', 'tablespoons'), ('ml', 'milliliters'), ('l', 'liters'), ('piece', 'pieces')], max_length=20),
        ),
    ]