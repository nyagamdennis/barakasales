# Generated by Django 5.0.7 on 2025-04-08 16:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0061_expenses_sales_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='BarakaApp.employees'),
        ),
    ]
