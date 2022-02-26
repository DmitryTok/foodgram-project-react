from api.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                        ShopingCart, Tag)
from django.contrib.auth import get_user_model
from django.forms import IntegerField
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


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


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    amount = IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ("id", "amount")


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ShopingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if ShopingCart.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('This recipe already in shopping cart')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Favorite.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ("recipe", "user")


class ListRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeSerializer(
        source='ingredient_recipe', many=True, read_only=True
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
        request = self.context.get('request')
        return (
            False if not request or request.user.is_anonymous else
            Favorite.objects.filter(recipe=obj, user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            False if not request or request.user.is_anonymous else
            ShopingCart.objects.filter(recipe=obj, user=request.user).exists()
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    text = serializers.CharField(required=False)
    ingredients = IngredientForRecipeSerializer(
        many=True,
        source="ingredient_recipe"
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
        ingredients = validated_data.pop("ingredient_recipe")
        recipe = Recipe.objects.create(author=user, **validated_data)
        for tag in tags:
            recipe.tags.add(tag)
        for ingredient in ingredients:
            current_ingredient = ingredient['ingredient']['id']
            IngredientAmount.objects.get_or_create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        instance.author = validated_data.get("author", instance.author)
        instance.name = validated_data.get("name", instance.name)
        instance.image = validated_data.get("image", instance.image)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get("cooking_time",
                                                   instance.cooking_time)
        instance.pub_date = validated_data.get("pub_date", instance.pub_date)
        instance.tags.set(tags)
        instance.save()
        ingredients_data = validated_data.pop("ingredients_recipe")
        IngredientAmount.objects.filter(recipe=instance).all().delete()
        for ingredient in ingredients_data:
            current_id = Ingredient.objects.get(id=ingredient['id'])
            ingredient_for_recipe = IngredientAmount.objects.create(
                id=ingredient['id'],
                ingredient=current_id,
                amount=ingredient['amount'],
                recipe=instance)
            ingredient_for_recipe.save()
        return instance
