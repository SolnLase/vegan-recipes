# Generated by Django 4.2.2 on 2023-07-20 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_tag_options_alter_ingredient_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='instruction',
            field=models.TextField(max_length=1000),
        ),
    ]
