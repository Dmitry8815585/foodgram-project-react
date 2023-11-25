from rest_framework import serializers

from .models import Ingredient, Recipe, RecipeIngredient, Tag
from users.serializers import MyUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = MyUserSerializer(read_only=True)
    ingredients = serializers.ListField(write_only=True)
    # ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        return recipe
