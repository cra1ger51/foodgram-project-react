from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipeViewSet, TagsViewSet

v1_router = DefaultRouter()
v1_router.register(
    r'recipes', RecipeViewSet
)
v1_router.register(
    r'ingredients', IngredientsViewSet
)
v1_router.register(
    r'tags', TagsViewSet
)

urlpatterns = [
    path('', include('users.urls')),
    path('', include(v1_router.urls)),
]