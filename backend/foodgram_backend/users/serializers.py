from rest_framework import serializers
from .models import MyUser


class MyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        ]

    def create(self, validated_data):
        user = MyUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
