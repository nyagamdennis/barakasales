# Generated by Django 5.0.7 on 2025-04-04 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0055_remove_salestab_mpesaamountone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salestab',
            name='cashAmount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='salestab',
            name='mpesaAmount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
