from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import MyUser

UserModel = get_user_model()


class MyUserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = UserModel
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)


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
        from recipes.serializers import FavoriteSerializer
        recipes = instance.recipe_set.all()
        request = self.context.get('request')

        favorite_serializer = FavoriteSerializer(
            recipes, many=True, context={'request': request}
        )

        return favorite_serializer.data

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
