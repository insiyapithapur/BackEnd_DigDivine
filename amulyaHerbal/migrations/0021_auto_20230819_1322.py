# Generated by Django 3.2.9 on 2023-08-19 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amulyaHerbal', '0020_auto_20230819_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='amulyaherbaluser',
            name='first_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='amulyaherbaluser',
            name='last_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='Tw9azZbH', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='9SIkczVmUw', editable=False, max_length=255, unique=True),
        ),
    ]
