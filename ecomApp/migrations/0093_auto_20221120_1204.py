# Generated by Django 3.2.9 on 2022-11-20 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0092_alter_userbvrequesthistory_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bvrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('paid', 'paid'), ('rejected', 'rejected')], max_length=30),
        ),
        migrations.AlterField(
            model_name='userbvrequesthistory',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('paid', 'paid'), ('rejected', 'rejected')], max_length=30),
        ),
    ]
