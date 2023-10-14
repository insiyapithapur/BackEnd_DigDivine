# Generated by Django 3.2.9 on 2022-06-21 07:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0066_auto_20220603_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='CpaLeadUrl',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('cpalead_url', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
