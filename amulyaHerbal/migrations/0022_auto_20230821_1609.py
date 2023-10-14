# Generated by Django 3.2.9 on 2023-08-21 10:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('amulyaHerbal', '0021_auto_20230819_1322'),
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicTimer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('post_click_wvdo_btn', models.DecimalField(decimal_places=2, max_digits=5)),
                ('pre_click_wvdo_btn', models.DecimalField(decimal_places=2, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='TQOGjNEY', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='AEfdqnMBd0', editable=False, max_length=255, unique=True),
        ),
    ]
