# Generated by Django 5.0.7 on 2025-04-12 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0067_alter_cashhandout_cash_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='cylinder',
            name='empty_cylinder_price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
