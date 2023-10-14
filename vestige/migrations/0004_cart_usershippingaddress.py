# Generated by Django 3.2.9 on 2022-04-27 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vestige', '0003_rename_vestigeuse_vestigeuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=10)),
                ('mobileNumber', models.CharField(max_length=15)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vestigeUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('savelater', models.BooleanField(default=False)),
                ('productQty', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vestige.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VestigeUsercart', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'unique_together': {('product', 'user')},
            },
        ),
    ]
