# Generated by Django 3.2.9 on 2023-10-19 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hhi', '0047_auto_20231019_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='g5hTC6IZ', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='XFaQfcNDRB', editable=False, max_length=255, unique=True),
        ),
    ]
