# Generated by Django 5.0.7 on 2025-01-04 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0007_assignedcylindersrecipt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignedcylinders',
            name='complete_sale',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
