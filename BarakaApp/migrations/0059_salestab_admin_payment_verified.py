# Generated by Django 5.0.7 on 2025-04-05 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0058_alter_salestab_cashamount_alter_salestab_mpesaamount'),
    ]

    operations = [
        migrations.AddField(
            model_name='salestab',
            name='admin_payment_verified',
            field=models.BooleanField(default=False),
        ),
    ]
