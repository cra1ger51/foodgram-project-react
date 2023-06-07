from django.contrib import admin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('recipes_count', 'subs_count')
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'recipes_count',
                    'subs_count',
                    'is_staff',
                    'is_superuser',
                    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')

    @admin.display(empty_value="0", description='Количество рецптов')
    def recipes_count(self, obj):
        return obj.recipes.all().count()

    @admin.display(empty_value="0", description='Количество подписчиков')
    def subs_count(self, obj):
        return obj.following.all().count()


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author',
                    )
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
