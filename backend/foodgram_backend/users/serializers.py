from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MyUser


class MyUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        )


class MyUserSubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']

    def get_recipes(self, instance):
        return [
            {
                'id': recipe.id,
                'name': recipe.name,
                'image': self.context['request'].build_absolute_uri(recipe.image.url) if recipe.image else None,
                'cooking_time': recipe.cooking_time,
            } for recipe in instance.recipe_set.all()
        ]


class MyUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = '__all__'
