from api.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                        ShopingCart, Tag)
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShopingCart
        fields = ("user", "recipe")

    def validate(self, data):
        user = data["user"]
        recipe_id = data["recipe"].id
        if ShopingCart.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError("This recipe already in shopping cart")
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Favorite.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ("recipe", "user")


class ListRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "image",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        all_ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientAmountSerializer(all_ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            False
            if not request or request.user.is_anonymous
            else Favorite.objects.filter(recipe=obj, user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            False
            if not request or request.user.is_anonymous
            else ShopingCart.objects.filter(recipe=obj, user=request.user).exists()
        )


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientAmount
        fields = ("id", "amount")


class CreateRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    author = CustomUserSerializer(read_only=True)
    ingredients = AddRecipeIngredientsSerializer(
        many=True,
    )
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError("Cooking time must be more than 0")
        return cooking_time

    @staticmethod
    def add_recipe_ingredients_tags(recipe, ingredients, tags):
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe, ingredient=ingredient["id"], amount=ingredient["amount"]
            )
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(
            author=self.context.get("request").user, **validated_data
        )
        self.add_recipe_ingredients_tags(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        IngredientAmount.objects.filter(recipe=recipe).delete()
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        self.add_recipe_ingredients_tags(recipe, ingredients, tags)
        return super().update(recipe, validated_data)
