# Generated by Django 4.2.3 on 2023-08-11 07:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_alter_usercardhistory_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="credits",
            name="bank",
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
