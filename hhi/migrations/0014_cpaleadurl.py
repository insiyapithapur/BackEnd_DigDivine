# Generated by Django 3.2.9 on 2022-06-21 06:16

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hhi', '0013_alter_sectiondata_title'),
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
