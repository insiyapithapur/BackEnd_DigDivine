# Generated by Django 3.2.9 on 2021-12-05 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0008_auto_20211205_0911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='productQty',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='productQty',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='availability',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
