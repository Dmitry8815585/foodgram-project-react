from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    measurement_unit = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient, blank=True
    )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipe_images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
