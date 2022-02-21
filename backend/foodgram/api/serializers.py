from api.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                        ShopingCart, Tag)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from backend.foodgram.api.models import User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(source="ingredient.measurement_unit")

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


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Favorite.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = "recipe", "user"


class ListRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=IngredientAmount.objects.all(), many=True
    )
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
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    author = CustomUserSerializer(read_only=True)
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
        if cooking_time <= 0:
            raise serializers.ValidationError("Please fill the cookint time field")
        return cooking_time

    def create(self, validated_data):
        user = self.context["request"].user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients_set")
        recipe = Recipe.objects.create(auhor=user)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            current_ingredient = ingredient["ingredient"]
            IngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        if "ingredients_set" in validated_data:
            instance.ingredients.clear()
            ingredients = validated_data.pop("ingredients_set")
            for ingredient in ingredients:
                current_ingredient = ingredient["ingredient"]
            IngredientAmount.objects.create(
                ingredient=current_ingredient,
                recipe=instance,
                amount=ingredient["amount"],
            )
        if "tags" in validated_data:
            instance.tags.set(validated_data.get("tags"))
        if "name" in validated_data:
            instance.name = validated_data.get("name", instance.name)
        if "text" in validated_data:
            instance.text = validated_data.get("text", instance.text)
        if "image" in validated_data:
            instance.image = validated_data.get("image", instance.image)
        if "cooking_time" in validated_data:
            instance.cooking_time = validated_data.get(
                "cooking_time", instance.cooking_time
            )
        instance.save()
        return instance
