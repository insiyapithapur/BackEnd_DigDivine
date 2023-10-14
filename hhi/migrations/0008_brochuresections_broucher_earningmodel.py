# Generated by Django 3.2.9 on 2022-06-04 04:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hhi', '0007_ads_adsensecount_offerreferbgimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrochureSections',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('brochure_name', models.CharField(max_length=255, null=True, unique=True)),
                ('brochure_image', models.ImageField(null=True, upload_to='BrochureSections')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EarningModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('earning_amount', models.CharField(max_length=255)),
                ('description_link', models.FileField(blank=True, null=True, upload_to='EarningModel')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Broucher',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('book_name', models.CharField(max_length=255, null=True)),
                ('book_pdf', models.FileField(blank=True, null=True, upload_to='Bookpdf')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('brochure', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='hhi.brochuresections')),
            ],
        ),
    ]
