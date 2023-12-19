import base64

from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from transliterate import translit
from users.serializers import MyUserSubscriptionSerializer

from .models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    UserFavoriteRecipe
)


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


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True, read_only=False
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    image = Base64ImageField()
    author = MyUserSubscriptionSerializer(source='user', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',  'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        ]

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_in_user_shopping_cart(request.user)
        return False

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

        if not self.context['request'].data.get('image'):
            raise ValidationError({'detail': 'Image field is required.'})

        validated_data['created_at'] = timezone.now()

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

    def validate_ingredient(self, ingredient_data):
        ingredient_id = ingredient_data['ingredient']['id']
        amount = ingredient_data.get('amount')

        if amount is not None and amount < 1:
            raise serializers.ValidationError(
                'Ingredient amount must be greater than or equal to 1'
                + f' for ingredient with id {ingredient_id}.'
            )

        try:
            Ingredient.objects.get(pk=ingredient_id)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                f'Ingredient with id {ingredient_id} does not exist.'
            )

        return ingredient_data

    def validate_tags(self, tags_data):
        unique_tags = set()

        for tag_id in tags_data:
            if tag_id in unique_tags:
                raise serializers.ValidationError(
                    {'detail': 'Duplicate tags are not allowed.'},
                    code='invalid'
                )
            unique_tags.add(tag_id)

            try:
                Tag.objects.get(pk=tag_id)
            except Tag.DoesNotExist:
                raise serializers.ValidationError(
                    {'detail': f'Tag with id {tag_id} does not exist.'},
                    code='invalid'
                )

        return tags_data

    def validate_cooking_time(self, cooking_time):
        if cooking_time is not None and cooking_time < 1:
            raise serializers.ValidationError(
                {'detail': 'Cooking time must be greater than or equal to 1.'}

            )
        return cooking_time

    def validate_ingredients(self, ingredients_data):
        unique_ingredients = set()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['ingredient']['id']

            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError(
                    {
                        'detail': 'Duplicate ingredients are not allowed'
                        + f' for ingredient with id {ingredient_id}.'
                    },
                    code='invalid'
                )
            unique_ingredients.add(ingredient_id)

            try:
                Ingredient.objects.get(pk=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    {'detail': 'Ingredient with id does not exist.'},
                    code='invalid'
                )

        return ingredients_data

    def validate(self, data):
        ingredients_data = data.get('recipe_ingredients', [])
        tags_data = data.get('tags', [])
        cooking_time = data.get('cooking_time')

        for ingredient_data in ingredients_data:
            self.validate_ingredient(ingredient_data)

        self.validate_tags(tags_data)
        self.validate_cooking_time(cooking_time)

        return data
