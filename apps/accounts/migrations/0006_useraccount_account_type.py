# Generated by Django 4.2.4 on 2023-08-09 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_useraccount_currency_usercard_daily_limit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='account_type',
            field=models.CharField(choices=[('SAVINGS', 'SAVINGS'), ('CURRENT', 'CURRENT'), ('BUSINESS', 'BUSINESS'), ('PREMIUM', 'PREMIUM')], default='SAVINGS', max_length=20),
        ),
    ]