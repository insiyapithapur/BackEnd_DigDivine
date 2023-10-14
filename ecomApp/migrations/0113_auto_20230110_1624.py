# Generated by Django 3.2.9 on 2023-01-10 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0112_auto_20230110_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='KW43AGIC', max_length=20),
        ),
        migrations.AlterField(
            model_name='logdata',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='hTll9wkyAN', editable=False, max_length=255, unique=True),
        ),
    ]
