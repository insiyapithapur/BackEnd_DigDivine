# Generated by Django 3.2.9 on 2023-10-14 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0121_auto_20231014_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='ofDbxn4N', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='YHLN3IhK5M', editable=False, max_length=255, unique=True),
        ),
    ]
