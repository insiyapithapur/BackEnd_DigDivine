# Generated by Django 3.2.9 on 2021-12-04 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0006_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='productQty',
            field=models.IntegerField(),
        ),
    ]
