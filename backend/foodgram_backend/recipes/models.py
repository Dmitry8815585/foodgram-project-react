from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import MyUser

from foodgram_backend.constants import (
    INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    RECIPE_IMAGE_UPLOAD_TO,
    RECIPE_NAME_MAX_LENGTH,
    TAG_COLOR_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH
)


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    color_validator = RegexValidator(
        regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message=_('Enter a valid HEX color.'),
        code='invalid_hex_color'
    )
    color = models.CharField(
        max_length=TAG_COLOR_MAX_LENGTH,
        default="#000000",
        validators=[color_validator]
    )
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

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
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField(upload_to=RECIPE_IMAGE_UPLOAD_TO)
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_in_user_shopping_cart(self, user):
        return self.shopping_cart_users.filter(pk=user.pk).exists()

    def count_favorite_users(self):
        return self.userfavoriterecipe_set.count()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


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
