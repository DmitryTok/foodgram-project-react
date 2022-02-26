# Generated by Django 3.2 on 2022-01-26 09:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0007_auto_20220125_1433"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipe",
            options={
                "ordering": ("-id",),
                "verbose_name": "Recipe",
                "verbose_name_plural": "Recipes",
            },
        ),
        migrations.CreateModel(
            name="Favorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.recipe",
                        verbose_name="Favorite recipe",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Favorite",
                "verbose_name_plural": "Favorites",
                "ordering": ("-id",),
            },
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_favorite_recipe"
            ),
        ),
    ]