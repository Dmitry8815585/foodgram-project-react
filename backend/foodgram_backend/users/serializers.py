from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import MyUser


class MyUserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = get_user_model()
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class MyUserSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, instance):
        user = self.context.get('request', None).user
        return user.is_authenticated and user.subscriptions.filter(
            id=instance.id
        ).exists()

    def get_recipes(self, instance):
        return [
            {
                'id': recipe.id,
                'name': recipe.name,
                'image': self.context['request'].build_absolute_uri(
                    recipe.image.url
                ) if recipe.image else None,
                'cooking_time': recipe.cooking_time,
            } for recipe in instance.recipe_set.all()
        ]

    def get_recipes_count(self, instance):
        return instance.recipe_set.count()


class MyUserProfileSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, instance):
        user = self.context['request'].user
        return user.is_authenticated and user.subscriptions.filter(
            id=instance.id
        ).exists()
