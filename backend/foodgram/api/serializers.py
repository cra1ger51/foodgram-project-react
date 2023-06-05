from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Favorites,
                            Ingredients,
                            IngredientsRecipes,
                            Recipes,
                            ShoppingCart,
                            Tags)
from users.serializers import CustomUserSerializer


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = '__all__'


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = '__all__'


class RecipesSubGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class IngredientsRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientsRecipes
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(
        many=True,
        read_only=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientsRecipesSerializer(
        source='ingredients_recipes',
        many=True,
        read_only=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='favorite_check', read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='shopping_cart_check', read_only=True
    )

    class Meta:
        model = Recipes
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def favorite_check(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorites.objects.filter(
            user=request.user, recipes=obj).exists()

    def shopping_cart_check(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipes=obj).exists()

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Недопустимое количество ингредиентов: 0')
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = get_object_or_404(Ingredients,
                                           id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient.name} уже добавлен!')
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError(
                    f'Количество ингредиента {ingredient.name} < 0'
                )
        data['ingredients'] = ingredients
        return data

    def ingredientsrecipe_create(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_obj = get_object_or_404(
                Ingredients, pk=ingredient['id'])
            IngredientsRecipes.objects.create(
                recipes=recipe,
                ingredients=ingredient_obj,
                amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        tags = self.initial_data.get('tags')
        recipe.tags.set(tags)
        self.ingredientsrecipe_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        tags = self.initial_data.get('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredientsrecipe_create(ingredients, instance)
        instance.save()
        return instance
