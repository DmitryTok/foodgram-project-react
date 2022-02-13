# Generated by Django 3.2 on 2022-01-23 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_auto_20220123_1007"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="color",
            field=models.CharField(
                choices=[
                    ("#0000FF", "Синий"),
                    ("#FFA500", "Оранжевый"),
                    ("#008000", "Зеленый"),
                    ("#800080", "Фиолетовый"),
                    ("#FFFF00", "Желтый"),
                ],
                max_length=50,
                unique=True,
                verbose_name="HEX Color",
            ),
        ),
    ]
