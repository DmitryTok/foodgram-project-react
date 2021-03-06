# Generated by Django 3.2 on 2022-01-27 19:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0009_auto_20220126_1110"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="image",
            field=models.ImageField(upload_to="media/", verbose_name="Image"),
        ),
        migrations.AlterField(
            model_name="shopingcart",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopping_cart",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
    ]
