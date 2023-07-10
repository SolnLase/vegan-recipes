# Generated by Django 4.2.2 on 2023-07-09 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_image_url_alter_tag_recipes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('-name',)},
        ),
        migrations.AddField(
            model_name='image',
            name='unique_identifier',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]