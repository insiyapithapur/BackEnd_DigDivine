# Generated by Django 3.2.9 on 2023-10-19 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0137_auto_20231016_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='ygp8zVpx', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='KN1LCIo9Ef', editable=False, max_length=255, unique=True),
        ),
    ]
