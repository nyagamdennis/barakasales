# Generated by Django 5.0.7 on 2025-04-10 21:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0065_cashhandout_cash_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashhandout',
            name='sales_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='BarakaApp.salesteam'),
        ),
    ]
