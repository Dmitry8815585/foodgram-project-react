from rest_framework import serializers
from django.utils.text import slugify
from transliterate import translit

from .models import (
    Ingredient, Recipe, RecipeIngredient, Tag, UserFavoriteRecipe
)
from users.models import MyUser

import base64
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

    def create(self, validated_data):
        transliterated_name = translit(
            validated_data['name'], 'ru', reversed=True
            )
        validated_data['slug'] = slugify(transliterated_name)

        tag = Tag.objects.create(**validated_data)
        return tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id', 'name',
            'measurement_unit', 'amount'
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=False
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(source='user', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',  'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_favorite = UserFavoriteRecipe.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
            return user_favorite
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags_data = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )

        recipe.tags.set(tags_data)

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tags_representation = TagSerializer(
            instance.tags.all(), many=True
        ).data

        representation['tags'] = tags_representation

        return representation

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        tags_data = validated_data.get('tags', [])
        instance.tags.set(tags_data)

        ingredients_data = validated_data.get('recipe_ingredients', [])
        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient']['id']
            amount = ingredient_data['amount']
            ingredient = Ingredient.objects.get(pk=ingredient_id)

            RecipeIngredient.objects.create(
                recipe=instance, ingredient=ingredient, amount=amount
            )

        instance.save()
        return instance
