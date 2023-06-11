from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tags(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        verbose_name='Теги',
        help_text='Теги'
    )
    color = ColorField(
        max_length=7,
        unique=True,
        null=False,
        default='#FF0000',
        verbose_name='Цвет тега',
        help_text='Цвет тега'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        null=False,
        verbose_name='Теги (кратко)',
        help_text='Теги (кратко)'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Теги'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(fields=['color', 'name', 'slug'],
                                    name='Tags_unique')
        ]

    def __str__(self):
        return f'Тег {self.name[:15]}'


class Ingredients(models.Model):
    name = models.CharField(
        max_length=100,
        null=False,
        verbose_name='Ингредиент',
        help_text='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=10,
        null=False,
        verbose_name='Единица измерения',
        help_text='Единица измерения'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['measurement_unit', 'name'],
                                    name='Ingredients_unique')
        ]

    def __str__(self):
        return f'Ингредиент {self.name[:15]}'


class Recipes(models.Model):
    tags = models.ManyToManyField(
        Tags,
        through='TagsRecipes',
        related_name='recipes',
        verbose_name='Теги к рецепту',
        help_text='Теги к рецепту'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        related_name='recipes',
        verbose_name='Необходимые ингредиенты',
        help_text='Необходимые ингредиенты'
    )
    name = models.CharField(
        max_length=200,
        null=False,
        verbose_name='Название',
        help_text='Название'
    )
    image = models.ImageField(
        verbose_name='Вкусная картинка',
        null=False,
        help_text='Вкусная картинка',
        upload_to='recipes/',
    )
    text = models.TextField(
        null=False,
        verbose_name='Инструкция к приготовлению',
        help_text='Инструкция к приготовлению'
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        null=False,
        default=1,
        verbose_name='Время приготовления',
        help_text='Время приготовления'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(fields=['author', 'name'],
                                    name='Recipes_unique')
        ]

    def __str__(self):
        return f'Рецепт {self.name[:15]}'


class TagsRecipes(models.Model):
    tags = models.ForeignKey(
        Tags,
        null=False,
        on_delete=models.CASCADE,
        related_name='tags_recipes',
        verbose_name='Теги'
    )
    recipes = models.ForeignKey(
        Recipes,
        null=False,
        on_delete=models.CASCADE,
        related_name='tags_recipes',
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['-recipes']
        verbose_name = 'Теги и рецепты'
        verbose_name_plural = 'Теги и рецепты'
        constraints = [
            models.UniqueConstraint(fields=['tags', 'recipes'],
                                    name='TagsRecipes_unique')
        ]

    def __str__(self):
        return f'Тег {self.tags.name} - рецепт {self.recipes.name}'


class IngredientsRecipes(models.Model):
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        null=False,
        related_name='ingredients_recipes',
        verbose_name='Ингредиенты'
    )
    recipes = models.ForeignKey(
        Recipes,
        null=False,
        on_delete=models.CASCADE,
        related_name='ingredients_recipes',
        verbose_name='Рецепты'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='Необходимое количество',
        help_text='Необходимое количество'
    )

    class Meta:
        ordering = ('-recipes', )
        verbose_name = 'Ингредиенты и рецепты'
        verbose_name_plural = 'Ингредиенты и рецепты'
        constraints = [
            models.UniqueConstraint(fields=['ingredients', 'recipes'],
                                    name='IngredientsRecipes_unique')
        ]

    def __str__(self):
        return (f'Ингредиент {self.ingredients.name}'
                '- рецепт {self.recipes.name}')


class Favorites(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепты'
    )
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['recipes', 'user'],
                                    name='Favorites_unique')
        ]

    def __str__(self):
        return (f'Любимый рецепт {self.recipes.name}')


class ShoppingCart(models.Model):
    recipes = models.ForeignKey(
        Recipes,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепты'
    )
    user = models.ForeignKey(
        User,
        null=False,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(fields=['recipes', 'user'],
                                    name='Recipe_cart_unique')
        ]

    def __str__(self):
        return (f'Что купить к рецепту {self.recipes.name}')
