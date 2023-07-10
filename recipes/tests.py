from django.test import TestCase
from django.contrib.auth.models import User
from .models import Recipe, Image, Ingredient, Step, Tag
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class RecipeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="dawid")
        self.recipe = Recipe.objects.create(
            author=self.user,
            title="Creamy Vegan Pasta",
            body="This creamy vegan pasta is my favorite recipe to make when!",
        )
        simple_image = SimpleUploadedFile(
            "test_image.jpg", b"image_content", content_type="image/jpeg"
        )
        self.image = Image.objects.create(recipe=self.recipe, url=simple_image)
        self.ingredient = Ingredient.objects.create(
            recipe=self.recipe, name="soy milk", quantity=2, unit="cup"
        )
        self.step = Step.objects.create(
            recipe=self.recipe,
            instruction="Put all ingredients in a bowl and mix them.",
        )
        self.tag = Tag.objects.create(name="dessert")
        self.recipe.tags.add(self.tag)

    def test_recipe(self):
        self.assertEqual(self.recipe.title, "Creamy Vegan Pasta")
        self.assertEqual(
            self.recipe.body,
            "This creamy vegan pasta is my favorite recipe to make when!",
        )
        self.assertEqual(
            self.recipe.slug,
            "creamy-vegan-pasta",
        )
        self.assertEqual(self.recipe.__str__(), self.recipe.title)

    def test_image(self):
        self.assertEqual(self.image.recipe, self.recipe)
        self.assertTrue(self.image.url)
        self.assertEqual(
            self.image.url.name,
            "recipes/dawid/creamy-vegan-pasta/test_image.jpg",
        )
        self.assertEqual(self.image.__str__(), self.image.url.name)

    def test_ingredient(self):
        self.assertEqual(self.ingredient.name, "soy milk")
        self.assertEqual(self.ingredient.quantity, 2)
        self.assertEqual(self.ingredient.unit, "cup")
        self.assertEqual(self.ingredient.__str__(), self.ingredient.name)

    def test_step(self):
        self.assertEqual(self.step.recipe, self.recipe)
        self.assertEqual(
            self.step.instruction, "Put all ingredients in a bowl and mix them."
        )
        self.assertEqual(self.step.order, 1)
        self.assertEqual(self.step.__str__(), self.step.instruction[:100])

    def test_tag(self):
        self.assertEqual(
            self.tag.recipes.get(slug="creamy-vegan-pasta"), self.recipe
        )
        self.assertEqual(self.tag.name, "dessert")
        self.assertEqual(self.tag.__str__(), self.tag.name)

    def tearDown(self):
        # Call the parent's tearDown() method
        super().tearDown()

        # Delete the files associated with the Image objects
        images = Image.objects.all()  # Fetch all Image objects created during testing
        for image in images:
            if image.url:
                # Delete the file from the storage
                storage, path = image.url.storage, image.url.path
                storage.delete(path)

                # Remove empty directories recursively
                directory = os.path.dirname(path)
                while directory != '':
                    try:
                        os.rmdir(directory)
                    except OSError:
                        break  # Stop if the directory is not empty
                    directory = os.path.dirname(directory)
