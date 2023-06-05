from django.contrib import admin

from .models import (Favorites,
                     Ingredients,
                     IngredientsRecipes,
                     Recipes,
                     ShoppingCart,
                     Tags,
                     TagsRecipes)


class TagsAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'color',
                    'slug',

                    )


class IngredientsRecipesAdmin(admin.ModelAdmin):
    list_display = ('ingredients',
                    'recipes',
                    'amount',

                    )


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('recipes',
                    'user',
                    )


class TagsRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipes',
                    'tags',
                    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipes',
                    'user',
                    )


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit',
                    )
    list_filter = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    readonly_fields = ('favorites_count',)
    list_display = ('name',
                    'author',
                    )
    list_filter = ('name', 'author',
                   ("tags", admin.RelatedOnlyFieldListFilter),)

    @admin.display(empty_value="0", description='Добавили в избранное раз')
    def favorites_count(self, obj):
        return Favorites.objects.filter(recipes=obj).count()


admin.site.register(Recipes, RecipesAdmin)
admin.site.register(Favorites, FavoritesAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(TagsRecipes, TagsRecipesAdmin)
admin.site.register(IngredientsRecipes, IngredientsRecipesAdmin)
