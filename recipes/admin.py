from django.contrib import admin
from .models import Recipe, Image, Ingredient, Step, Tag

admin.site.register(Recipe)
admin.site.register(Image)
admin.site.register(Ingredient)
admin.site.register(Step)
admin.site.register(Tag)
