# Generated by Django 3.2.9 on 2022-03-27 07:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0056_usercoin'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoinSection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('section_name', models.CharField(max_length=255)),
                ('ads_id', models.CharField(max_length=255)),
                ('reward_point', models.IntegerField()),
                ('minmax_point', models.CharField(max_length=18)),
                ('image', models.ImageField(blank=True, null=True, upload_to='CoinSection')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='usercoin',
            name='coin',
            field=models.IntegerField(default=0),
        ),
    ]
