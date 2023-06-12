from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import CustomPermission
from .serializers import (IngredientsSerializer,
                          RecipesSerializer,
                          RecipesSubGetSerializer,
                          TagsSerializer)
from .utils.list_to_pdf import list_to_pdf
from core.pagination import CustomPagination
from recipes.models import (Favorites,
                            Ingredients,
                            IngredientsRecipes,
                            Recipes,
                            ShoppingCart,
                            Tags)
from users.models import User


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ['get']
    lookup_field = 'id'
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ['get']
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('^name',)
    # lookup_field = 'id'
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'id'
    permission_classes = (CustomPermission, )
    pagination_class = CustomPagination

    def get_queryset(self):
        author_id = self.request.query_params.get('author')
        if author_id:
            author = get_object_or_404(User, pk=author_id)
            return author.recipes.all()
        tags_slug = self.request.query_params.get('tags')
        if tags_slug:
            tags = get_object_or_404(Tags, slug=tags_slug)
            return tags.recipes.all()
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1':
            return Recipes.objects.filter(favorites__user=self.request.user)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart == '1':
            return Recipes.objects.filter(
                shopping_cart__user=self.request.user)
        return Recipes.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create_func(self, id, request, model):
        user = request.user
        recipe = get_object_or_404(Recipes, id=id)
        obj = model.objects.filter(user=user, recipes=recipe)
        if obj.exists():
            return Response({'errors': 'Рецепт уже добавлен!'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipes=recipe)
        serializer = RecipesSubGetSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_func(self, id, request, model):
        user = request.user
        recipe = get_object_or_404(Recipes, id=id)
        obj = model.objects.filter(user=user, recipes=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, id):
        if request.method == 'POST':
            return self.create_func(id, request, Favorites)
        if request.method == "DELETE":
            return self.delete_func(id, request, Favorites)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, id):
        if request.method == 'POST':
            return self.create_func(id, request, ShoppingCart)
        if request.method == "DELETE":
            return self.delete_func(id, request, ShoppingCart)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        final_list = {}
        ingredients = IngredientsRecipes.objects.filter(
            recipes__shopping_cart__user=user).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
            'amount')
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]

        return list_to_pdf(final_list)
