from django.db import models
from django.contrib.auth import get_user_model
from users.models import MyUser


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#000000")
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient'
    )
    shopping_cart_users = models.ManyToManyField(
        MyUser, related_name='shopping_cart', through='ShoppingCartItem'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipe_images/', null=True)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()

    def is_in_user_shopping_cart(self, user):
        return self.shopping_cart_users.filter(pk=user.pk).exists()

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='ingredient_to_recipe'
    )
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.amount} {self.ingredient.name}"


class UserFavoriteRecipe(models.Model):
    user = models.ForeignKey(
        MyUser, on_delete=models.CASCADE, related_name='favorite_recipes'
    )
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.recipe.name}"


class ShoppingCartItem(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s shopping cart: {self.recipe.name}"
