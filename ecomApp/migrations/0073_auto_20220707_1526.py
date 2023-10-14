# Generated by Django 3.2.9 on 2022-07-07 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0072_activation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activation',
            name='category',
        ),
        migrations.AddField(
            model_name='activation',
            name='day1_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activation',
            name='day2_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='activation',
            name='day3_status',
            field=models.BooleanField(default=False),
        ),
    ]
