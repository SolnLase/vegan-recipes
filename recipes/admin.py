from django.contrib import admin
from . import models 

admin.site.register(models.Recipe)
admin.site.register(models.Image)
admin.site.register(models.Ingredient)
admin.site.register(models.Step)
admin.site.register(models.Tag)