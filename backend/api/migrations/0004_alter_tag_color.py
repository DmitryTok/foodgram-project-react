# Generated by Django 3.2 on 2022-01-24 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0003_alter_tag_color"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="color",
            field=models.CharField(
                max_length=50, unique=True, verbose_name="HEX Color"
            ),
        ),
    ]
