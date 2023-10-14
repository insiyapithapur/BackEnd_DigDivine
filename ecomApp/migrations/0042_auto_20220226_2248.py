# Generated by Django 3.2.9 on 2022-02-26 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomApp', '0041_alter_tagname_serial_no'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taghirarchy',
            options={'ordering': ('category__serial_no',)},
        ),
        migrations.AddField(
            model_name='videosections',
            name='thumbnail',
            field=models.URLField(blank=True, null=True),
        ),
    ]
