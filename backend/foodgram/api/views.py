import io

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import CustomPermission
from .serializers import (IngredientsSerializer,
                          RecipesSerializer,
                          RecipesSubGetSerializer,
                          TagsSerializer)
from recipes.models import (Favorites,
                            Ingredients,
                            IngredientsRecipes,
                            Recipes,
                            ShoppingCart,
                            Tags)
from users.pagination import CustomPagination


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
    lookup_field = 'id'
    filter_backends = (filters.SearchFilter, )
    pagination_class = None
    search_fields = ('^name',)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'id'
    permission_classes = (CustomPermission, )
    pagination_class = CustomPagination

    def get_queryset(self):
        author = self.request.query_params.get('author')
        if author is not None:
            return Recipes.objects.filter(author__id=author)
        tags = self.request.query_params.get('tags')
        if tags is not None:
            return Recipes.objects.filter(tags__slug=tags)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None and int(is_favorited) == 1:
            return Recipes.objects.filter(favorites__user=self.request.user)
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if is_in_shopping_cart is not None and int(is_in_shopping_cart) == 1:
            return Recipes.objects.filter(
                shopping_cart__user=self.request.user)
        return Recipes.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_delete_func(self, id, request, model):
        user = request.user
        recipe = get_object_or_404(Recipes, id=id)
        obj = model.objects.filter(user=user, recipes=recipe)
        if request.method == "POST":
            if obj.exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipes=recipe)
            serializer = RecipesSubGetSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
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
        return self.post_delete_func(id, request, Favorites)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, id):
        return self.post_delete_func(id, request, ShoppingCart)

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

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        p.setFont("Arial", 20)
        p.drawString(250, 800, "Список покупок:")
        height = 760
        for i, (name, data) in enumerate(final_list.items(), 1):
            p.drawString(100, height, (f'{i}) {name} - {data["amount"]}, '
                                       f'{data["measurement_unit"]}'))
            height -= 25
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True,
                            filename="Список покупок.pdf")
