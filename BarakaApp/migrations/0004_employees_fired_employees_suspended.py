# Generated by Django 5.0.7 on 2025-01-01 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0003_remove_customers_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='employees',
            name='fired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='employees',
            name='suspended',
            field=models.BooleanField(default=False),
        ),
    ]
