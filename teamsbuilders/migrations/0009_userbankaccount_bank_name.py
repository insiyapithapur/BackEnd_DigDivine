# Generated by Django 3.2.9 on 2022-08-14 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamsbuilders', '0008_alter_userbankaccount_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbankaccount',
            name='bank_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
