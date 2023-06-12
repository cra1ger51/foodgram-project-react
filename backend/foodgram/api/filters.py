from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredients


class IngredientsFilter(FilterSet):
    """Фильтр ингдериентов."""
    name = CharFilter(field_name='^name')

    class Meta:
        model = Ingredients
        fields = ('name',)
