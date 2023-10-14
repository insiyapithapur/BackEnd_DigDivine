# Generated by Django 3.2.9 on 2023-02-21 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vestige', '0031_auto_20230130_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='coinsection',
            name='section_type',
            field=models.CharField(choices=[('video_ads', 'video_ads'), ('recommended_apps', 'recommended_apps')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='bvrequest',
            name='request_id',
            field=models.CharField(default='VHC8dabG', max_length=20),
        ),
        migrations.AlterField(
            model_name='presignup',
            name='signup_token',
            field=models.CharField(default='vBvSIIKwk9', editable=False, max_length=255, unique=True),
        ),
    ]
