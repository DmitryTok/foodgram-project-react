# Generated by Django 3.2 on 2022-01-26 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0008_auto_20220126_0908'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.recipe', verbose_name='Rcipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Shoping cart',
                'verbose_name_plural': 'Shoping carts',
                'ordering': ('id',),
            },
        ),
        migrations.AddConstraint(
            model_name='shopingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_shoping_cart'),
        ),
    ]
