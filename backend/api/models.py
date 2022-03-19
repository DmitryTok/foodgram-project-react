from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Tag name")
    color = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="HEX Color")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")

    class Meta:
        ordering = ("name",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return f"{self.name}"


class Ingredient(models.Model):
    name = models.CharField(max_length=150, verbose_name="Name")
    measurement_unit = models.CharField(max_length=150, verbose_name="Unit")

    class Meta:
        ordering = ("id",)
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

    def __str__(self):
        return f"{self.name}"


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag, related_name="tags_recipe", verbose_name="Tag")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author_resipe",
        verbose_name="Author",
    )
    ingredients = models.ManyToManyField(
        Ingredient, related_name="ingredients_resipe", verbose_name="Ingredients"
    )
    name = models.CharField(max_length=200, verbose_name="Recipe name")
    image = models.ImageField(upload_to="media/", verbose_name="Image")
    text = models.TextField(max_length=2000, verbose_name="Text")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Cooking time", validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return f"{self.name}"


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_amount",
        verbose_name="Ingredient for recipe",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_shop",
        verbose_name="resipe_amount",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Amount", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "Amount"
        verbose_name_plural = "Amounts"

    def __str__(self):
        return f"{self.ingredient}: {self.recipe}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="User")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Favorite recipe"
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe"
            )
        ]

    def __str__(self):
        return f"{self.user}: {self.recipe}"


class ShopingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipe_cart",
        verbose_name="User",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_cart",
        verbose_name="Rcipe",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "Shoping cart"
        verbose_name_plural = "Shoping carts"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_shoping_cart"
            )
        ]

    def __str__(self):
        return f"{self.user}: {self.recipe}"
