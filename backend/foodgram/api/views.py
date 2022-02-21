import io

from api.filters import CustomRecipeFilter
from api.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                        ShopingCart, Tag)
from api.serializers import (CreateRecipeSerializer, IngredientSerializer,
                             ListRecipeSerializer, ShoppingCartSerializer,
                             TagSerializer, FavoriteSerializer)
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.permissions import IsAuthorOrAdminOrReadOnly
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.serializers import RecipeForFollowSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [
        AllowAny,
    ]
    serializer_class = TagSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [
        IsAuthorOrAdminOrReadOnly,
    ]
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        IsAuthorOrAdminOrReadOnly,
    ]
    serializer_class = CreateRecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilter

    def get_serializer_class(self):
        if self.request.method == "POST" or self.request.method == "PATCH":
            return CreateRecipeSerializer
        if self.request.method == "GET":
            return ListRecipeSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if ShopingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "This recipe already in shopping cart"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            shoping_cart = ShopingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                shoping_cart, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            delete_shoping_cart = ShopingCart.objects.filter(user=user, recipe=recipe)
            if delete_shoping_cart.exists():
                delete_shoping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shoping_cart",
        permission_classes=[IsAuthenticated],
    )
    def download_shoping_cart(self, request):
        bytestream_buffer = io.BytesIO()
        custom_canvas = canvas.Canvas(bytestream_buffer, pagesize=letter, bottomup=0)
        text_object = custom_canvas.beginText()
        text_object.setTextOrigin(inch, inch)
        text_object.setFont("Helvetica", 14)
        ingredients_list = (
            IngredientAmount.objects.filter(recipe__recipe_cart__user=request.user)
            .values_list("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        print(ingredients_list)
        lines = []
        for ingredient in ingredients_list:
            lines.append(
                f"{ingredient['ingredient__name']}"
                f"{ingredient['ingredient__measurement_unit']}"
                f"{ingredient['amount']}"
            )
        for line in lines:
            text_object.textLine(line)
        custom_canvas.drawText(text_object)
        custom_canvas.showPage()
        custom_canvas.save()
        bytestream_buffer.seek(0)
        return FileResponse(
            bytestream_buffer, as_attachment=True, filename="shoping_list.pdf"
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == "POST":
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "This recipe already in favorite"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(
                favorite, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
