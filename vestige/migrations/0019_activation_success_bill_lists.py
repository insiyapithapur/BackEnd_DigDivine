# Generated by Django 3.2.9 on 2022-07-12 02:35

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vestige', '0018_alter_producttagpivot_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='activation',
            name='success_bill_lists',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), default=list, null=True, size=None),
        ),
    ]
