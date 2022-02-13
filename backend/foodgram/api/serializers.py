import webcolors
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                        ShopingCart, Tag)
from users.serializers import CustomUserSerializer


class HEXColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError("This is not a HEX color")
        return data


class TagSerializer(serializers.ModelSerializer):
    color = HEXColor()

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit")


class ShoppingCartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="recipe.name")
    image = serializers.ImageField(source="recipe.image")
    cooking_time = serializers.ReadOnlyField(source="recipe.cooking_time")

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


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
        return IngredientAmountSerializer(
            IngredientAmount.objects.filter(recipe=obj).all(), many=True
        ).data

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return ShopingCart.objects.filter(user=user, recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    ingredients = IngredientAmountSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
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
        if cooking_time <= 0:
            raise serializers.ValidationError(
                "Please fill the cookint time field"
            )
        return cooking_time

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        user = self.context.get("request").user
        create_recipe = Recipe.objects.create(author=user, **validated_data)
        for ingredient in ingredients:
            amount = ingredient.get("amount")
            id = ingredient.get("id")
            IngredientAmount.objects.get_or_create(
                ingredient_id=id, recipe=create_recipe, amount=amount
            )
        create_recipe.tags.set(tags)
        create_recipe.save()
        return create_recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        instance.author = validated_data.get("author", instance.author)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.tags.set(tags)
        instance.save()
        ingredients_data = validated_data.pop("ingredients_recipes")
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        for ingredient in ingredients_data:
            ing = Ingredient.objects.get(id=ingredient["id"])
            ing_for_rec = IngredientAmount.objects.create(
                id=ingredient["id"],
                ingredient=ing,
                amount=ingredient["amount"],
                recipe=instance,
            )
            ing_for_rec.save()
        return instance
