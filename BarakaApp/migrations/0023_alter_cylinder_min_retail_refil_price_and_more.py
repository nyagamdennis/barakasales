# Generated by Django 5.0.7 on 2025-01-14 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BarakaApp', '0022_remove_cylinder_retail_refil_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cylinder',
            name='min_retail_refil_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_retail_selling_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_wholesale_refil_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='cylinder',
            name='min_wholesale_selling_price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
