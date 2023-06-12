from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import User
from .validators import (validate_email, validate_username,
                         validate_username_exists)


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username, validate_username_exists],
        allow_blank=False
    )
    email = serializers.EmailField(max_length=254, validators=[validate_email],
                                   allow_blank=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )

    def create(self, validated_data):
        email = validated_data.get("email", None)
        validated_data.pop("email")
        return User.objects.create(email=email, **validated_data)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='subscribe_check'
    )

    def subscribe_check(self, obj):
        user = self.context['request'].user

        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='recipes_list'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='recipes_list_count'
    )

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                'На самого себя подписаться нельзя!')
        if (user.follower.filter(author=author).exists()):
            raise serializers.ValidationError(
                'Вы уже подписаны на данного пользователя!')
        return data

    def recipes_list(self, obj):
        from api.serializers import RecipesSubGetSerializer
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return RecipesSubGetSerializer(queryset, many=True).data

    def recipes_list_count(self, obj):
        return obj.recipes.count()
