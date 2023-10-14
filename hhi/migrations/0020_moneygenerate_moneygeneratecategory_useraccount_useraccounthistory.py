# Generated by Django 3.2.9 on 2022-08-12 10:04

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hhi', '0019_ads_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccountHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=6)),
                ('order_number', models.CharField(max_length=25, null=True)),
                ('info', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('credit', 'credit'), ('debit', 'debit')], default='debit', max_length=25)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hhi_user_account_history', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hhi_user_account', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MoneyGenerateCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('required_product', models.IntegerField(default=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hhi_required_product_count_cat', to='hhi.tagname')),
            ],
        ),
        migrations.CreateModel(
            name='MoneyGenerate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('day1_status', models.BooleanField(default=False)),
                ('day1_status_completed', models.DateTimeField(null=True)),
                ('day2_status', models.BooleanField(default=False)),
                ('day2_status_completed', models.DateTimeField(null=True)),
                ('day3_status', models.BooleanField(default=False)),
                ('day3_status_completed', models.DateTimeField(null=True)),
                ('day4_status', models.BooleanField(default=False)),
                ('day4_status_completed', models.DateTimeField(null=True)),
                ('day5_status', models.BooleanField(default=False)),
                ('day5_status_completed', models.DateTimeField(null=True)),
                ('success_bill_no', models.IntegerField(default=0)),
                ('success_bill_lists', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), default=list, null=True, size=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hhi_money_gen', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
